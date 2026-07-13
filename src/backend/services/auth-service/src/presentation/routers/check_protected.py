from application.dto import AccountBalanceAndTypesOfAccountDTO, AllAccountBalancesDTO

from presentation.dep_funcs.dependencies import (
    DepForBindingInnerLayerSQLAlchemy,
    DepForBindingInnerLayerRedis,
    access_to_db_session,
    access_to_redis_pipe,
)

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from redis.exceptions import RedisError
from redis.commands.search import AsyncPipeline
from sqlalchemy.ext.asyncio import AsyncSession

protected_router = APIRouter(prefix="/api/user", tags=["protected"])


@protected_router.get(
    "/balances", response_model=List[AccountBalanceAndTypesOfAccountDTO]
)
async def get_balances(
    request: Request,
    pipe: AsyncPipeline = Depends(access_to_redis_pipe),
    session: AsyncSession = Depends(access_to_db_session),
) -> List[AccountBalanceAndTypesOfAccountDTO] | AllAccountBalancesDTO:

    checked_sess_id: str | None = (
        request.cookies.get("session_id") if "session_id" in request.cookies else None
    )

    if not checked_sess_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Cookies failed: Нету куки"
        )

    try:
        use_case_hgetall_ui = await DepForBindingInnerLayerRedis(
            pipe
        ).get_something_from_cache_use_case()
        result_use_case_hgetall_ui = await use_case_hgetall_ui(
            f"users:session:{checked_sess_id}"
        )
    except RedisError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Redis connection error: "
            "Не удалось взять данные о сессии пользователя",
        )

    if not result_use_case_hgetall_ui:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization failed: сессия истекла",
        )

    ui = result_use_case_hgetall_ui.get("UserId")

    try:
        ui = int(ui)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400, detail="Invalid user_id format: Неправильный user_id"
        )

    try:
        use_case_get_all = await DepForBindingInnerLayerSQLAlchemy(
            session
        ).get_all_account_balances_use_case()
        return await use_case_get_all(ui)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
