from aiogram.fsm.state import StatesGroup, State

class PickAge(StatesGroup):
    age = State()
    results = State()