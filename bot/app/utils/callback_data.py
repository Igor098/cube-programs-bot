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
        if len(parts) != 4:
            raise InvalidCallbackPayload("Неверное количество частей")

        action, page_str, id_str, ver_str = parts

        if action not in {"p", "d"}:
            raise InvalidCallbackPayload("Неизвестное действие")

        # Парсинг версии
        try:
            version = int(ver_str)
            if version < 0:
                raise ValueError
        except ValueError:
            raise InvalidCallbackPayload("Версия должна быть положительным числом")

        # Для списка
        if action == "p":
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
        elif action == "d":
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
    return f"p|{page}|-|{ver}"

def encode_detail(page, program_id, ver):
    return f"d|{page}|{program_id}|{ver}"
