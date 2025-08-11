from html import escape as _escape
from models import ProgramWithId
from config import settings


def _clamp(text: str, max_len: int) -> str:
    if not text:
        return ""
    t = text.strip()
    return t if len(t) <= max_len else t[: max_len - 1].rstrip() + "…"


def _safe_html(s) -> str:
    if s is None:
        return ""
    return _escape(str(s))

def format_program_line(p: ProgramWithId) -> str:
    short_name = _safe_html(p.short_name)
    if not p.program_level:
        return f"{short_name} • {p.min_age}–{p.max_age} лет"
    return f"{short_name} • {p.program_level} • {p.min_age}–{p.max_age} лет"



def build_list_message(total: int, page: int, pages: int) -> str:
    """
    Формирует текстовое сообщение со списком программ.
    Возвращает:
      - полный текст сообщения (с заголовком и строкой 'Всего/Страница')
      - список строк программ (для нумерованного вывода или отдельной обработки)
    @param programs: Список программ
    @param total: Общее количество программ
    @param page: Номер текущей страницы
    @param pages: Общее количество страниц
    @return: Кортеж из полного текста сообщения и списка строк программ
    """
    page = max(0, page)
    pages = max(1, pages)

    header = []
    header.append("📚 <b>Программы обучения</b>")
    header.append("")
    header.append(f"Всего программ: {total}")
    header.append(f"Страница {page + 1} из {pages}")

    start_text = "\n".join(header)

    return start_text

def build_enroll_message(p: ProgramWithId) -> str:
    """
    Формирует текстовое сообщение для записи на программу.
    """
    navigator_link = getattr(p, "navigator_link", None) or getattr(settings, "NAVIGATOR_LINK", None)
    navigator_link = _escape(navigator_link)  

    return (
        "Для того, чтобы записаться вам нужно:\n"
        f"1️⃣ Отправить заявку в навигаторе: "
        f"<a href=\"{navigator_link}\">перейти в навигатор</a>\n"
        "2️⃣ Заполнить бланк заявления (файл ниже)\n\n"
        "Заполнить бланк можно как самостоятельно, так и прийти к нам.\n"
        f"🏢 Адрес: {_escape(settings.ORGANIZATION_ADDRESS)}\n"
        f"🕒 График работы: {_escape(settings.WORK_SHEDULE)}"
    )
    

def build_enroll_question_message():
    return (
        "<b>Хотите записаться на программу?</b> Это просто!\n\n"
        "1️⃣ Нажмите «<b>Список программ</b>» (кнопка ниже) и выберите подходящий курс.\n"
        "2️⃣ В карточке выбранной программы нажмите «<b>Записаться</b>» и следуйте инструкции."
    )
    

def build_pick_age_intro_html() -> str:
    return (
        "<b>Подберём программу по возрасту</b> 🧭\n\n"
        "Нажмите кнопку с вашим возрастом ниже — покажем только подходящие программы.\n\n"
    )
    
    
def format_program_caption_html(p: ProgramWithId) -> str:
    """
    Короткий caption для фото (лимит у Telegram около 1024 символов).
    Оставим запас ~900.
    """
    name = f"<strong>{_escape(p.short_name or p.name or "")}</strong>\n"
    level = _escape(p.program_level or "")
    age = f"{p.min_age} – {p.max_age}" if p.min_age and p.max_age else "—"

    desc = _clamp((p.description or "").replace("\n", " ").strip(), 800)
    desc = _escape(desc)

    requirements = _escape(p.requirements or "")

    head = f"<b>{name}</b>"
    age = f"📈 Возраст: <i>{age} лет</i>"
    requirements = f"\n📋 Дополнительные требования: <i>{requirements if requirements else 'Нет'}</i>"

    if not level:
        parts = [head, age, "", desc, requirements]
    else:
        level = f"🎓 Уровень: <i>{level}</i>"
        parts = [head, level, age, "", desc, requirements]

    return "\n".join(parts)
