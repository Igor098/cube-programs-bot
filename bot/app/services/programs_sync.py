from loguru import logger
from typing import Any, List
from states.programs_store import store
from models import ProgramWithId  # dataclass из твоего кода
from .program_service import get_programs_list  # твоя функция

def _map_to_dataclass(raw: dict[str, Any]) -> ProgramWithId:
    # Нормализация минимально нужная: trim, lower для short_name, None для пустых строк
    def _none_if_empty(v): 
        return None if isinstance(v, str) and v.strip() == "" else v
    return ProgramWithId(
        id            = int(raw["id"]),
        name          = str(raw["name"]).strip(),
        short_name    = str(raw["short_name"]).strip(),
        description   = str(raw.get("description","")).strip(),
        min_age       = int(raw["min_age"]),
        max_age       = int(raw["max_age"]),
        category      = str(raw["category"]).strip(),
        program_level = _none_if_empty(raw.get("program_level")),
        navigator_link= str(raw["navigator_link"]).strip(),
        requirements  = _none_if_empty(raw.get("requirements")),
        image_url     = _none_if_empty(raw.get("image_url")),
        is_active     = bool(raw.get("is_active", True)),
    )

async def sync_programs_from_api() -> tuple[int, str]:
    """
    Возвращает (кол-во загруженных, сообщение).
    Не бросает сетевых исключений — они уже отловлены внутри get_programs_list().
    Может кинуть ValueError, если данные кривые.
    """
    data = await get_programs_list()  # [] при сетевой ошибке
    if not data:
        msg = "Каталог не обновлён: API вернул пустой список или была сетевая ошибка"
        logger.warning(msg)
        return 0, msg

    items: List[ProgramWithId] = []
    for i, raw in enumerate(data):
        try:
            items.append(_map_to_dataclass(raw))
        except Exception as e:
            logger.error(f"Некорректная запись #{i}: {e}")

    if not items:
        msg = "Каталог не обновлён: после валидации нет валидных программ"
        logger.warning(msg)
        return 0, msg

    # атомарный сброс
    await store.reset_programs(items)
    msg = f"Каталог обновлён: {len(items)} программ"
    logger.info(msg)
    return len(items), msg