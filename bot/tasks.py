import logging

from celery import Celery
from celery.schedules import crontab
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import time
import os
from loggers.celery_logger import logger

app = Celery('tasks', broker='redis://redis:6379/0')  # Celery runs in Docker's Redis service

# Setup periodic task
app.conf.beat_schedule = {
    'fill-form-and-screenshot-every-10-minutes': {
        'task': 'tasks.fill_form_and_screenshot',
        'schedule': crontab(minute='*/10'),  # Runs every 10 minutes
        'args': ({'name': 'John', 'surname': 'Doe', 'email': 'john@example.com', 'phone': '1234567890', 'birthday': '1990-01-01', 'user_id': 1},)
    },
}
app.conf.timezone = 'UTC'

@app.task
def fill_form_and_screenshot(data):
    logger.info('Filling form and making screenshot')
    # Selenium setup (note the URL to access Selenium inside the Docker network)
    options = webdriver.ChromeOptions()
    options.headless = True  # Run in the background
    driver = webdriver.Remote(command_executor='http://selenium:4444/wd/hub', options=options)

    try:
        driver.get("https://b24-iu5stq.bitrix24.site/backend_test/")

        # Fill form
        driver.find_element_by_name('name').send_keys(data['name'])
        driver.find_element_by_name('surname').send_keys(data['surname'])
        driver.find_element(By.CLASS_NAME, "b24-form-btn")
        time.sleep(2)
        driver.find_element_by_name('email').send_keys(data['email'])
        driver.find_element_by_name('phone').send_keys(data['phone'])
        driver.find_element(By.CLASS_NAME, "b24-form-btn")
        time.sleep(2)
        driver.find_element_by_name('birthday').send_keys(data['birthday'])
        # Submit form
        driver.find_element_by_name('submit').click()

        # Screenshot
        screenshot_path = f"screenshots/{time.strftime('%Y-%m-%d_%H:%M')}_{data['user_id']}.jpg"
        driver.save_screenshot(screenshot_path)

        return screenshot_path
    finally:
        driver.quit()


@app.task
def save_user_data(data):
    """Saves user data to DB tables (queue and user)"""
    ...
