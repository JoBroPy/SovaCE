from application.interfaces.repositories import (
    UserRepositoryProtocol,
    AccountBalanceRepositoryProtocol,
)
from application.interfaces.other_interfaces import (
    CacheProtocol,
    SerializationMapperProtocol,
    HttpApiProtocol,
)
from application.use_cases import (
    GetAllAccountBalancesUseCase,
    GetAccountBalanceUseCase,
    TransferBalanceUseCase,
    GetUserUseCase,
    GetAllUsersUseCase,
    AddUserUseCase,
    OpenTypeOfAccountWithUserUseCase,
    GetDataFromCacheUseCase,
    SaveDataToCacheUseCase,
)
from infrastructure.database.db_rep import (
    SQLAlchemyAccountBalanceRepository,
    SQLAlchemyUserRepository,
)
from infrastructure.database.cache_rep import RedisCacheRepository
from infrastructure.external.http_client_rep import HttpClientAPIRepository
from infrastructure.mappers.redis_mapper import RedisCacheMapper
from infrastructure.mappers.http_api_mapper import HttpApiMapper

from dotenv import load_dotenv
import os
import urllib.parse
import aiohttp

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from redis.commands.search import AsyncPipeline

load_dotenv()


def generate_google_oauth_redirect_uri() -> str:
    query_params = {
        "client_id": os.getenv("OAUTH_GOOGLE_CLIENT_ID"),
        "redirect_uri": "http://127.0.0.1:5500/auth.html",
        "response_type": "code",
        "scope": " ".join(
            [
                "openid",
                "email",
                "profile",
            ]
        ),
        # "state": secrets.token_urlsafe(16)
    }

    query_string = urllib.parse.urlencode(query_params, quote_via=urllib.parse.quote)
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"

    return f"{base_url}?{query_string}"


async def get_http_client(request: Request) -> aiohttp.ClientSession:
    return request.app.state.http_client


async def access_to_db_session(request: Request):
    async with request.app.state.SessionLocal() as session:
        yield session


async def access_to_redis_pipe(request: Request):
    async with request.app.state.redis.pipeline() as pipe:
        yield pipe


class DepForBindingInnerLayerSQLAlchemy:
    def __init__(self, session: AsyncSession):
        self._account_balance_repo: AccountBalanceRepositoryProtocol = (
            SQLAlchemyAccountBalanceRepository(session)
        )
        self._user_repo: UserRepositoryProtocol = SQLAlchemyUserRepository(session)

    # -----Use Case для Account Balance--------------------------------------------------------------------------------------

    async def get_account_balance_use_case(self):
        return GetAccountBalanceUseCase(self._account_balance_repo)

    async def get_all_account_balances_use_case(self):
        return GetAllAccountBalancesUseCase(self._account_balance_repo)

    async def transfer_balance_use_case(self):
        return TransferBalanceUseCase(self._account_balance_repo)

    # -----Use Case для User-------------------------------------------------------------------------------------------------

    async def get_user_use_case(self):
        return GetUserUseCase(self._user_repo)

    async def get_all_users_use_case(self):
        return GetAllUsersUseCase(self._user_repo)

    async def add_user_use_case(self):
        return AddUserUseCase(self._user_repo)

    async def open_type_of_account_with_user_use_case(self):
        return OpenTypeOfAccountWithUserUseCase(self._user_repo)


class DepForBindingInnerLayerRedis:
    def __init__(
        self,
        pipe: AsyncPipeline,
        redis_cache_mapper: SerializationMapperProtocol = RedisCacheMapper,
    ):
        self._cache_repo: CacheProtocol = RedisCacheRepository(pipe)
        self._redis_cache_mapper = redis_cache_mapper

    # -----Use Case для Cache------------------------------------------------------------------------------------------------

    async def get_something_from_cache_use_case(self):
        return GetDataFromCacheUseCase(self._cache_repo, self._redis_cache_mapper)

    async def save_something_to_cache_use_case(self):
        return SaveDataToCacheUseCase(self._cache_repo, self._redis_cache_mapper)


class DepForBindingInnerLayerHttpClient:
    def __init__(
        self,
        http_client: aiohttp.ClientSession,
        http_api_mapper: SerializationMapperProtocol = HttpApiMapper,
    ):
        self._api_request_repo: HttpApiProtocol = HttpClientAPIRepository(http_client)
        self._http_api_mapper = http_api_mapper

    # Здесь должны быть use case`ы, однако мне они не нужны будут поэтому я их здесь не прописывал
