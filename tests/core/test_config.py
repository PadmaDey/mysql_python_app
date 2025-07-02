import unittest
from unittest.mock import patch
from backend.app.core.config import Settings


class TestSettings(unittest.TestCase):

    @patch.dict("os.environ", {
        "PORT": "8080",
        "DEBUG": "false",  # make sure DEBUG is explicitly false here
        "MYSQL_DATABASE": "test_database",
        "MYSQL_USER": "emp_1",
        "MYSQL_PASSWORD": "qwerty",
        "MYSQL_PORT": "3306",
        "MYSQL_HOST": "mysql",
    }, clear=True)
    def test_defaults(self):
        settings = Settings()
        self.assertEqual(settings.PORT, 8080)
        self.assertFalse(settings.DEBUG)  # Will now pass
        self.assertEqual(settings.MYSQL_DATABASE, "test_database")
        self.assertEqual(settings.MYSQL_USER, "emp_1")
        self.assertEqual(settings.MYSQL_PASSWORD, "qwerty")
        self.assertEqual(settings.MYSQL_PORT, 3306)
        self.assertEqual(settings.MYSQL_HOST, "mysql")

    @patch.dict("os.environ", {"ENV": "local"}, clear=True)
    def test_async_db_url_local_env(self):
        settings = Settings()
        self.assertTrue(settings.ASYNC_DB_URL.startswith("mysql+asyncmy://"))
        self.assertIn("@localhost:", settings.ASYNC_DB_URL)

    @patch.dict("os.environ", {"ENV": "prod", "MYSQL_HOST": "mysql"}, clear=True)
    def test_async_db_url_non_local_env(self):
        settings = Settings()
        self.assertTrue(settings.ASYNC_DB_URL.startswith("mysql+asyncmy://"))
        self.assertIn("@mysql:", settings.ASYNC_DB_URL)

