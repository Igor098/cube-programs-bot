from functools import wraps
from typing import Any, Awaitable, Callable

from aiohttp import ClientSession, ClientTimeout
from app.config import settings

def with_aiohttp_session(func: Callable[..., Awaitable[Any]]):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with ClientSession(base_url=settings.API_URL, timeout=ClientTimeout(total=10)) as session:
            return await func(*args, session=session, **kwargs)
    return wrapper