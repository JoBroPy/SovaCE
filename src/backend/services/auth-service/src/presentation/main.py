from infrastructure.config.conf_for_database import ConfigForDatabase
from infrastructure.config.conf_for_cache import ConfigForCache

from presentation.routers.auth import auth_router
from presentation.routers.check_protected import protected_router

from contextlib import asynccontextmanager
import aiohttp

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.engine = ConfigForDatabase.engine
    app.state.SessionLocal = ConfigForDatabase.session_factory

    app.state.redis = ConfigForCache.engine_redis

    app.state.http_client = aiohttp.ClientSession()

    app.state.ttl_auth = 1 * 24 * 60 * 60  # день * час * минуты * секунды

    yield  # ← Приложение работает здесь

    # Shutdown
    await app.state.engine.dispose()
    await app.state.redis.aclose()
    await app.state.http_client.close()


app = FastAPI(title="Auth Service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_credentials=True,
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(protected_router)
