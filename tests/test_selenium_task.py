import asyncio
import logging
import os
import time
from celery import Celery
from celery.schedules import crontab
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from bot.database import UserQueue, User
from bot.loggers.celery_logger import logger
from bot import TELEGRAM_BOT


postgres_url = URL.create(
    "postgresql+asyncpg",
    username=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
    host=os.getenv('localhost'),
    database=os.getenv("POSTGRES_DB"),
    port=os.getenv("POSTGRES_PORT")
)

async_engine = create_async_engine(postgres_url)

# Setting up async SQLAlchemy session
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


def fill_form_and_screenshot():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_fill_form_and_screenshot())


async def _fill_form_and_screenshot():
    # Create an async session for this task
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Fetching user_id from UserQueue
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

            # Selenium setup (local WebDriver setup)
            user_agent = 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36'
            options = webdriver.ChromeOptions()
            options.add_argument(f"--user-agent={user_agent}")
            # options.add_argument('headless')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--no-sandbox')

            # service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(options=options)

            try:
                driver.get("https://b24-iu5stq.bitrix24.site/backend_test/")

                # Fill form
                driver.find_element(By.NAME, 'name').click().send_keys(data['name'])
                driver.find_element(By.NAME, 'lastname').click().send_keys(data['surname'])
                driver.save_screenshot("step1.png")
                driver.find_element(By.CLASS_NAME, "b24-form-btn").click()
                driver.save_screenshot("after_clicking_step1.png")
                await asyncio.sleep(2)
                logger.info(f'Filled Name and surname')
                try:
                    email_input = WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((By.NAME, 'email'))
                    )
                    email_input.click().send_keys(data['email'])
                except TimeoutException:
                    print("Timeout: Email field not found after clicking Next")
                    # Optionally take a screenshot for debugging
                    driver.save_screenshot("timeout_error.png")
                driver.find_element(By.NAME, 'phone').send_keys(data['phone'])
                driver.find_element(By.CLASS_NAME, "b24-form-btn").click()
                await asyncio.sleep(2)
                logger.info(f'Filled Email and Phone')
                birthday_input = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.NAME, 'birthday'))
                )
                email_input.send_keys(data['birthday'])
                # Submit form
                logger.info('Filled birthday data')
                driver.find_element(By.NAME, 'submit').click()

                # Screenshot
                os.makedirs('screenshots', exist_ok=True)
                screenshot_path = f"screenshots/{time.strftime('%Y-%m-%d_%H:%M')}_{user.user_id}.jpg"
                driver.save_screenshot(screenshot_path)

                with open(screenshot_path, 'rb') as photo:
                    TELEGRAM_BOT.send_photo(chat_id=data['chat_id'], photo=photo, caption="Вот ваш обещанный скриншот!")

                # Remove user from queue and commit the transaction
                await session.delete(user_queue_entry)
                await session.commit()

                logger.info(f"User {user_id} has been removed from the UserQueue.")

                return screenshot_path

            finally:
                driver.quit()

if __name__ == "__main__":
    fill_form_and_screenshot()