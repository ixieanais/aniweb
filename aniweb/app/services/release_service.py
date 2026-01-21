import json

from dataclasses import dataclass
from datetime import datetime

from database import DataBase
from parsers import Anilibria
from config import UPDATE_TIME


@dataclass
class ReleaseService:
    database: DataBase

    async def update_release_if_needed(self, alias: str):
        self.alias = alias
        release_info = await self.database.get_release(alias)
        self.release_id = release_info["id"]
        expires_in = await self.database.get_expires_in(self.release_id)
        current_time = round(datetime.now().timestamp())

        if expires_in is None or expires_in[0] <= current_time:
            if expires_in is None:
                await self.database.insert_expires_in(self.release_id, current_time + UPDATE_TIME)
            else:
                await self.database.update_expires_in(current_time + UPDATE_TIME, release_info["id"])

            await self.fetch_and_store_release()

    async def fetch_and_store_release(self):
        release_data = await Anilibria.get_release_info(self.alias)

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