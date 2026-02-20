from dataclasses import dataclass

from database import DataBase


@dataclass
class FavoritesService:
    database: DataBase

    async def get_context(self, uid: str):
        return {
            "favorites": await self.database.get_favorites(uid)
        }