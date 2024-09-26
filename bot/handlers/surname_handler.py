from aiogram import types
from aiogram.fsm.context import FSMContext

from bot.states import UserState


async def process_surname(message: types.Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await state.set_state(UserState.email)
    await message.answer("Введите ваш email:")
