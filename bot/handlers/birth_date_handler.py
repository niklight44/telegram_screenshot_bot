from aiogram import types
from aiogram.fsm.context import FSMContext
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from ..database import User, UserQueue  # Import the correct models
from ..database import engine  # Your database engine

# Setup SQLAlchemy session
Session = sessionmaker(bind=engine)


async def process_birth_date(message: types.Message, state: FSMContext):
    session = Session()  # Create a new session

    try:
        # Try parsing the date to ensure it's in the correct format
        birth_date = datetime.strptime(message.text, '%d-%m-%Y')
        await state.update_data(birth_date=birth_date)  # Store parsed date

        # Retrieve user data from FSMContext
        user_data = await state.get_data()

        # Assuming user data includes name, surname, email, etc.
        user_id = message.from_user.id  # Using Telegram's user_id

        # Check if the user exists in the database
        user = session.query(User).filter_by(user_id=user_id).first()

        if not user:
            # If user doesn't exist, create a new one
            user = User(
                user_id=user_id,
                name=user_data['name'],  # Assuming 'name' is in state data
                surname=user_data['surname'],
                email=user_data['email'],
                phone=user_data['phone'],
                birthday=birth_date
            )
            session.add(user)

        # Add the user to the queue (assuming user_id is a ForeignKey in UserQueue)
        user_queue = UserQueue(user_id=user.user_id)
        session.add(user_queue)

        # Commit the transaction to save the user and the queue entry
        session.commit()

        await message.answer("Спасибо, ваши данные и очередь сохранены!")
        await state.finish()

    except ValueError:
        await message.answer("Пожалуйста, введите дату в формате ГГГГ-ММ-ДД.")

    except Exception as e:
        session.rollback()  # Rollback in case of an error
        await message.answer("Произошла ошибка при сохранении данных.")
        raise e  # Log or handle the error as needed

    finally:
        session.close()  # Close the session
