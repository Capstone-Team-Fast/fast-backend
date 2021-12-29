import datetime
import logging
import os
import re

from backend import settings
from routing import constant

LOG_DIR = os.path.join(settings.BASE_DIR, 'routing\\logs')
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def log():
    def get_filename():
        log_filename = f'{datetime.datetime.now().strftime(constant.DATETIME_FORMAT)}'
        log_filename = re.sub('[^a-zA-Z\d]', '', log_filename)
        log_filename = log_filename + '.log'
        return log_filename

    filename = os.path.join(LOG_DIR, get_filename())
    logging.basicConfig(level=logging.INFO,
                        filename=filename,
                        filemode='w',
                        format='%(asctime)s %(name)s> %(levelname)s %(message)s')


log()
