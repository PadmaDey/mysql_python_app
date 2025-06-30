import unittest
from backend.app.utils.secret_key import generate_secret_key

class TestSecretKey(unittest.TestCase):

    def test_generate_secret_key_default_length(self):
        key = generate_secret_key()
        self.assertIsInstance(key, str)
        self.assertGreaterEqual(len(key), 32)  # token_urlsafe may generate longer

    def test_generate_secret_key_custom_length(self):
        key = generate_secret_key(64)
        self.assertIsInstance(key, str)
        self.assertGreaterEqual(len(key), 64)
