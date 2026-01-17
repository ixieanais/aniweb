from pydantic import BaseModel


class WatchedRequest(BaseModel):
    episode_id: str
    release_id: str


class FavoriteRequest(BaseModel):
    alias: str