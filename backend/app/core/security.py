import uuid
from typing import Optional, Tuple

from loguru import logger
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from core.error_messages import TOKEN_NOT_VALID
from core.token_types import TokenType

from core.config import settings
from exceptions.business import TokenNotValidError

from fastapi.responses import Response

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
