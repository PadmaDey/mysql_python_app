import unittest
from backend.app.core.auth import password


class TestPasswordUtils(unittest.IsolatedAsyncioTestCase):

    async def test_get_password_hash_and_verify_password(self):
        plain_password = "StrongPass@123"

        # Generate hash
        hashed_password = await password.get_password_hash(plain_password)

        self.assertIsInstance(hashed_password, str)
        self.assertNotEqual(plain_password, hashed_password)

        # Verify hash works
        is_valid = await password.verify_password(plain_password, hashed_password)
        self.assertTrue(is_valid)

    async def test_verify_password_invalid(self):
        plain_password = "Password1!"
        hashed_password = await password.get_password_hash("AnotherPassword2!")

        # Should return False
        is_valid = await password.verify_password(plain_password, hashed_password)
        self.assertFalse(is_valid)
