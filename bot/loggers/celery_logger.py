import logging
import os

log_folder = os.getenv('LOG_FOLDER')
logger = logging.getLogger('celery_logger')

logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(f'{log_folder}/celery_logs.log')

file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

