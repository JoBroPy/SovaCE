from dotenv import load_dotenv
import os

from redis.asyncio import Redis

load_dotenv()


class ConfigForCache:
    _redis_url_from_env: str = os.getenv("REDIS_DATABASE_URL") or ""

    engine_redis = Redis.from_url(
        _redis_url_from_env,
        decode_responses=True,  # 🔥 Возвращает str, а не bytes
        max_connections=50,  # 🔥 Максимум соединений в пуле
    )
