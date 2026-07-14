from presentation.main import app

import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_get_balances() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        response = await ac.get("/balances")
        assert response.status_code == 404
