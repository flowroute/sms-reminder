import sys
import logging
from pythonjsonlogger import jsonlogger

from settings import LOG_LEVEL


log = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
log.addHandler(handler)
log.setLevel(LOG_LEVEL)  # Default to INFO log level
