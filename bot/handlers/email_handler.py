from aiogram import types
from aiogram.fsm.context import FSMContext

from bot.states import UserState


async def process_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await state.set_state(UserState.phone)
    await message.answer("Введите ваш телефон:")
