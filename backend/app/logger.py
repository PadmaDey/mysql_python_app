import logging
import os

log_file_path = os.path.join("logs", "app.log")
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

log_format = "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"

ENABLE_CONSOLE_LOG = False
handlers = [logging.FileHandler(log_file_path, mode="a")]
if ENABLE_CONSOLE_LOG:
    handlers.append(logging.StreamHandler())

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    handlers=handlers,
)

logger = logging.getLogger("app")
# logging.disable(logging.CRITICAL)
