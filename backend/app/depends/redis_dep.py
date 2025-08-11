from redis.asyncio import Redis
from core.config import settings

redis_host = settings.REDIS_HOST
redis_port = int(settings.REDIS_PORT)
redis_user = settings.REDIS_USER
redis_password = settings.REDIS_PASSWORD

redis_client = Redis(
    host=redis_host,
    port=redis_port,
    username=redis_user,
    password=redis_password,
    decode_responses=True
)


async def get_redis():
    return redis_client
