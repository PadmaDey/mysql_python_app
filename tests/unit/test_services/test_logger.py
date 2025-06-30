import unittest
from backend.app.services.logger import setup_logger

class TestLoggerSetup(unittest.TestCase):

    def test_logger_creation(self):
        logger = setup_logger("test_logger", enable_console=False)
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test_logger")
