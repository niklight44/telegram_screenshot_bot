import os
from aiogram import types
from aiogram.fsm.context import FSMContext
from datetime import datetime

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select

from ..database import User, UserQueue

# Create the database URL
postgres_url = URL.create(
    "postgresql+asyncpg",
    username=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('POSTGRES_HOST'),
    database=os.getenv("POSTGRES_DB"),
    port=os.getenv("POSTGRES_PORT")
)

# Create the asynchronous engine
async_engine = create_async_engine(postgres_url, future=True)

# Create the asynchronous session maker
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def process_birth_date(message: types.Message, state: FSMContext):
    async with AsyncSessionLocal() as session:  # Use async context manager for the session
        try:
            # Try parsing the date to ensure it's in the correct format
            birth_date = datetime.strptime(message.text, '%d.%m.%Y')
            await state.update_data(birth_date=birth_date)  # Store parsed date

            # Retrieve user data from FSMContext
            user_data = await state.get_data()

            # Check if the user with a specific phone exists in the database
            stmt = select(User).where(User.phone == user_data['phone'])
            result = await session.execute(stmt)
            user = result.scalars().first()

            if not user:
                # If user doesn't exist, create a new one
                user = User(
                    name=user_data['name'],
                    surname=user_data['surname'],
                    email=user_data['email'],
                    phone=user_data['phone'],
                    birthday=birth_date
                )
                session.add(user)
                await session.commit()  # Commit after adding user

            # Create a new session for adding the user to the queue
            async with session.begin():  # Start a new transaction
                user_queue = UserQueue(user_id=user.id)
                session.add(user_queue)

                # Commit the transaction to save the queue entry
                await session.commit()

            await message.answer("Спасибо, ваши данные и очередь сохранены!")
            await state.clear()

        except ValueError:
            await message.answer("Пожалуйста, введите дату в формате ДД.ММ.ГГГГ.")

        except Exception as e:
            await session.rollback()  # Rollback in case of an error
            await message.answer("Произошла ошибка при сохранении данных.")
            raise e  # Log or handle the error as needed
