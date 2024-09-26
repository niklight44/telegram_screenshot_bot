from aiogram import types
from aiogram.fsm.context import FSMContext

from bot.states import UserState


async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(UserState.surname)  # Corrected state transition
    await message.answer("Введите вашу фамилию:")
