import uvicorn

from datetime import datetime
from database import DataBase
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError
from fastapi.responses import HTMLResponse, Response, RedirectResponse
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from uuid import uuid4
from contextlib import asynccontextmanager

import config
import schemas
from services import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    global database
    database = DataBase()
    await database.create_tables()

    yield


app = FastAPI(lifespan=lifespan, docs_url=None)
app.mount("/static", StaticFiles(directory=config.STATIC_PATH), name="static")
templates = Jinja2Templates(directory=config.TEMPLATES_PATH)


async def is_authorized(request: Request) -> bool:
    return await database.is_authorized(request.cookies.get(config.SESSION_NAME))


@app.get("/", response_class=HTMLResponse, tags=["Pages"])
async def home_page(request: Request, authorized: bool = Depends(is_authorized)):
    service = HomeService(database)
    await service.update_releases_if_needed(request.cookies.get(config.SESSION_NAME))
    context = await service.get_context()
    context["authorized"] = authorized

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
    status="",
    authorized: bool = Depends(is_authorized)
):
    service = CatalogService(database)
    await service.fetch_and_store_releases(page, genres, sort, status)
    context = await service.get_context()
    context["authorized"] = authorized
    if context["meta"]["current_page"] == context["meta"]["total_pages"] + 1:
        raise HTTPException(status_code=404, detail="page not found")

    return templates.TemplateResponse(
        request=request,
        name="catalog.html",
        context=context
    )

@app.get("/signup", response_class=HTMLResponse, tags=["Pages"])
async def register_page(request: Request, authorized: bool = Depends(is_authorized)):
    if authorized:
        return RedirectResponse("/")

    return templates.TemplateResponse(
        request=request,
        name="signup.html"
    )

@app.post("/signup")
async def signup(response: Response, creds: schemas.UserLoginSchema):
    if await database.user_exists(creds.email):
        raise HTTPException(status_code=401)

    uid = str(uuid4())
    response.set_cookie(config.SESSION_NAME, uid, max_age=config.SESSION_MAX_AGE)

    ph = PasswordHasher()
    hashed_password = ph.hash(creds.password)

    await database.save_user(
        uid=uid,
        username=creds.email,
        email=creds.email,
        password=hashed_password,
        connected_at=datetime.now().timestamp(),
        last_visit_at=datetime.now().timestamp()
    )

@app.get("/login", response_class=HTMLResponse, tags=["Pages"])
async def login_page(request: Request, authorized: bool = Depends(is_authorized)):
    if authorized:
        return RedirectResponse("/")

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )

@app.post("/login")
async def login(response: Response, creds: schemas.UserLoginSchema):
    if not await database.user_exists(creds.email):
        raise HTTPException(status_code=401, detail="Неверное имя или пароль")

    user_info = await database.get_user_info(creds.email)
    ph = PasswordHasher()
    try:
        ph.verify(user_info["password"], creds.password)
    except InvalidHashError:
        raise HTTPException(status_code=401, detail="Неверный пароль")

    response.set_cookie(config.SESSION_NAME, user_info["uid"], max_age=config.SESSION_MAX_AGE)
    return {config.SESSION_NAME: user_info["uid"]}

@app.get("/favorites", response_class=HTMLResponse, tags=["Pages"])
async def favorites_page(request: Request, authorized: bool = Depends(is_authorized)):
    if not authorized:
        return RedirectResponse("/")

    service = FavoritesService(database)
    context = await service.get_context(request.cookies.get(config.SESSION_NAME))
    context["authorized"] = authorized

    return templates.TemplateResponse(
        request=request,
        name="favorites.html",
        context=context
    )

@app.get("/release/{alias}", response_class=HTMLResponse, tags=["Pages"])
async def release_page(request: Request, alias: str, authorized: bool = Depends(is_authorized)):
    service = ReleaseService(database)
    await service.update_release_if_needed(alias, request.cookies.get(config.SESSION_NAME))
    context = await service.get_context()
    context["authorized"] = authorized

    return templates.TemplateResponse(
        request=request,
        name="release.html",
        context=context
    )

async def forbidden_page():
    raise HTTPException(status_code=403)

@app.get("/video/{id}", response_class=HTMLResponse, tags=["Pages"])
async def video_page(request: Request, id: str, authorized: bool = Depends(is_authorized)):
    service = VideoService(database)
    await service.get_info(id, request.cookies.get(config.SESSION_NAME))
    context = await service.get_context()
    context["authorized"] = authorized

    return templates.TemplateResponse(
        request=request,
        name="video.html",
        context=context
    )

@app.post("/viewed")
async def add_viewed(request: Request, data: schemas.ViewedRequest):
    try:
        await database.insert_viewed(
            request.cookies.get(config.SESSION_NAME),
            data.episode_id,
            data.release_id,
            datetime.now().timestamp()
        )
        return {"status": "complete"}
    except Exception as e:
        print(e)
        return {"status": "incomplete"}

@app.post("/favorite")
async def add_favorites(request: Request, data: schemas.FavoriteRequest):
    try:
        await database.insert_favorite(request.cookies.get(config.SESSION_NAME), data.alias, datetime.now().timestamp())
        return {"status": "complete", "details": "starred"}
    except IntegrityError:
        raise HTTPException(status_code=401)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401)

@app.delete("/favorite")
async def delete_favorite(request: Request, data: schemas.FavoriteRequest):
    try:
        await database.delete_favorite(request.cookies.get(config.SESSION_NAME), data.alias)
        return {"status": "complete", "details": "unstarred"}
    except Exception as e:
        print(e)
        return {"status": "incomplete"}

@app.get("/search")
async def search_releases_and_store(query: str):
    service = SearchService(database)
    return await service.fetch_and_store_releases(query)

@app.post("/view_time/{eid}", tags=["View Time"])
async def create_view_time(request: Request, eid: str, data: schemas.ViewTimeRequest):
    await database.save_view_time(request.cookies.get(config.SESSION_NAME), eid, data.time, datetime.now().timestamp())
    return {"status": "created"}

@app.get("/view_time/{eid}", tags=["View Time"])
async def get_view_time(request: Request, eid: str):
    return await database.get_view_time(request.cookies.get(config.SESSION_NAME), eid)

@app.patch("/view_time/{rid}/{eid}", tags=["View Time"])
async def update_view_time(request: Request, rid: str, eid: str, data: schemas.ViewTimeRequest):
    await database.update_view_time(request.cookies.get(config.SESSION_NAME), rid, eid, data.time, datetime.now().timestamp())
    return {"status": "changed", "details": {"time": data.time}}

@app.delete("/view_time/{eid}", tags=["View Time"])
async def delete_view_time(request: Request, eid: str):
    await database.delete_view_time(request.cookies.get(config.SESSION_NAME), eid)
    return {"status": "deleted"}

@app.get("/viewed_count", tags=["Profile"])
async def get_viewed_count(request: Request):
    return await database.get_count_viewed(request.cookies.get(config.SESSION_NAME))

@app.get("/favorites_count", tags=["Profile"])
async def get_favorites_count(request: Request):
    return await database.get_count_favorites(request.cookies.get(config.SESSION_NAME))

@app.exception_handler(404)
async def not_found_page(request: Request, exc: HTTPException):
    return templates.TemplateResponse(request=request, name="not_found.html")


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=4242, reload=True)