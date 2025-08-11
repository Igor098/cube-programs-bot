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

    async def __call__(self, c: CallbackQuery) -> bool:
        try:
            payload = CallbackPayload.parse(c.data)
        except InvalidCallbackPayload:
            return False
        return payload.action == self.action
