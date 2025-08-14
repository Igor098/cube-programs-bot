from pydantic import BaseModel, Field


class TwaAuthIn(BaseModel):
    init_data: str = Field(..., description="window.Telegram.WebApp.initData")