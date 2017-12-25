import logging
import os
from logging.handlers import RotatingFileHandler

LOG_PATTERN = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: [%(filename)s] %(message)s')
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
LOG_DIR = PROJECT_DIR + "/log"

if not os.path.isdir(LOG_DIR):
    os.makedirs(LOG_DIR)

# debug logger
DEBUG_LOGGER = logging.getLogger('debug')
DEBUG_LOGGER.setLevel(logging.DEBUG)
DEBUG_FILE_HANDLER = RotatingFileHandler(LOG_DIR + "/debug.log", "a", 1000000, 1)
DEBUG_FILE_HANDLER.setFormatter(LOG_PATTERN)
DEBUG_LOGGER.addHandler(DEBUG_FILE_HANDLER)

# write in the console
STEAM_HANDLER = logging.StreamHandler()
STEAM_HANDLER.setFormatter(LOG_PATTERN)
STEAM_HANDLER.setLevel(logging.DEBUG)
DEBUG_LOGGER.addHandler(STEAM_HANDLER)
