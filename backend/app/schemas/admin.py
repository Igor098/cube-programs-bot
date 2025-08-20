import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.core.error_messages import INCORRECT_PASSWORD, INCORRECT_USERNAME
from app.core.regexps import PASSWORD_REGEX, USERNAME_REGEX


class AdminCreateSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, title="Логин", description="Логин администратора",
                          examples=["admin"])

    password: str = Field(..., min_length=8, max_length=255, title="Пароль", description="Пароль администратора",
                          examples=["Password123$"])
    telegram_id: Optional[int] = Field(None, title="ID Telegram", description="ID администратора в Telegram",
                                       examples=[123456789])

    @field_validator('password')
    def validate_password(cls, value):
        is_valid = re.fullmatch(PASSWORD_REGEX, value)
        if not is_valid:
            raise ValueError(INCORRECT_PASSWORD)
        return value

    @field_validator('username')
    def validate_username(cls, value):
        is_valid = re.fullmatch(USERNAME_REGEX, value)
        if not is_valid:
            raise ValueError(INCORRECT_USERNAME)
        return value

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "admin",
                    "password": "Password123$",
                    "telegram_id": 123456789
                },
                {
                    "username": "admin",
                    "password": "Password123$",
                }
            ]
        }
    }


class AdminLoginSchema(BaseModel):
    username: str = Field(..., min_length=3, max_length=100, title="Логин", description="Логин администратора",
                          examples=["admin"])
    password: str = Field(..., min_length=8, max_length=255, title="Пароль", description="Пароль администратора",
                          examples=["Password123$"])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "admin",
                    "password": "Password123$"
                }
            ]
        }
    }


class AdminTelegramLoginSchema(BaseModel):
    telegram_id: int = Field(..., title="ID Telegram", description="ID администратора в Telegram", examples=[123456789])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "telegram_id": 123456789
                }
            ]
        }
    }


class AdminTelegramSchema(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class AdminSchema(BaseModel):
    id: int = Field(..., title="ID", description="ID администратора", examples=[1, 10])

    username: str = Field(..., min_length=3, max_length=100, title="Логин", description="Логин администратора",
                          examples=["admin"])
    telegram_id: Optional[int] = Field(None, title="ID Telegram", description="ID администратора в Telegram",
                                       examples=[123456789])

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "admin",
                    "telegram_id": 123456789
                },
                {
                    "username": "admin"
                }
            ]
        }
    }


class AdminFilter(BaseModel):
    id: Optional[int] = None
    telegram_id: Optional[int] = None
    username: Optional[str] = None
