from dataclasses import dataclass


class InvalidCallbackPayload(Exception):
    """Некорректная строка callback_data."""

@dataclass(frozen=True)
class CallbackPayload:
    action: str  # "p" или "d"
    page: int | None
    program_id: int | None
    version: int

    @classmethod
    def parse(cls, raw: str) -> "CallbackPayload":
        # Проверка длины — защита от мусора
        if not raw or len(raw) > 40:
            raise InvalidCallbackPayload("Пустая или слишком длинная строка")

        parts = raw.split("|")
        print("parts: ", parts)
        if len(parts) != 4:
            raise InvalidCallbackPayload("Неверное количество частей")

        action, page_str, id_str, ver_str = parts

        if action not in {"list", "detail", "enroll"}:
            raise InvalidCallbackPayload("Неизвестное действие")

        # Парсинг версии
        try:
            version = int(ver_str)
            if version < 0:
                raise ValueError
        except ValueError:
            raise InvalidCallbackPayload("Версия должна быть положительным числом")

        # Для списка
        if action == "list":
            if id_str != "-":
                raise InvalidCallbackPayload("В режиме списка id должен быть '-'")
            try:
                page = int(page_str)
                if page < 0:
                    raise ValueError
            except ValueError:
                raise InvalidCallbackPayload("Неверный номер страницы")
            return cls(action=action, page=page, program_id=None, version=version)

        # Для деталей
        elif action == "detail":
            try:
                program_id = int(id_str)
                page = int(page_str)
                if page < 0:
                    raise ValueError
                if program_id < 1:
                    raise ValueError
            except ValueError:
                raise InvalidCallbackPayload("Неверный id программы")
            return cls(action=action, page=page, program_id=program_id, version=version)
        
        # Для записи
        elif action == "enroll":
            try:
                program_id = int(id_str)
                page = int(page_str)
                if page < 0:
                    raise ValueError
                if program_id < 1:
                    raise ValueError
            except ValueError:
                raise InvalidCallbackPayload("Неверный id программы")
            return cls(action=action, page=page, program_id=program_id, version=version)

def encode_list(page, ver):
    print(f"list encode: {page}, {ver}")
    return f"list|{page}|-|{ver}"

def encode_detail(page, program_id, ver):
    print(f"detail encode: {page}, {program_id}, {ver}")
    return f"detail|{page}|{program_id}|{ver}"

def encode_enroll(page: int, program_id: int, version: int) -> str:
    print(f"enroll encode: {page}, {program_id}, {version}")
    return f"enroll|{page}|{program_id}|{version}"

def encode_pick(age: int, version: int) -> str:
    print(f"enroll encode: {age}, {version}")
    return f"pick|age|{age}|{version}"

def encode_pick_page(age: int, page: int, ver: int) -> str:
    return f"pick:page:{age}:{page}:{ver}"

def encode_pick_return(age: int, page: int) -> str:
    return f"pick:return:{age}:{page}"
