from aiogram import types
from aiogram.fsm.context import FSMContext

from bot.states import UserState


async def start(message: types.Message, state: FSMContext) -> None:
    await state.set_state(UserState.name)
    await message.answer('Здравствуйте! Давайте знакомиться! Меня зовут Чумба. А как зовут вас?')