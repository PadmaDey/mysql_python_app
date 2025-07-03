import unittest
from datetime import timedelta
from pydantic import ValidationError
from backend.app.schemas.item import Expires_delta, Token, TokenData


class TestExpiresDeltaSchema(unittest.TestCase):

    def test_default_expires_delta(self):
        data = Expires_delta()
        self.assertIsNone(data.expires_delta)

    def test_valid_expires_delta(self):
        data = Expires_delta(expires_delta=timedelta(minutes=15))
        self.assertEqual(data.expires_delta.total_seconds(), 900)


class TestTokenSchema(unittest.TestCase):

    def test_valid_token(self):
        token = Token(access_token="abc123", token_type="bearer")
        self.assertEqual(token.access_token, "abc123")
        self.assertEqual(token.token_type, "bearer")

    def test_missing_fields(self):
        with self.assertRaises(ValidationError):
            Token(access_token="abc123")  # Missing token_type


class TestTokenDataSchema(unittest.TestCase):

    def test_valid_token_data(self):
        token_data = TokenData(email="user@example.com")
        self.assertEqual(token_data.email, "user@example.com")

    def test_invalid_email_format(self):
        with self.assertRaises(ValidationError):
            TokenData(email="invalid-email")
