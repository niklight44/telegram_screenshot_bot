import logging

logger = logging.getLogger('celery_logger')

logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('./logs/celery_logs.log')

file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

