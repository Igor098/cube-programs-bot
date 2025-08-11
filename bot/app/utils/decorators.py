from functools import wraps
import httpx
from config import settings

def with_http_client(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with httpx.AsyncClient(
            base_url=settings.API_URL,
            timeout=10.0,
        ) as client:
            return await func(*args, client=client, **kwargs)
    return wrapper