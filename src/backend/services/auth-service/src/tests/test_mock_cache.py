from presentation.dep_funcs.dependencies import DepForBindingInnerLayerRedis

from unittest.mock import AsyncMock
import pytest


@pytest.mark.asyncio
async def test_get_user_id_from_cache_redis() -> None:
    fake_redis_pipe = AsyncMock()

    fake_redis_pipe.hgetall.return_value = None
    fake_redis_pipe.execute.return_value = [{"UserId": "1929-2131-4422"}]

    use_case_hgetall_ui = await DepForBindingInnerLayerRedis(
        fake_redis_pipe
    ).get_something_from_cache_use_case()
    result_use_case_hgetall_ui = await use_case_hgetall_ui("users:session:123124141")
    ui = result_use_case_hgetall_ui.get("UserId")

    assert bool(ui) is True
