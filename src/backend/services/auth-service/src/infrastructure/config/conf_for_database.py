from dotenv import load_dotenv
import os

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv()


class ConfigForDatabase:
    _db_url_from_env: str = os.getenv("DATABASE_URL_ASYNC") or ""

    engine = create_async_engine(
        url=_db_url_from_env, echo=False, pool_size=5, max_overflow=10
    )

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
