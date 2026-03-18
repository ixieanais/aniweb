import json

from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from database import DataBase
from parsers import Anilibria


@dataclass
class CatalogService:
    database: DataBase

    async def fetch_and_store_releases(self, page: int, genres: str, sorting: str, publish_state: str):
        result = await Anilibria.get_catalog_releases(page, genres=genres, sorting=sorting, publish_state=publish_state)

        self.releases = result["data"]
        self.meta = result["meta"]

        for release in self.releases:
            uuid = str(uuid4())

            try:
                await self.database.insert_release(
                    id=uuid,
                    name=release["name"]["main"],
                    english_name=release["name"]["english"],
                    type=release["type"]["value"],
                    year=release["year"],
                    source="anilibria",
                    poster=f'https://anilibria.tv{release["poster"]["optimized"]["preview"]}',
                    alias=release["alias"],
                    description=release["description"],
                    age_rating=release["age_rating"]["label"],
                    genres=json.dumps([genre["name"] for genre in release["genres"]], ensure_ascii=False),
                    is_ongoing=release["is_ongoing"],
                    created_at=datetime.fromisoformat(release.get("created_at")).timestamp() if release.get("created_at") else None,
                    updated_at=datetime.fromisoformat(release.get("updated_at")).timestamp() if release.get("updated_at") else None,
                    fresh_at=datetime.fromisoformat(release.get("fresh_at")).timestamp() if release.get("fresh_at") else None,
                    total_episodes=len(release["episodes"]) if release.get("episodes") else None
                )
            except IntegrityError:
                try:
                    await self.database.update_release_updated_at(
                        datetime.fromisoformat(release.get("updated_at")).timestamp() if release.get("updated_at") else None,
                        release["alias"]
                    )
                    await self.database.update_release_fresh_at(
                        datetime.fromisoformat(release.get("fresh_at")).timestamp() if release.get("fresh_at") else None,
                        release["alias"]
                    )
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)

    async def get_context(self):
        return {
            "releases": self.releases,
            "meta": self.meta["pagination"],
            "genres": await Anilibria.get_genres()
        }