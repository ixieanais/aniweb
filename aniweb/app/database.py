from functools import wraps
from typing import Any, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy_utils import create_database, database_exists

import config
from models import *


engine = create_async_engine(
    url=config.DATABASE_URL,
    echo=False,
)

if not database_exists(config.DATABASE_URL.replace("asyncpg", "psycopg")):
    create_database(config.DATABASE_URL.replace("asyncpg", "psycopg"))

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

session_factory = async_sessionmaker(engine)


class DataBase:
    def __init__(self):
        self.session: Optional[AsyncSession] = None

    @staticmethod
    def conn(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            async with AsyncSessionLocal() as session:
                self.session = session
                try:
                    result = await func(self, *args, **kwargs)
                    await session.commit()
                    return result
                except Exception as e:
                    await session.rollback()
                    raise e
                finally:
                    await session.close()
        return wrapper

    @conn
    async def create_tables(self):
        async with engine.connect() as conn:
            await conn.run_sync(Base.metadata.create_all)
            await conn.commit()

    @conn
    async def insert_release(
        self,
        id: str,
        name: str,
        english_name: Optional[str],
        type: str,
        year: int,
        source: str,
        poster: str,
        alias: str,
        description: str,
        age_rating: str,
        genres: str,
        is_ongoing: bool,
        created_at: Optional[float],
        updated_at: Optional[float],
        fresh_at: float,
        total_episodes: Optional[int]
    ):
        await self.session.execute(
            text("""
                INSERT INTO releases
                (id, name, english_name, type, year, source, poster, alias, description,
                 age_rating, genres, is_ongoing, created_at, updated_at, fresh_at, total_episodes)
                VALUES (:id, :name, :english_name, :type, :year, :source,
                        :poster, :alias, :description, :age_rating, :genres,
                        :is_ongoing, :created_at, :updated_at, :fresh_at, :total_episodes)
                ON CONFLICT DO NOTHING
            """),
            {
                "id": id,
                "name": name,
                "english_name": english_name,
                "type": type,
                "year": year,
                "source": source,
                "poster": poster,
                "alias": alias,
                "description": description,
                "age_rating": age_rating,
                "genres": genres,
                "is_ongoing": is_ongoing,
                "created_at": created_at,
                "updated_at": updated_at,
                "fresh_at": fresh_at,
                "total_episodes": total_episodes
            }
        )

    @conn
    async def insert_episode(
        self,
        id: str,
        anime_name: str,
        episode_name: str,
        order: int,
        opening: str,
        ending: str,
        duration: int,
        preview: str,
        url_1080: Optional[str],
        url_720: Optional[str],
        url_480: Optional[str],
        source: str,
        release_id: str,
    ):
        await self.session.execute(
            text("""
                INSERT INTO episodes
                (id, anime_name, episode_name, ordinal, opening, ending, duration, preview,
                 url_1080, url_720, url_480, source, release_id)
                VALUES (:id, :anime_name, :episode_name, :ordinal, :opening, :ending, :duration,
                        :preview, :url_1080, :url_720, :url_480, :source, :release_id)
                ON CONFLICT (release_id, ordinal) DO NOTHING
            """),
            {
                "id": id,
                "anime_name": anime_name,
                "episode_name": episode_name,
                "ordinal": order,
                "opening": opening,
                "ending": ending,
                "duration": duration,
                "preview": preview,
                "url_1080": url_1080,
                "url_720": url_720,
                "url_480": url_480,
                "source": source,
                "release_id": release_id
            }
        )

    @conn
    async def update_release_updated_at(
        self,
        updated_at: float,
        alias: str
    ):
        await self.session.execute(
            text("UPDATE releases SET updated_at = :updated_at WHERE alias = :alias"),
            {"updated_at": updated_at, "alias": alias}
        )

    @conn
    async def update_release_fresh_at(
        self,
        fresh_at: float,
        alias: str
    ):
        await self.session.execute(
            text("UPDATE releases SET fresh_at = :fresh_at WHERE alias = :alias"),
            {"fresh_at": fresh_at, "alias": alias}
        )

    @conn
    async def update_release(
        self,
        id: str,
        name: str,
        english_name: Optional[str],
        type: str,
        year: int,
        poster: str,
        alias: str,
        description: str,
        age_rating: str,
        genres: str,
        is_ongoing: bool,
        created_at: Optional[float],
        updated_at: Optional[float],
        fresh_at: float,
        total_episodes: Optional[int]
    ):
        await self.session.execute(
            text("""
                UPDATE releases SET
                    name = :name,
                    english_name = :english_name,
                    type = :type,
                    year = :year,
                    poster = :poster,
                    alias = :alias,
                    description = :description,
                    age_rating = :age_rating,
                    genres = :genres,
                    is_ongoing = :is_ongoing,
                    created_at = :created_at,
                    updated_at = :updated_at,
                    fresh_at = :fresh_at,
                    total_episodes = :total_episodes
                WHERE id = :id
            """),
            {
                "id": id,
                "name": name,
                "english_name": english_name,
                "type": type,
                "year": year,
                "poster": poster,
                "alias": alias,
                "description": description,
                "age_rating": age_rating,
                "genres": genres,
                "is_ongoing": is_ongoing,
                "created_at": created_at,
                "updated_at": updated_at,
                "fresh_at": fresh_at,
                "total_episodes": total_episodes
            }
        )

    @conn
    async def get_latest_releases(self) -> list[Any]:
        result = await self.session.execute(
            text("SELECT * FROM releases WHERE fresh_at IS NOT NULL ORDER BY fresh_at DESC LIMIT 10")
        )
        rows = result.all()
        return [dict(row._asdict()) for row in rows]

    @conn
    async def get_release(self, alias: str) -> Optional[dict]:
        result = await self.session.execute(
            text("SELECT * FROM releases WHERE alias = :alias"),
            {"alias": alias}
        )
        row = result.mappings().first()
        return dict(row) if row else None

    @conn
    async def get_episodes_id(self, release_id: str) -> list[dict]:
        result = await self.session.execute(
            text("SELECT id, ordinal FROM episodes WHERE release_id = :release_id ORDER BY ordinal ASC"),
            {"release_id": release_id}
        )
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    @conn
    async def get_episode_urls(self, id: str) -> dict:
        sources = {}

        result = await self.session.execute(
            text("SELECT url_1080, url_720, url_480 FROM episodes WHERE id = :id"),
            {"id": id}
        )
        row = result.first()

        if row:
            if row[0]: sources[1080] = row[0]
            if row[1]: sources[720] = row[1]
            if row[2]: sources[480] = row[2]

        return sources

    @conn
    async def get_episode_order_neighbors(self, order: int, release_id: int):
        result = {}

        prev_result = await self.session.execute(
            text("SELECT id, ordinal FROM episodes WHERE ordinal = :ordinal AND release_id = :release_id"),
            {"ordinal": order - 1, "release_id": release_id}
        )
        prev_value = prev_result.mappings().first()
        result["prev"] = dict(prev_value) if prev_value else None

        next_result = await self.session.execute(
            text("SELECT id, ordinal FROM episodes WHERE ordinal = :ordinal AND release_id = :release_id"),
            {"ordinal": order + 1, "release_id": release_id}
        )
        next_value = next_result.mappings().first()
        result["next"] = dict(next_value) if next_value else None

        return result

    @conn
    async def get_episode_info(self, id: str) -> Optional[dict]:
        result = await self.session.execute(
            text("SELECT * FROM episodes WHERE id = :id"),
            {"id": id}
        )
        row = result.mappings().first()
        return dict(row) if row else None

    @conn
    async def get_release_alias(self, id: str) -> Optional[str]:
        result = await self.session.execute(
            text("SELECT alias FROM releases WHERE id = :id"),
            {"id": id}
        )
        row = result.first()
        return row[0] if row else None

    async def _get_release_id(self, alias: str) -> Optional[str]:
        result = await self.session.execute(
            text("SELECT id FROM releases WHERE alias = :alias"),
            {"alias": alias}
        )
        row = result.first()
        return row[0] if row else None

    @conn
    async def get_viewed_episodes(self, release_id: str, uid: str):
        result = await self.session.execute(
            text("SELECT episode_id FROM viewed WHERE release_id = :release_id AND uid = :uid"),
            {"release_id": release_id, "uid": uid}
        )
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    @conn
    async def update_is_ongoing(self, is_ongoing: bool, alias: str):
        await self.session.execute(
            text("UPDATE releases SET is_ongoing = :is_ongoing WHERE alias = :alias"),
            {"is_ongoing": is_ongoing, "alias": alias}
        )

    @conn
    async def insert_expires_in(self, id: str, expires_in: int):
        await self.session.execute(
            text("INSERT INTO expires_in (id, expires_in) VALUES (:id, :expires_in)"),
            {"id": id, "expires_in": expires_in}
        )

    @conn
    async def update_expires_in(self, expires_in: int, id: str):
        await self.session.execute(
            text("UPDATE expires_in SET expires_in = :expires_in WHERE id = :id"),
            {"expires_in": expires_in, "id": id}
        )

    @conn
    async def update_total_episodes(self, release_id: str, total_episodes: int):
        await self.session.execute(
            text("UPDATE releases SET total_episodes = :total_episodes WHERE id = :release_id"),
            {"total_episodes": total_episodes, "release_id": release_id}
        )

    @conn
    async def get_expires_in(self, id: str):
        result = await self.session.execute(
            text("SELECT expires_in FROM expires_in WHERE id = :id"),
            {"id": id}
        )
        return result.first()

    @conn
    async def insert_viewed(self, uid: str, episode_id: str, release_id: str, added_at: float):
        await self.session.execute(
            text("""
                INSERT INTO viewed (uid, episode_id, release_id, added_at)
                VALUES (:uid, :episode_id, :release_id, :added_at)
                ON CONFLICT (uid, episode_id) DO NOTHING
            """),
            {"uid": uid, "episode_id": episode_id, "release_id": release_id, "added_at": added_at}
        )

    @conn
    async def get_is_viewed(self, uid: str, episode_id: str) -> bool:
        result = await self.session.execute(
            text("SELECT 1 FROM viewed WHERE episode_id = :episode_id AND uid = :uid"),
            {"episode_id": episode_id, "uid": uid}
        )
        row = result.first()
        return bool(row)

    @conn
    async def insert_favorite(self, uid: str, alias: str, added_at: float):
        release_id = await self._get_release_id(alias)
        await self.session.execute(
            text("INSERT INTO favorites (uid, release_id, added_at) VALUES (:uid, :release_id, :added_at)"),
            {"uid": uid, "release_id": release_id, "added_at": added_at}
        )

    @conn
    async def is_favorite(self, uid: str, alias: str) -> bool:
        release_id = await self._get_release_id(alias)
        result = await self.session.execute(
            text("SELECT 1 FROM favorites WHERE release_id = :release_id AND uid = :uid"),
            {"release_id": release_id, "uid": uid}
        )
        row = result.first()
        return bool(row)

    @conn
    async def get_favorites(self, uid: str):
        result = await self.session.execute(
            text("""
                SELECT r.name, r.type, r.year, r.poster, r.alias, r.age_rating
                FROM releases AS r
                INNER JOIN favorites AS f ON r.id = f.release_id
                WHERE f.uid = :uid
                ORDER BY f.added_at DESC
            """),
            {"uid": uid}
        )
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    @conn
    async def delete_favorite(self, uid: str, alias: str):
        release_id = await self._get_release_id(alias)
        await self.session.execute(
            text("DELETE FROM favorites WHERE release_id = :release_id AND uid = :uid"),
            {"release_id": release_id, "uid": uid}
        )

    @conn
    async def get_recently_releases(self, uid: str):
        result = await self.session.execute(
            text("""
                SELECT r.name, r.type, r.year, r.poster, r.alias, r.age_rating
                FROM releases AS r
                INNER JOIN view_time AS v ON r.id = v.release_id
                WHERE v.uid = :uid
                ORDER BY v.updated_at DESC
            """),
            {"uid": uid}
        )
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    @conn
    async def get_recently_episodes(self, uid: str):
        result = await self.session.execute(
            text("""
                SELECT e.id, e.ordinal
                FROM episodes AS e
                INNER JOIN view_time AS v ON e.id = v.episode_id
                WHERE v.uid = :uid
                ORDER BY v.updated_at DESC
            """),
            {"uid": uid}
        )
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    @conn
    async def save_view_time(self, uid: str, episode_id: str, time: int, updated_at: float):
        result = await self.session.execute(
            text("SELECT release_id FROM episodes WHERE id = :episode_id"),
            {"episode_id": episode_id}
        )
        row = result.first()
        release_id = row[0] if row else None

        await self.session.execute(
            text("""
                INSERT INTO view_time (uid, episode_id, release_id, time, updated_at)
                VALUES (:uid, :episode_id, :release_id, :time, :updated_at)
                ON CONFLICT (uid, release_id) DO UPDATE SET
                    episode_id = EXCLUDED.episode_id,
                    time = EXCLUDED.time,
                    updated_at = EXCLUDED.updated_at
            """),
            {"uid": uid, "episode_id": episode_id, "release_id": release_id, "time": time, "updated_at": updated_at}
        )

    @conn
    async def get_view_time(self, uid: str, episode_id: str) -> Optional[int]:
        result = await self.session.execute(
            text("SELECT time FROM view_time WHERE episode_id = :episode_id AND uid = :uid"),
            {"episode_id": episode_id, "uid": uid}
        )
        row = result.first()
        return row[0] if row else None

    @conn
    async def update_view_time(self, uid: str, release_id: str, episode_id: str, time: int, updated_at: float):
        await self.session.execute(
            text("""
                UPDATE view_time SET
                    episode_id = :episode_id,
                    time = :time,
                    updated_at = :updated_at
                WHERE release_id = :release_id AND uid = :uid
            """),
            {"episode_id": episode_id, "time": time, "updated_at": updated_at, "release_id": release_id, "uid": uid}
        )

    @conn
    async def delete_view_time(self, uid: str, episode_id: str):
        await self.session.execute(
            text("DELETE FROM view_time WHERE episode_id = :episode_id AND uid = :uid"),
            {"episode_id": episode_id, "uid": uid}
        )

    @conn
    async def get_count_favorites(self, uid: str) -> int:
        result = await self.session.execute(
            text("SELECT COUNT(*) FROM favorites WHERE uid = :uid"),
            {"uid": uid}
        )
        row = result.first()
        return row[0] if row else 0

    @conn
    async def get_count_viewed(self, uid: str) -> int:
        result = await self.session.execute(
            text("SELECT COUNT(*) FROM viewed WHERE uid = :uid"),
            {"uid": uid}
        )
        row = result.first()
        return row[0] if row else 0

    @conn
    async def save_user(
        self,
        uid: str,
        username: str,
        email: str,
        password: str,
        connected_at: int,
        last_visit_at: int
    ):
        password_bytes = password.encode('utf-8') if isinstance(password, str) else password

        await self.session.execute(
            text("""
                INSERT INTO users (uid, username, email, password, connected_at, last_visit_at)
                VALUES (:uid, :username, :email, :password, :connected_at, :last_visit_at)
            """),
            {
                "uid": uid,
                "username": username,
                "email": email,
                "password": password_bytes,
                "connected_at": connected_at,
                "last_visit_at": last_visit_at
            }
        )

    @conn
    async def user_exists(self, email: str) -> bool:
        result = await self.session.execute(
            text("SELECT 1 FROM users WHERE email = :email"),
            {"email": email}
        )
        row = result.first()
        return bool(row)

    @conn
    async def is_authorized(self, uid: Optional[str]) -> bool:
        if uid is None:
            return False

        result = await self.session.execute(
            text("SELECT 1 FROM users WHERE uid = :uid"),
            {"uid": uid}
        )
        row = result.first()
        return bool(row)

    @conn
    async def get_user_info(self, email: str):
        result = await self.session.execute(
            text("SELECT uid, password FROM users WHERE email = :email"),
            {"email": email}
        )
        row = result.mappings().first()
        return dict(row) if row else None

    @conn
    async def delete_user(self, uid: str):
        await self.session.execute(
            text("DELETE FROM users WHERE uid = :uid"),
            {"uid": uid}
        )