import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str = ""
    DB_PORT: str = ""
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    REDIS_HOST: str = ""
    REDIS_PORT: str = ""
    REDIS_USER: str = ""
    REDIS_PASSWORD: str = ""
    ACCESS_TTL: int = 0
    REFRESH_TTL: int = 0
    CSRF_TTL: int = 0
    BOT_TTL: int = 0
    ALGORITHM: str = ""
    SECRET_KEY:str =""
    JWT_ISSUER: str = ""
    JWT_AUDIENCE: str = ""
    MODE: str = ""

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../", ".env")
    )

    def get_database_url(self):
        if self.MODE == "development":
            return f"sqlite+aiosqlite:///app/database/db.sqlite3"
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
