from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    name = State()
    surname = State()
    email = State()
    phone = State()
    birth_date = State()
