import asyncio
import json

from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime
from aiosqlite import IntegrityError

from database import DataBase
from parsers import Anilibria
from config import UPDATE_TIME


@dataclass
class HomeService:
    database: DataBase

    async def update_releases_if_needed(self):
        expires_in = await self.database.get_expires_in("main")
        current_time = round(datetime.now().timestamp())

        if expires_in is None or expires_in[0] <= current_time:
            if expires_in is None:
                await self.database.insert_expires_in("main", current_time + UPDATE_TIME)
            else:
                await self.database.update_expires_in(current_time + UPDATE_TIME, "main")

            await self.fetch_and_store_releases()

    async def fetch_and_store_releases(self):
        releases = await Anilibria.get_latest_releases(limit=10, include="alias")

        tasks = []

        for release in releases:
            alias = release["alias"]
            task = Anilibria.get_release_info(alias, exclude="torrents,members,sponsor")
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            uuid = str(uuid4())

            try:
                await self.database.insert_release(
                    id=uuid,
                    name=result["name"]["main"],
                    english_name=result["name"]["english"],
                    type=result["type"]["value"],
                    year=result["year"],
                    source="anilibria",
                    poster=f'https://anilibria.tv{result["poster"]["optimized"]["preview"]}',
                    alias=result["alias"],
                    description=result["description"],
                    age_rating=result["age_rating"]["label"],
                    genres=json.dumps([genre["name"] for genre in result["genres"]], ensure_ascii=False),
                    is_ongoing=result["is_ongoing"],
                    created_at=datetime.fromisoformat(result.get("created_at")).timestamp() if result.get("created_at") else None,
                    updated_at=datetime.fromisoformat(result.get("updated_at")).timestamp() if result.get("updated_at") else None,
                    fresh_at=datetime.fromisoformat(result.get("fresh_at")).timestamp() if result.get("fresh_at") else None,
                    total_episodes=len(release["episodes"]) if release.get("episodes") else None
                )
            except IntegrityError:
                try:
                    await self.database.update_release_updated_at(
                        datetime.fromisoformat(release.get("updated_at")).timestamp() if release.get("updated_at") else None,
                        result["alias"]
                    )
                    await self.database.update_release_fresh_at(
                        datetime.fromisoformat(result.get("fresh_at")).timestamp() if result.get("fresh_at") else None,
                        result["alias"]
                    )
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)

    async def get_context(self):
        return {
            "latest": await self.database.get_latest_releases(),
            "recently": await self.database.get_recently_releases(),
            "recently_episodes": await self.database.get_recently_episodes()
        }