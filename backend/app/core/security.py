import uuid
import hmac
import hashlib
import time

from typing import Optional, Tuple

from loguru import logger
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from redis.asyncio import Redis

from core.error_messages import TOKEN_NOT_VALID
from core.token_types import TokenType

from core.config import settings
from exceptions.business import TokenNotValidError

from fastapi.responses import Response

from dataclasses import dataclass
from typing import Optional
from urllib.parse import parse_qsl
import json

class TwaVerificationError(Exception):
    pass

@dataclass
class VerifiedTwa:
    telegram_id: int
    auth_date: int
    hash: str
    query_id: Optional[str]
    raw: dict

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_element(text):
    return pwd_context.hash(text)


def verify(plain_text, hashed_text):
    return pwd_context.verify(plain_text, hashed_text)


def create_jwt_token(id: int, expires_delta: timedelta, token_type: str, jti: Optional[str] = None) -> str:
    expire = datetime.now(tz=timezone.utc) + expires_delta
    logger.info(f"Token type: {token_type}")
    payload = {
        "sub": str(id),
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "exp": int(expire.timestamp()),
        "iat": int(datetime.now(tz=timezone.utc).timestamp()),
        "type": token_type,
    }
    if jti:
        payload["jti"] = jti

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(user_id: int) -> str:
    return create_jwt_token(
        user_id,
        expires_delta=timedelta(seconds=settings.ACCESS_TTL),
        token_type=TokenType.ACCESS
    )


def create_refresh_token(user_id: int, jti: Optional[str] = None) -> Tuple[str, str | None]:
    jti = jti or str(uuid.uuid4())
    return create_jwt_token(
        user_id,
        expires_delta=timedelta(seconds=settings.REFRESH_TTL),
        token_type=TokenType.REFRESH,
        jti=jti
    ), jti


def create_csrf_token(user_id: int) -> str:
    return create_jwt_token(
        user_id,
        expires_delta=timedelta(seconds=settings.CSRF_TTL),
        token_type=TokenType.CSRF
    )


def create_bot_token(telegram_id: int) -> str:
    return create_jwt_token(
        telegram_id,
        expires_delta=timedelta(seconds=settings.BOT_TTL),
        token_type=TokenType.BOT
    )


def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER
        )
        logger.info(f"Payload: {payload}")
        token_type = payload.get("type")
        iss = payload.get("iss")
        aud = payload.get("aud")

        if iss != settings.JWT_ISSUER or aud != settings.JWT_AUDIENCE or token_type != expected_type:
            raise JWTError

        return payload

    except JWTError as e:
        logger.error(f"Ошибка при декодировании токена: {e}")
        raise TokenNotValidError(TOKEN_NOT_VALID)


def set_cookie(response: Response, token: str, token_type: str, ttl: int):
    response.set_cookie(
        key=f"{token_type}_token",
        value=token,
        httponly=False if token_type == TokenType.CSRF else True,
        samesite="lax",
        max_age=ttl
    )

def _parse_init_data(init_data: str) -> dict:
    # Превращаем query-string в dict без URL-декодирования вручную — parse_qsl сделает сам
    try:
        items = parse_qsl(init_data, strict_parsing=True)  # бросит ValueError при мусоре
        data = {k: v for k, v in items}
    except Exception as e:
        raise TwaVerificationError(f"Bad init_data: {e}")
    if "hash" not in data:
        raise TwaVerificationError("Missing hash in init_data")
    if "auth_date" not in data:
        raise TwaVerificationError("Missing auth_date in init_data")
    if "user" not in data:
        raise TwaVerificationError("Missing user in init_data")
    return data

def verify_init_data(init_data: str, bot_token: str, max_age_sec: int = 300) -> VerifiedTwa:
    data = _parse_init_data(init_data)
    received_hash = data.pop("hash")
    # Собираем data_check_string из отсортированных пар key=value
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    # Ключ для HMAC — sha256(bot_token)
    secret_key = hashlib.sha256(bot_token.encode("utf-8")).digest()
    expected_hash = hmac.new(secret_key, data_check_string.encode("utf-8"), hashlib.sha256).hexdigest()

    # Сравнение подписи — безопасно
    if not hmac.compare_digest(expected_hash, received_hash):
        raise TwaVerificationError("Invalid Telegram hash")

    # Проверка TTL
    auth_date = int(data["auth_date"])
    if time.time() - auth_date > max_age_sec:
        raise TwaVerificationError("auth_date is too old")

    # Достаём telegram_id
    try:
        user = json.loads(data["user"])
        telegram_id = int(user["id"])
    except Exception:
        raise TwaVerificationError("Bad user field")

    return VerifiedTwa(
        telegram_id=telegram_id,
        auth_date=auth_date,
        hash=received_hash,
        query_id=data.get("query_id"),
        raw=data,
    )

class ReplayError(Exception):
    pass

async def assert_not_replayed(redis: Redis, marker: str, ttl: int) -> None:
    # SETNX + EX — установит ключ только если его нет
    ok = await redis.set(name=f"auth:twa:replay:{marker}", value="1", ex=ttl, nx=True)
    if not ok:
        raise ReplayError("Replay detected")