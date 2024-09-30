import asyncio
import logging
import os
from aiogram import Dispatcher, Bot
from sqlalchemy.engine import URL

from bot.commands import register_user_commands
from bot.database import create_async_engine, get_session_maker, BaseModel, proceed_schemas
from bot.handlers import register_user_handlers
from bot.tasks import app
from bot import TELEGRAM_BOT

async def main() -> None:
    logging.basicConfig(level=logging.DEBUG, filename='./logs/bot.log', filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s')

    dp = Dispatcher()

    register_user_commands(dp)
    register_user_handlers(dp)

    print(f"Username: {os.getenv('POSTGRES_USER')}")
    print(f"Password: {os.getenv('POSTGRES_PASSWORD')}")
    print(f"Host: {os.getenv('POSTGRES_HOST')}")
    print(f"Database: {os.getenv('POSTGRES_DB')}")
    print(f"Port: {os.getenv('POSTGRES_PORT')}")
    # TODO: добавить переменные БД в .env
    postgres_url = URL.create(
        "postgresql+asyncpg",
        username=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv("POSTGRES_DB"),
        port=os.getenv("POSTGRES_PORT")
    )

    async_engine = create_async_engine(postgres_url)
    session_maker = get_session_maker(async_engine)
    await proceed_schemas(async_engine, BaseModel.metadata)

    # Starting Celery app
    # app.start()

    await dp.start_polling(TELEGRAM_BOT)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot Stopped')
