import unittest
import os
import logging
from backend.app.services.logger import setup_logger

class TestLoggerSetup(unittest.TestCase):
    def setUp(self):
        self.log_dir = "test_logs"
        self.log_file = "test_app.log"
        self.log_path = os.path.join(self.log_dir, self.log_file)

        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def tearDown(self):
        # Ensure all file handlers are closed to avoid Windows file lock issues
        for logger_name in ["test_logger", "test_logger_format", "console_logger", "level_logger"]:
            logger = logging.getLogger(logger_name)
            handlers = logger.handlers[:]
            for handler in handlers:
                handler.close()
                logger.removeHandler(handler)
            logging.getLogger().handlers.clear()

        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        if os.path.exists(self.log_dir):
            os.rmdir(self.log_dir)

    def test_logger_creates_log_file(self):
        logger = setup_logger(name="test_logger", log_dir=self.log_dir, log_file=self.log_file)
        logger.info("Logger setup test")

        # Flush all handlers to ensure file write
        for handler in logger.handlers:
            handler.flush()

        self.assertTrue(os.path.exists(self.log_path))

    def test_logger_logs_correct_format(self):
        logger = setup_logger(name="test_logger_format", log_dir=self.log_dir, log_file=self.log_file)
        test_message = "This is a format test"
        logger.warning(test_message)

        for handler in logger.handlers:
            handler.flush()

        with open(self.log_path, "r") as f:
            content = f.read()

        self.assertIn("WARNING", content)
        self.assertIn(test_message, content)

    def test_logger_with_console_output(self):
        logger = setup_logger(
            name="console_logger", 
            log_dir=self.log_dir, 
            log_file=self.log_file,
            enable_console=True
        )
        logger.debug("Debug message to console and file")

        for handler in logger.handlers:
            handler.flush()

        self.assertTrue(os.path.exists(self.log_path))

    def test_logger_respects_log_level(self):
        logger = setup_logger(
            name="level_logger", 
            log_dir=self.log_dir, 
            log_file=self.log_file, 
            level=logging.ERROR
        )
        logger.warning("This should not be logged")
        logger.error("This should be logged")

        for handler in logger.handlers:
            handler.flush()

        with open(self.log_path, "r") as f:
            content = f.read()

        self.assertNotIn("This should not be logged", content)
        self.assertIn("This should be logged", content)
