from dataclasses import dataclass

from database import DataBase


@dataclass
class FavoritesService:
    database: DataBase

    async def get_context(self):
        favorites = await self.database.get_favorites()
        return {
            "favorites": favorites
        }