from aiohttp import ClientSession


class Anilibria:
    @staticmethod
    async def get_latest_releases(limit=10, include="", exclude="members,season,publish_day,genres.image") -> dict:
        async with ClientSession() as session:
            async with session.get(
                url="https://api.anilibria.app/api/v1/anime/releases/latest",
                params={
                    "limit": limit,
                    "include": include,
                    "exclude": exclude
                }
            ) as response:
                response.raise_for_status()
                return await response.json()

    @staticmethod
    async def get_catalog_releases(page=1, limit=12, genres="", sorting="", publish_state="", include="", exclude="season,publish_day,genres.image") -> dict:
        async with ClientSession() as session:
            async with session.get(
                url="https://api.anilibria.app/api/v1/anime/catalog/releases",
                params={
                    "page": page,
                    "limit": limit,
                    "f[genres]": genres,
                    "f[sorting]": sorting,
                    "f[publish_statuses]": publish_state,
                    "include": include,
                    "exclude": exclude
                }
            ) as response:
                response.raise_for_status()
                return await response.json()

    @staticmethod
    async def get_search_result(query: str, limit=14, sorting="RATING_DESC", include="", exclude="season,publish_day,genres.image") -> dict:
        async with ClientSession() as session:
            async with session.get(
                url="https://api.anilibria.app/api/v1/anime/catalog/releases",
                params={
                    "limit": limit,
                    "f[search]": query,
                    "f[sorting]": sorting,
                    "include": include,
                    "exclude": exclude
                }
            ) as response:
                response.raise_for_status()
                return await response.json()

    @staticmethod
    async def get_release_info(alias: str, include="", exclude="members,season,publish_day,genres.image,torrents") -> dict:
        async with ClientSession() as session:
            async with session.get(
                url=f"https://api.anilibria.app/api/v1/anime/releases/{alias}",
                params={
                    "include": include,
                    "exclude": exclude
                }
            ) as response:
                response.raise_for_status()
                return await response.json()

    @staticmethod
    async def get_genres(include="id,name,total_releases", exclude="") -> list:
        async with ClientSession() as session:
            async with session.get(
                url="https://api.anilibria.app/api/v1/anime/genres",
                params={
                    "include": include,
                    "exclude": exclude
                }
            ) as response:
                response.raise_for_status()
                return await response.json()