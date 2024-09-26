from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from bot.handlers.name_handler import process_name
from bot.handlers.surname_handler import process_surname
from bot.handlers.email_handler import process_email
from bot.handlers.phone_handler import process_phone
from bot.handlers.birth_date_handler import process_birth_date
from bot.states import UserState


def register_user_handlers(router: Router):
    router.message.register(process_name, UserState.name)
    router.message.register(process_surname, UserState.surname)
    router.message.register(process_email, UserState.email)
    router.message.register(process_phone, UserState.phone)
    router.message.register(process_birth_date, UserState.birth_date)
