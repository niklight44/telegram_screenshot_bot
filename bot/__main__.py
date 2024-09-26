import asyncio
import logging
import os
from aiogram import Dispatcher, Bot
from sqlalchemy.engine import URL

from bot.commands import register_user_commands
from bot.database import create_async_engine, get_session_maker, BaseModel, proceed_schemas
from bot.handlers import register_user_handlers


async def main() -> None:
    logging.basicConfig(level=logging.DEBUG, filename='../logs/bot.log', filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s')

    dp = Dispatcher()
    bot = Bot(token=os.getenv('token'))

    register_user_commands(dp)
    register_user_handlers(dp)

    # TODO: добавить переменные БД в .env
    postgres_url = URL.create(
        "posgtgresql+asyncpg",
        username=os.getenv('DB_USER'),
        host="localhost",
        database=os.getenv("DB_NAME"),
        post=os.getenv("DB_PORT")
    )
    async_engine = create_async_engine()
    session_maker = get_session_maker(async_engine)
    await proceed_schemas(async_engine, BaseModel.metadata)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot Stopped')
