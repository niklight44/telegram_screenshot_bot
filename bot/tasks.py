import asyncio
import logging
import os
import time

from aiogram.types import FSInputFile
from celery import Celery
from celery.schedules import crontab
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from transliterate import translit


from .database import UserQueue, User
from .loggers.celery_logger import logger
from bot import TELEGRAM_BOT

postgres_url = URL.create(
    "postgresql+asyncpg",
    username=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('POSTGRES_HOST'),
    database=os.getenv("POSTGRES_DB"),
    port=os.getenv("POSTGRES_PORT")
)

async_engine = create_async_engine(postgres_url)

# Setting up async SQLAlchemy session
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

app = Celery('bot.tasks', broker='redis://redis:6379/0', include="bot.tasks")

# Setting up periodic task
app.conf.beat_schedule = {
    'fill-form-and-screenshot-every-10-minutes': {
        'task': 'bot.tasks.fill_form_and_screenshot',
        'schedule': crontab(minute='*/5'),  # Runs every 5 minutes
    },
}
app.conf.timezone = 'UTC'


@app.task
def fill_form_and_screenshot():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_fill_form_and_screenshot())


async def _fill_form_and_screenshot():
    # Create an async session for this task
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Fetching user_id from UserQueue table
            result = await session.execute(select(UserQueue))
            user_queue_entry = result.scalars().first()

            if not user_queue_entry:
                logger.error("No users found in UserQueue")
                return

            user_id = user_queue_entry.user_id

            # Fetching user data from the database
            result = await session.execute(select(User).filter_by(id=user_id))
            user = result.scalars().first()

            if not user:
                logger.error(f"No user found with ID {user_id}")
                return

            data = {
                'name': user.name,
                'surname': user.surname,
                'email': user.email,
                'phone': user.phone,
                'birthday': user.birthday.strftime('%Y-%m-%d'),  # Convert to string if necessary
                'chat_id': user.chat_id
            }
            logger.info(data)

            logger.info(f'Filling form and making screenshot for user {user.id}')

            # Selenium setup
            user_agent = 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36'
            options = webdriver.ChromeOptions()
            options.add_argument(f"--user-agent={user_agent}")
            options.add_argument('--lang=ru-RU')
            options.add_argument('headless')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')
            options.add_argument('--remote-encoding=UTF-8')
            driver = webdriver.Chrome(options=options)

            try:
                driver.get("https://b24-iu5stq.bitrix24.site/backend_test/")

                # Filling the form
                name_element = driver.find_element(By.NAME, 'name')
                name_element.clear()
                name_element.click()
                name = translit(data['name'], 'ru', reversed=True)
                name_element.send_keys(name)
                lastname_element = driver.find_element(By.NAME, 'lastname')
                lastname_element.clear()
                lastname_element.click()
                surname = translit(data['surname'], 'ru', reversed=True)
                lastname_element.send_keys(surname)
                driver.save_screenshot("step1.png")
                driver.find_element(By.CLASS_NAME, "b24-form-btn").click()
                driver.save_screenshot("after_clicking_step1.png")
                await asyncio.sleep(2)
                logger.info(f'Filled Name and surname')
                try:
                    email_input = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((By.NAME, 'email'))
                    )
                    email_input.clear()
                    email_input.click()
                    email_input.send_keys(data['email'])
                except TimeoutException:
                    print("Timeout: Email field not found after clicking Next")
                    # Optionally take a screenshot for debugging
                    driver.save_screenshot("timeout_error.png")
                driver.find_element(By.NAME, 'phone').send_keys(data['phone'])
                driver.save_screenshot("step2.png")
                driver.find_element(By.CSS_SELECTOR, "div.b24-form-btn-container > div:nth-child(2) > button").click()
                await asyncio.sleep(2)
                logger.info(f'Filled Email and Phone')
                driver.save_screenshot("after_clicking_step2.png")
                # logger.info(data['birthday'])
                birthday_input = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.CLASS_NAME, 'b24-form-control'))
                )
                birthday_input.send_keys(data['birthday'])
                # Submiting our form
                logger.info('Filled birthday data')
                driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

                # Screenshot result
                os.makedirs('screenshots', exist_ok=True)
                screenshot_path = f"screenshots/{time.strftime('%Y-%m-%d_%H:%M')}_{user.id}.png"
                await asyncio.sleep(2)
                driver.save_screenshot(screenshot_path)

                await TELEGRAM_BOT.send_photo(chat_id=data['chat_id'], photo=FSInputFile(path=screenshot_path),
                                                  caption="Вот ваш обещанный скриншот!")

                # Remove user from queue and commit the transaction
                await session.delete(user_queue_entry)
                await session.commit()

                logger.info(f"User {user_id} has been removed from the UserQueue.")

                return screenshot_path

            finally:
                driver.quit()
