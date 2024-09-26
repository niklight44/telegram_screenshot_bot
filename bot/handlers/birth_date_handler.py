from aiogram import types
from aiogram.fsm.context import FSMContext


from datetime import datetime

async def process_birth_date(message: types.Message, state: FSMContext):
    try:
        # Try parsing the date to ensure it's in the correct format
        birth_date = datetime.strptime(message.text, '%Y-%m-%d')
        await state.update_data(birth_date=message.text)

        user_data = await state.get_data()
        # TODO: добавить код для записи данных в базу данных

        await message.answer("Спасибо, ваши данные сохранены!")
        await state.finish()
    except ValueError:
        await message.answer("Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")

