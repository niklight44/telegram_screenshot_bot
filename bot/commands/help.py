from aiogram.types import Message


async def help(message: Message):
    return message.answer('Здесь вы сможете получить помощь по функционалу бота!')