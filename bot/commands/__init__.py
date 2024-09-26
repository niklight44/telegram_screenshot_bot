__all__ = ['start', 'register_user_commands']

from aiogram import Router
from aiogram.filters import Command

from bot.commands.start import start
from bot.commands.help import help


def register_user_commands(router: Router) -> None:
    router.message.register(start, Command(commands=['start']))
    router.message.register(help, Command(commands=['help']))