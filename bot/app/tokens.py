from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict


@dataclass
class AccessTokenData:
    access_token: str
    expires_at: datetime


user_tokens: Dict[int, AccessTokenData] = {}


def get_token(telegram_id: int) -> str | None:
    token_data = user_tokens.get(telegram_id)
    now = datetime.now(timezone.utc)
    
    if token_data and token_data.expires_at > now:
        return token_data.access_token
    else:
        user_tokens.pop(telegram_id, None)
    return None
