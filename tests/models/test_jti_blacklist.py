import unittest
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from backend.app.models.jti_blacklist import JTIBlacklist
from backend.app.db.database import AsyncSessionLocal


class TestJTIBlacklistModel(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.db = AsyncSessionLocal()
        self.session = await self.db.__aenter__()

    async def asyncTearDown(self):
        await self.db.__aexit__(None, None, None)

    async def _cleanup_jti(self, jti_token: str):
        await self.session.execute(
            delete(JTIBlacklist).where(JTIBlacklist.jti == jti_token)
        )
        await self.session.commit()

    async def test_add_jti(self):
        jti_token = "test-jti-12345"

        await self._cleanup_jti(jti_token)

        jti_entry = JTIBlacklist(jti=jti_token)
        self.session.add(jti_entry)
        await self.session.commit()

        result = await self.session.execute(
            select(JTIBlacklist).where(JTIBlacklist.jti == jti_token)
        )
        found_entry = result.scalar_one_or_none()

        self.assertIsNotNone(found_entry)
        self.assertEqual(found_entry.jti, jti_token)
        self.assertIsNotNone(found_entry.created_at)

    async def test_jti_unique_constraint(self):
        jti_token = "duplicate-jti-9999"

        await self._cleanup_jti(jti_token)

        entry1 = JTIBlacklist(jti=jti_token)
        entry2 = JTIBlacklist(jti=jti_token)

        self.session.add(entry1)
        await self.session.commit()

        self.session.add(entry2)
        with self.assertRaises(IntegrityError):
            await self.session.commit()
