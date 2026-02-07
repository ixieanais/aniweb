from pydantic import BaseModel


class ViewedRequest(BaseModel):
    episode_id: str
    release_id: str


class FavoriteRequest(BaseModel):
    alias: str


class ViewTimeRequest(BaseModel):
    time: int