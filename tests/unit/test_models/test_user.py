import unittest
from sqlalchemy import select
from backend.app.models.user import User
from backend.app.db.database import AsyncSessionLocal
from tests.conftest import register_test_email

class TestUserModel(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.db = AsyncSessionLocal()
        self.session = await self.db.__aenter__()

    async def asyncTearDown(self):
        await self.db.__aexit__(None, None, None)

    async def test_create_user(self):
        email = "unittestuser@example.com"
        await register_test_email(email)

        user = User(
            name="Unit User",
            email=email,
            phone_no=1234567890,
            password_hash="hashed_pass"
        )
        self.session.add(user)
        await self.session.commit()

        result = await self.session.execute(select(User).where(User.email == email))
        saved_user = result.scalar_one_or_none()

        self.assertIsNotNone(saved_user)
        self.assertEqual(saved_user.name, "Unit User")
        self.assertEqual(saved_user.phone_no, 1234567890)
        self.assertEqual(saved_user.password_hash, "hashed_pass")
        self.assertIsNotNone(saved_user.created_at)
        self.assertIsNotNone(saved_user.updated_at)

    async def test_email_unique_constraint(self):
        email = "duplicateuser@example.com"
        await register_test_email(email)

        user1 = User(
            name="First User",
            email=email,
            password_hash="hash1"
        )
        user2 = User(
            name="Second User",
            email=email,
            password_hash="hash2"
        )

        self.session.add(user1)
        await self.session.commit()

        self.session.add(user2)
        with self.assertRaises(Exception):  # IntegrityError or DB-specific
            await self.session.commit()
