from dataclasses import dataclass

from database import DataBase


@dataclass
class HomeService:
    database: DataBase

    async def update_releases_if_needed(self, uid: str):
        self.uid = uid
        self.is_authorized = self.database.is_authorized(uid)

    async def get_context(self):
        return {
            "authorized": self.is_authorized
        }