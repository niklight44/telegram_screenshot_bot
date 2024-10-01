import os
from aiogram import Bot


TOKEN = os.getenv("Token")
print(f"TOKEN: {TOKEN}")
TELEGRAM_BOT = Bot(token=TOKEN)
