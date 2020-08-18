import datetime
import logging
import os
import sys

ROOT_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..')


def project_path(path):
    path = os.path.join(ROOT_FOLDER, path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


## logging
LOGGING_FORMAT = logging.Formatter(
    '[%(asctime)s:%(levelname)s:%(name)s] %(message)s', datefmt='%H:%M:%S')
LOGGING_LEVEL = logging.INFO
LOG_PATH = os.path.join(project_path('out/logs'), f'{datetime.datetime.now().isoformat()}.log')


def console_handler():
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(LOGGING_LEVEL)
    handler.setFormatter(LOGGING_FORMAT)
    return handler


logging.basicConfig(handlers=[console_handler()])
