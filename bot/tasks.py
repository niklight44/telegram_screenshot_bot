import logging
import os

from celery import Celery
from celery.schedules import crontab
from selenium import webdriver
from selenium.webdriver.common.by import By
from sqlalchemy import URL
from sqlalchemy.orm import sessionmaker

from .database import UserQueue
from .database.engine import create_async_engine
from .database import User

import time
from .loggers.celery_logger import logger

postgres_url = URL.create(
        "postgresql+asyncpg",
        username=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST'),
        database=os.getenv("POSTGRES_DB"),
        port=os.getenv("POSTGRES_PORT")
    )

async_engine = create_async_engine(postgres_url)

app = Celery('tasks', broker='redis://redis:6379/0')  # Celery runs in Docker's Redis service

# Setup periodic task
app.conf.beat_schedule = {
    'fill-form-and-screenshot-every-10-minutes': {
        'task': 'tasks.fill_form_and_screenshot',
        'schedule': crontab(minute='*/10'),  # Runs every 10 minutes
    },
}
app.conf.timezone = 'UTC'

# SQLAlchemy session setup
Session = sessionmaker(bind=async_engine)
session = Session()

@app.task
def fill_form_and_screenshot():
    # Fetch user_id from UserQueue
    user_queue_entry = session.query(UserQueue).first()

    if not user_queue_entry:
        logger.error("No users found in UserQueue")
        return

    user_id = user_queue_entry.user_id

    # Fetch user data from the database
    user = session.query(User).filter_by(user_id=user_id).first()

    if not user:
        logger.error(f"No user found with ID {user_id}")
        return

    data = {
        'name': user.name,
        'surname': user.surname,
        'email': user.email,
        'phone': user.phone,
        'birthday': user.birthday.strftime('%Y-%m-%d'),  # Convert to string if necessary
        'user_id': user.user_id
    }

    logger.info(f'Filling form and making screenshot for user {user.user_id}')

    # Selenium setup (note the URL to access Selenium inside the Docker network)
    options = webdriver.ChromeOptions()
    options.headless = True  # Runs browser in the background
    driver = webdriver.Remote(command_executor='http://selenium:4444/wd/hub', options=options)

    try:
        driver.get("https://b24-iu5stq.bitrix24.site/backend_test/")

        # Fill form
        driver.find_element(By.NAME, 'name').send_keys(data['name'])
        driver.find_element(By.NAME, 'surname').send_keys(data['surname'])
        driver.find_element(By.CLASS_NAME, "b24-form-btn").click()
        time.sleep(2)
        driver.find_element(By.NAME, 'email').send_keys(data['email'])
        driver.find_element(By.NAME, 'phone').send_keys(data['phone'])
        driver.find_element(By.CLASS_NAME, "b24-form-btn").click()
        time.sleep(2)
        driver.find_element(By.NAME, 'birthday').send_keys(data['birthday'])
        # Submit form
        driver.find_element(By.NAME, 'submit').click()

        # Screenshot
        screenshot_path = f"screenshots/{time.strftime('%Y-%m-%d_%H:%M')}_{data['user_id']}.jpg"
        driver.save_screenshot(screenshot_path)

        return screenshot_path
    finally:
        driver.quit()
