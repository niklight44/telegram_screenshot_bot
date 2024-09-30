import os
from aiogram import Bot


TOKEN = os.getenv("Token")
TELEGRAM_BOT = Bot(token=TOKEN)
