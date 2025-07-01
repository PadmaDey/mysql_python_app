import unittest
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from sqlalchemy.orm import DeclarativeBase

from backend.app.db.database import engine, AsyncSessionLocal, Base


class TestDatabaseSetup(unittest.IsolatedAsyncioTestCase):

    def test_engine_is_async_engine(self):
        self.assertIsInstance(engine, AsyncEngine)

    def test_base_is_subclass_of_declarative_base(self):
        self.assertTrue(issubclass(Base, DeclarativeBase))

    async def test_async_session_local_returns_session(self):
        async with AsyncSessionLocal() as session:
            self.assertIsInstance(session, AsyncSession)
            self.assertFalse(session.in_transaction())  # Should not be in tx until commit/rollback
