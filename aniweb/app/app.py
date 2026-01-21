import uvicorn

from datetime import datetime
from database import DataBase
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager

import config
import schemas
from services import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    global database
    database = DataBase(config.DATABASE_PATH)
    await database.create_tables()

    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory=config.STATIC_PATH), name="static")
templates = Jinja2Templates(directory=config.TEMPLATES_PATH)


@app.get("/", response_class=HTMLResponse, tags=["Pages"])
async def home_page(request: Request):
    service = HomeService(database)
    await service.update_releases_if_needed()
    context = await service.get_context()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=context
    )

@app.get("/catalog", response_class=HTMLResponse, tags=["Pages"])
async def catalog_page(
    request: Request,
    page=1,
    genres="",
    sort="RATING_DESC",
    status=""
):
    # raise HTTPException(status_code=404, detail="page not found")
    service = CatalogService(database)
    await service.fetch_and_store_releases(page, genres, sort, status)
    context = await service.get_context()
    if context["meta"]["current_page"] == context["meta"]["total_pages"] + 1:
        raise HTTPException(status_code=404, detail="page not found")

    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context=context
    )

@app.get("/profile", response_class=HTMLResponse, tags=["Pages"])
async def profile_page(request: Request):
    context = {}

    return templates.TemplateResponse(
        request=request,
        name="not_found.html",
        context=context
    )

@app.get("/favorites", response_class=HTMLResponse, tags=["Pages"])
async def favorites_page(request: Request):
    service = FavoritesService(database)
    context = await service.get_context()

    return templates.TemplateResponse(
        request=request,
        name="favorites.html",
        context=context
    )

@app.get("/release/{alias}", response_class=HTMLResponse, tags=["Pages"])
async def release_page(request: Request, alias: str):
    service = ReleaseService(database)
    await service.update_release_if_needed(alias)
    context = await service.get_context()

    return templates.TemplateResponse(
        request=request,
        name="release.html",
        context=context
    )

@app.get("/video/{id}", response_class=HTMLResponse, tags=["Pages"])
async def video_page(reqeust: Request, id: str):
    service = VideoService(database)
    await service.get_info(id)
    context = await service.get_context()

    return templates.TemplateResponse(
        request=reqeust,
        name="video.html",
        context=context
    )

@app.post("/viewed")
async def add_viewed(data: schemas.ViewedRequest):
    try:
        await database.insert_viewed(
            data.episode_id,
            data.release_id,
            datetime.now().timestamp()
        )
        return {"status": "complete"}
    except Exception as e:
        print(e)
        return {"status": "incomplete"}

@app.post("/favorite")
async def add_favorites(data: schemas.FavoriteRequest):
    try:
        await database.insert_favorite(data.alias, datetime.now().timestamp())
        return {"status": "complete", "details": "starred"}
    except Exception as e:
        print(e)
        return {"status": "incomplete"}

@app.delete("/favorite")
async def delete_favorite(data: schemas.FavoriteRequest):
    try:
        await database.delete_favorite(data.alias)
        return {"status": "complete", "details": "unstarred"}
    except Exception as e:
        print(e)
        return {"status": "incomplete"}

@app.get("/search")
async def search_releases_and_store(query: str):
    service = SearchService(database)
    return await service.fetch_and_store_releases(query)

@app.post("/view_time/{eid}", tags=["View Time"])
async def create_view_time(eid: str, data: schemas.ViewTimeRequest):
    await database.save_view_time(eid, data.time, datetime.now().timestamp())
    return {"status": "created"}

@app.get("/view_time/{eid}", tags=["View Time"])
async def get_view_time(eid: str):
    return await database.get_view_time(eid)

@app.patch("/view_time/{eid}", tags=["View Time"])
async def update_view_time(eid: str, data: schemas.ViewTimeRequest):
    await database.update_view_time(eid, data.time, datetime.now().timestamp())
    return {"status": "changed", "details": {"time": data.time}}

@app.delete("/view_time/{eid}", tags=["View Time"])
async def delete_view_time(eid: str):
    await database.delete_view_time(eid)
    return {"status": "deleted"}

@app.exception_handler(404)
async def not_found_page(request: Request, exc: HTTPException):
    return templates.TemplateResponse(request=request, name="not_found.html")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=4242, reload=True)