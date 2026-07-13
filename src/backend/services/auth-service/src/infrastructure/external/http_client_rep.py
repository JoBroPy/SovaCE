from typing import Any
import aiohttp


class HttpClientRepository:
    def __init__(self, http_client: aiohttp.ClientSession):
        self.http_client = http_client


class HttpClientAPIRepository(HttpClientRepository):
    async def get(self, params: str) -> Any:
        pass

    async def post(self, params: str, value: dict[str, Any]) -> None:
        pass
