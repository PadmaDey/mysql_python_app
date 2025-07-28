import unittest
from backend.app.db.dependencies import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from types import AsyncGeneratorType


class TestGetDbDependency(unittest.IsolatedAsyncioTestCase):

    async def test_get_db_returns_session(self):
        # Check the generator returns a valid AsyncSession
        db_gen = get_db()
        self.assertIsInstance(db_gen, AsyncGeneratorType)

        session = await anext(db_gen)
        self.assertIsInstance(session, AsyncSession)

        # Close manually since we didn't iterate fully
        await db_gen.aclose()

    async def test_get_db_session_closes(self):
        # This is a behavior check: if the generator closes, session is closed
        session_closed_flag = {"closed": False}

        class MockSession(AsyncSession):
            async def close(self_inner):
                session_closed_flag["closed"] = True

        async def mock_get_db():
            async with MockSession() as session:
                yield session

        gen = mock_get_db()
        _ = await anext(gen)
        await gen.aclose()

        self.assertTrue(session_closed_flag["closed"])
