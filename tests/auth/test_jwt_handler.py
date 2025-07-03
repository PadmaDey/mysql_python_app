import unittest
from datetime import timedelta
from jose import jwt
from uuid import uuid4, UUID
import os

from sqlalchemy import select, delete

from backend.app.auth import jwt_handler
from backend.app.utils.validation import get_current_utc_time
from backend.app.models.jti_blacklist import JTIBlacklist
from backend.app.db.database import AsyncSessionLocal

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


class TestJWTHandler(unittest.IsolatedAsyncioTestCase):

    async def test_create_and_decode_access_token(self):
        data = {"email": "test@example.com"}
        token = await jwt_handler.create_access_token(data)

        self.assertIsInstance(token, str)

        decoded = await jwt_handler.decode_access_token(token)
        self.assertEqual(decoded["email"], "test@example.com")
        self.assertIn("exp", decoded)
        self.assertIn("jti", decoded)

        try:
            UUID(decoded["jti"])
        except ValueError:
            self.fail("Invalid UUID format in 'jti'")

    async def test_create_token_with_expiry(self):
        data = {"email": "exp@test.com"}
        expire_in = timedelta(minutes=5)
        token = await jwt_handler.create_access_token(data, expires_delta=expire_in)

        decoded = await jwt_handler.decode_access_token(token)
        expected_exp = (await get_current_utc_time()).timestamp() + 300
        self.assertTrue(abs(decoded["exp"] - expected_exp) < 60)

    async def test_decode_invalid_token(self):
        invalid_token = "this.is.not.valid"
        decoded = await jwt_handler.decode_access_token(invalid_token)
        self.assertIsNone(decoded)

    async def test_is_token_blacklisted_false(self):
        async with AsyncSessionLocal() as db:
            result = await jwt_handler.is_token_blacklisted("non-existent-jti", db)
            self.assertFalse(result)

    async def test_is_token_blacklisted_true(self):
        jti = str(uuid4())
        async with AsyncSessionLocal() as db:
            # Ensure clean state
            await db.execute(delete(JTIBlacklist).where(JTIBlacklist.jti == jti))
            await db.commit()

            # Insert
            db.add(JTIBlacklist(jti=jti))
            await db.commit()

            # Verify blacklist detection
            result = await jwt_handler.is_token_blacklisted(jti, db)
            self.assertTrue(result)

            # Cleanup
            await db.execute(delete(JTIBlacklist).where(JTIBlacklist.jti == jti))
            await db.commit()
