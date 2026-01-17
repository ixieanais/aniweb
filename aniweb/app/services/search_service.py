import json

from dataclasses import dataclass
from uuid import uuid4
from datetime import datetime
from aiosqlite import IntegrityError

from database import DataBase
from parsers import Anilibria


@dataclass
class SearchService:
    database: DataBase

    async def fetch_and_store_releases(self, query: str):
        result = await Anilibria.get_search_result(query)

        for release in result["data"]:
            uuid = str(uuid4())

            try:
                await self.database.insert_release(
                    id=uuid,
                    name=release["name"]["main"],
                    english_name=release["name"]["english"],
                    type=release["type"]["value"],
                    year=release["year"],
                    source="anilibria",
                    poster=f'https://anilibria.tv{release["poster"]["src"]}',
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

        return result