import logging
import os

def setup_logger(
    name: str = "app",
    log_dir: str = "logs",
    log_file: str = "app.log",
    enable_console: bool = False,
    level: int = logging.DEBUG
) -> logging.Logger:
    """
    Sets up and returns a logger instance.

    Args:
        name (str): Logger name.
        log_dir (str): Directory for the log files.
        log_file (str): Log file name.
        enable_console (bool): Whether to also log to console.
        level (int): Logging level.

    Returns:
        logging.Logger: Configured logger instance.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, log_file)

    log_format = "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(funcName)s | %(message)s"

    handlers = [logging.FileHandler(log_file_path, mode="a")]
    if enable_console:
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers,
        force=True  # Ensures reconfiguration when run multiple times in testing
    )

    return logging.getLogger(name)

# Default logger instance
logger = setup_logger()
# logging.disable(logging.CRITICAL)
