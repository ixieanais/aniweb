import aiosqlite

from functools import wraps
from typing import Any, Optional


class DataBase:
    def __init__(self, path: str, /):
        self.path = path

    def tip(self):
        self.database: aiosqlite.Connection
        self.cursor: aiosqlite.Cursor

    @staticmethod
    def conn(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            async with aiosqlite.connect(self.path) as database:
                self.database = database
                self.cursor = await database.cursor()
                try:
                    return await func(self, *args, **kwargs)
                finally:
                    await self.cursor.close()
        return wrapper

    @conn
    async def create_tables(self):
        await self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodes (
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                anime_name VARCHAR(255),
                episode_name VARCHAR(255),
                ordinal INTEGER,
                opening VARCHAR(255),
                ending VARCHAR(255),
                duration INTEGER,
                preview VARCHAR(255),
                url_1080 VARCHAR(255),
                url_720 VARCHAR(255),
                url_480 VARCHAR(255),
                source VARCHAR(20),
                release_id VARCHAR(36),
                UNIQUE(anime_name, ordinal),
                FOREIGN KEY(release_id) REFERENCES releases(id)
            )
        """)
        await self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS releases (
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                name VARCHAR(255),
                english_name VARCHAR(255),
                type VARCHAR(15),
                year INTEGER,
                source VARCHAR(20),
                poster VARCHAR(255),
                alias VARCHAR(255),
                description TEXT,
                age_rating VARCHAR(3),
                genres TEXT,
                is_ongoing INTEGER,
                created_at INTEGER,
                updated_at INTEGER,
                fresh_at INTEGER,
                total_episodes INTEGER,
                UNIQUE(name)
            )
        """)
        await self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                release_id VARCHAR(36),
                added_at INTEGER,
                FOREIGN KEY(release_id) REFERENCES releases(id),
                UNIQUE(release_id)
            )
        """)
        await self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS stars (
                release_id VARCHAR(36),
                quanity INTEGER,
                added_at INTEGER,
                FOREIGN KEY(release_id) REFERENCES releases(id),
                UNIQUE(release_id)
            )
        """)
        await self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS viewed (
                episode_id VARCHAR(36),
                release_id VARCHAR(36),
                added_at INTEGER,
                FOREIGN KEY(episode_id) REFERENCES episodes(id),
                FOREIGN KEY(release_id) REFERENCES releases(id),
                UNIQUE(episode_id)
            )
        """)
        await self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS expires_in (
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                expires_in INTEGER,
                UNIQUE(id)
            )
        """)
        await self.database.commit()

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
        await self.cursor.execute(
            "INSERT INTO releases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (id, name, english_name, type, year, source, poster, alias, description, age_rating, genres, is_ongoing, created_at, updated_at, fresh_at, total_episodes)
        )
        await self.database.commit()

    @conn
    async def insert_episode(
        self,
        id: str, # UUID
        anime_name: str,
        episode_name: str,
        order: int,
        opening: str,
        ending: str,
        duration: int,
        preview: str, # URL
        url_1080: Optional[str],
        url_720: Optional[str],
        url_480: Optional[str],
        source: str,
        release_id: str,
    ):
        await self.cursor.execute(
            "INSERT OR IGNORE INTO episodes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (id, anime_name, episode_name, order, opening, ending, duration, preview, url_1080, url_720, url_480, source, release_id)
        )
        await self.database.commit()

    @conn
    async def update_release_updated_at(
        self,
        updated_at: float,
        alias: str
    ):
        await self.cursor.execute("UPDATE releases SET updated_at = ? WHERE alias = ?", (updated_at, alias))
        await self.database.commit()

    @conn
    async def update_release_fresh_at(
        self,
        fresh_at: float,
        alias: str
    ):
        await self.cursor.execute("UPDATE releases SET fresh_at = ? WHERE alias = ?", (fresh_at, alias))
        await self.database.commit()

    @conn
    async def get_latest_releases(self) -> list[Any]:
        self.cursor.row_factory = aiosqlite.Row
        cursor = await self.cursor.execute("SELECT * FROM releases ORDER BY fresh_at DESC LIMIT 10")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    @conn
    async def get_release(self, alias: str) -> dict:
        self.cursor.row_factory = aiosqlite.Row
        cursor = await self.cursor.execute("SELECT * FROM releases WHERE alias = ?", (alias,))
        row = await cursor.fetchone()
        return dict(row)

    @conn
    async def get_episodes_id(self, release_id: str) -> list[dict]:
        self.cursor.row_factory = aiosqlite.Row
        cursor = await self.cursor.execute("SELECT id, ordinal FROM episodes WHERE release_id = ? ORDER BY ordinal ASC", (release_id,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    @conn
    async def get_episode_urls(self, id: str) -> dict:
        resolutions = [1080, 720, 480]
        sources = {}

        for resolution in resolutions:
            cursor = await self.cursor.execute(f"SELECT url_{resolution} FROM episodes WHERE id = ?", (id,))
            result = await cursor.fetchone()
            if result is not None:
                sources[resolution] = result[0]

        return sources

    @conn
    async def get_episode_order_neighbors(self, order: int, release_id: int):
        self.cursor.row_factory = aiosqlite.Row
        prev_cursor = await self.cursor.execute(
            "SELECT id, ordinal FROM episodes WHERE ordinal = ? AND release_id = ?",
            (order - 1, release_id)
        )
        prev_value = await prev_cursor.fetchone()

        next_cursor = await self.cursor.execute(
            "SELECT id, ordinal FROM episodes WHERE ordinal = ? AND release_id = ?",
            (order + 1, release_id)
        )
        next_value = await next_cursor.fetchone()

        return {
            "prev": dict(prev_value) if prev_value else None,
            "next": dict(next_value) if next_value else None
        }

    @conn
    async def get_episode_info(self, id: str) -> Optional[dict]:
        self.cursor.row_factory = aiosqlite.Row
        cursor = await self.cursor.execute("SELECT * FROM episodes WHERE id = ?", (id,))
        row = await cursor.fetchone()
        return dict(row) if row else None

    @conn
    async def get_release_alias(self, id: str) -> Optional[str]:
        cursor = await self.cursor.execute("SELECT alias FROM releases WHERE id = ?", (id,))
        row = await cursor.fetchone()
        return row[0] if row else None

    async def _get_release_id(self, alias: str) -> Optional[str]:
        cursor = await self.cursor.execute("SELECT id FROM releases WHERE alias = ?", (alias,))
        row = await cursor.fetchone()
        return row[0] if row else None

    @conn
    async def get_viewed_episodes(self, release_id: str):
        self.cursor.row_factory = aiosqlite.Row
        cursor = await self.cursor.execute("SELECT episode_id FROM viewed WHERE release_id = ?", (release_id,))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    @conn
    async def update_is_ongoing(self, is_ongoing: bool, alias: str):
        await self.cursor.execute("UPDATE releases SET is_ongoing = ? WHERE alias = ?", (is_ongoing, alias))
        await self.database.commit()

    @conn
    async def insert_expires_in(self, id: str, expires_in: int):
        await self.cursor.execute("INSERT INTO expires_in VALUES (? ,?)", (id, expires_in))
        await self.database.commit()

    @conn
    async def update_expires_in(self, expires_in: int, id: str):
        await self.cursor.execute("UPDATE expires_in SET expires_in = ? WHERE id = ?", (expires_in, id))
        await self.database.commit()

    @conn
    async def update_total_episodes(self, release_id: str, total_episodes: int):
        await self.cursor.execute("UPDATE releases SET total_episodes = ? WHERE release_id = ?", (total_episodes, release_id))

    @conn
    async def get_expires_in(self, id: str):
        cursor = await self.cursor.execute("SELECT expires_in FROM expires_in WHERE id = ?", (id,))
        return await cursor.fetchone()

    @conn
    async def insert_viewed(self, episode_id: str, release_id: str, added_at: float):
        await self.cursor.execute("INSERT OR IGNORE INTO viewed VALUES (?, ?, ?)", (episode_id, release_id, added_at))
        await self.database.commit()

    @conn
    async def insert_favorite(self, alias: str, added_at: float):
        release_id = await self._get_release_id(alias)
        await self.cursor.execute("INSERT INTO favorites VALUES (?, ?)", (release_id, added_at))
        await self.database.commit()

    @conn
    async def is_favorite(self, alias: str) -> bool:
        release_id = await self._get_release_id(alias)
        cursor = await self.cursor.execute("SELECT rowid FROM favorites WHERE release_id = ?", (release_id,))
        result = await cursor.fetchone()
        return True if result else False

    @conn
    async def get_favorites(self):
        self.cursor.row_factory = aiosqlite.Row
        cursor = await self.cursor.execute("""
            SELECT r.name, r.type, r.year, r.poster, r.alias, r.age_rating
            FROM releases AS r
            INNER JOIN favorites AS f
            ON r.id = f.release_id
            ORDER BY f.added_at DESC
        """)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    @conn
    async def delete_favorite(self, alias: str):
        release_id = await self._get_release_id(alias)
        await self.cursor.execute("DELETE FROM favorites WHERE release_id = ?", (release_id,))
        await self.database.commit()