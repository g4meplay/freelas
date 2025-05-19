import httpx
from httpx import Response


class Client:

    @staticmethod
    async def get(url: str, *args, **kwargs) -> Response:
        async with httpx.AsyncClient(timeout=3600) as client:
            return await client.get(url, *args, **kwargs)
 
    @staticmethod
    async def post(url: str, *args, **kwargs) -> Response:
        async with httpx.AsyncClient(timeout=3600) as client:
            return await client.post(url, *args, **kwargs)
