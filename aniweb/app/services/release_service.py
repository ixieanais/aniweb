import json

from dataclasses import dataclass
from datetime import datetime
from fastapi import HTTPException

from database import DataBase
from parsers import Anilibria
from config import UPDATE_TIME


@dataclass
class ReleaseService:
    database: DataBase

    async def update_release_if_needed(self, alias: str):
        self.alias = alias
        release_info = await self.database.get_release(alias)
        if release_info is None:
            raise HTTPException(status_code=404)

        self.release_id = release_info["id"]
        expires_in = await self.database.get_expires_in(self.release_id)
        current_time = round(datetime.now().timestamp())

        if expires_in is None or expires_in[0] <= current_time:
            if expires_in is None:
                await self.database.insert_expires_in(self.release_id, current_time + UPDATE_TIME)
            else:
                await self.database.update_expires_in(current_time + UPDATE_TIME, release_info["id"])

            await self.fetch_and_store_release(release_info["id"])

    async def fetch_and_store_release(self, release_id: str):
        release_data = await Anilibria.get_release_info(self.alias)

        await self.database.update_release(
            id=release_id,
            name=release_data["name"]["main"],
            english_name=release_data["name"]["english"],
            type=release_data["type"]["value"],
            year=release_data["year"],
            poster=f'https://anilibria.tv{release_data["poster"]["optimized"]["preview"]}',
            alias=release_data["alias"],
            description=release_data["description"],
            age_rating=release_data["age_rating"]["label"],
            genres=json.dumps([genre["name"] for genre in release_data["genres"]], ensure_ascii=False),
            is_ongoing=release_data["is_ongoing"],
            created_at=datetime.fromisoformat(release_data.get("created_at")).timestamp() if release_data.get("created_at") else None,
            updated_at=datetime.fromisoformat(release_data.get("updated_at")).timestamp() if release_data.get("updated_at") else None,
            fresh_at=datetime.fromisoformat(release_data.get("fresh_at")).timestamp() if release_data.get("fresh_at") else None,
            total_episodes=len(release_data["episodes"]) if release_data.get("episodes") else None
        )

        for episode in release_data["episodes"]:
            await self.database.insert_episode(
                id=episode["id"],
                anime_name=release_data["name"]["main"],
                episode_name=episode["name"],
                order=episode["ordinal"],
                opening=json.dumps(
                    {
                        "start": episode["opening"]["start"],
                        "end": episode["opening"]["stop"]
                    }
                ),
                ending=json.dumps(
                    {
                        "start": episode["ending"]["start"],
                        "end": episode["ending"]["stop"]
                    }
                ),
                duration=episode["duration"],
                preview=f'https://anilibria.tv{episode["preview"]["src"]}' if episode.get("preview").get("src") else None,
                url_1080=episode["hls_1080"],
                url_720=episode["hls_720"],
                url_480=episode["hls_480"],
                source="anilibria",
                release_id=self.release_id
            )

        await self.database.update_is_ongoing(release_data["is_ongoing"], self.release_id)

    async def get_context(self):
        release_data = await self.database.get_release(self.alias)
        return {
            "release_data": release_data,
            "episodes_data": await self.database.get_episodes_id(self.release_id),
            "viewed_data": await self.database.get_viewed_episodes(self.release_id),
            "genres": json.loads(release_data["genres"]),
            "is_favorite": await self.database.is_favorite(self.alias)
        }