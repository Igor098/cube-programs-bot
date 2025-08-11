from aiogram.types import CallbackQuery
from aiogram.filters import BaseFilter
from utils.callback_data import CallbackPayload, InvalidCallbackPayload

class ActionFilter(BaseFilter):
    """
    Фильтрует callback_data по полю action в формате CallbackPayload.
    Пример формата: p|<page>|-|<ver> или d|<page>|<id>|<ver>
    """
    def __init__(self, action: str):
        self.action = action

    async def __call__(self, call: CallbackQuery) -> bool:
        data = call.data or ""
        if "|" not in data:
            return False
        try:
            payload = CallbackPayload.parse(data)
        except InvalidCallbackPayload:
            return False
        
        return payload.action == self.action
