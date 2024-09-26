from aiogram import types
from aiogram.fsm.context import FSMContext

from bot.states import UserState


async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(UserState.birth_date)
    await message.answer("Введите вашу дату рождения (ДД.ММ.ГГГГ):")
