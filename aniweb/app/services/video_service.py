from dataclasses import dataclass
from fastapi.exceptions import HTTPException

from database import DataBase


@dataclass
class VideoService:
    database: DataBase

    async def get_info(self, id: str):
        self.id = id
        self.episode_data = await self.database.get_episode_info(id)
        if self.episode_data is None:
            raise HTTPException(status_code=404)

        self.alias = await self.database.get_release_alias(self.episode_data["release_id"])

    async def get_context(self):
        return {
            "title": self.episode_data["anime_name"],
            "episode_name": self.episode_data["episode_name"] if self.episode_data["episode_name"] is not None else "",
            "order": self.episode_data["ordinal"],
            "alias": self.alias,
            "preview": self.episode_data.get("preview"),
            "id": self.id,
            "order_neighbors": await self.database.get_episode_order_neighbors(self.episode_data["ordinal"], self.episode_data["release_id"]),
            "urls": await self.database.get_episode_urls(self.id),
            "opening": self.episode_data["opening"],
            "ending": self.episode_data["ending"],
            "release_id": self.episode_data["release_id"],
            "view_time": await self.database.get_view_time(self.id),
            "is_viewed": await self.database.get_is_viewed(self.id)
        }