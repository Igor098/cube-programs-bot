from datetime import time
from loguru import logger
from typing import Any, List, Optional
from states.programs_store import store
from models import ProgramWithId, Group, TimeSlot
from .program_service import get_programs_list


def _none_if_empty(v: Any) -> Optional[str]:
    return None if isinstance(v, str) and v.strip() == "" else v

def _to_bool(v: Any, default: bool = True) -> bool:
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip().lower()
        if s in {"true", "1", "yes", "y"}:
            return True
        if s in {"false", "0", "no", "n"}:
            return False
    if isinstance(v, (int, float)):
        return bool(v)
    return default

def _to_time(v: Any) -> time:
    """
    Ожидает str в ISO ('HH:MM' / 'HH:MM:SS[.ffffff][+HH:MM]') или уже time.
    """
    if isinstance(v, time):
        return v
    if isinstance(v, str):
        return time.fromisoformat(v)
    raise ValueError(f"Unsupported time value: {v!r}")

def _to_str(v: Any, default: str = "") -> str:
    if v is None:
        return default
    return str(v).strip()

def _to_int(v: Any) -> int:
    return int(v)

def _program_level_to_str(v: Any) -> Optional[str]:
    if v is None:
        return None
    val = getattr(v, "value", v)
    s = str(val).strip()
    return s or None

def _as_list(v: Any) -> list:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    if isinstance(v, dict):
        return [v]
    raise TypeError(f"Expected list/dict for collection, got {type(v).__name__}")


def _map_program(raw: dict[str, Any]) -> ProgramWithId:
    groups_raw = raw.get("groups")
    groups_list = _as_list(groups_raw)

    groups: List[Group] = []
    for g in groups_list:
        slots_raw = g.get("time_slots", g.get("slots"))
        slot_items = _as_list(slots_raw)

        slots: list[TimeSlot] = []
        for s in slot_items:
            slots.append(
                TimeSlot(
                    id=_to_int(s.get("id", 0)),
                    weekday=_to_int(s["weekday"]),
                    start_time=_to_time(s["start_time"]),
                    end_time=_to_time(s["end_time"]),
                )
            )

        groups.append(
            Group(
                id=_to_int(g.get("id", 0)),
                name=_to_str(g["name"]),
                time_slots=slots,
            )
        )

    return ProgramWithId(
        id=_to_int(raw["id"]),
        name=_to_str(raw["name"]),
        short_name=_to_str(raw.get("short_name", "")),
        description=_to_str(raw.get("description", "")),
        min_age=_to_int(raw["min_age"]),
        max_age=_to_int(raw["max_age"]),
        program_level=_program_level_to_str(raw.get("program_level")),
        navigator_link=_to_str(raw.get("navigator_link", "")),  # у тебя тип str (не Optional)
        requirements=_none_if_empty(raw.get("requirements")),
        image_url=_none_if_empty(raw.get("image_url")),
        is_active=_to_bool(raw.get("is_active", True)),
        groups=groups,
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
            items.append(_map_program(raw))
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