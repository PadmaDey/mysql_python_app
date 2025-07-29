import pytest
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from backend.app.models.jti_blacklist import JTIBlacklist

pytestmark = pytest.mark.asyncio


class TestJTIBlacklistModel:
    async def _cleanup_jti(self, session, jti_token: str):
        """Remove any JTI records to ensure a clean slate for tests."""
        await session.execute(delete(JTIBlacklist).where(JTIBlacklist.jti == jti_token))
        await session.commit()

    async def test_jti_unique_constraint(self, db_session):
        """
        Verify that JTIs must be unique.
        Attempts to insert a duplicate JTI should raise an IntegrityError.
        """
        jti_token = "duplicate-jti-9999"

        # Clean up any leftovers first
        await self._cleanup_jti(db_session, jti_token)

        # Insert the first record (should succeed)
        first_entry = JTIBlacklist(jti=jti_token)
        db_session.add(first_entry)
        await db_session.commit()

        # Insert a duplicate (should raise IntegrityError)
        duplicate_entry = JTIBlacklist(jti=jti_token)
        db_session.add(duplicate_entry)

        with pytest.raises(IntegrityError):
            await db_session.commit()

        # IMPORTANT: Rollback before any new DB operations
        await db_session.rollback()

        # Final cleanup to leave DB state clean
        await self._cleanup_jti(db_session, jti_token)

    async def test_insert_and_retrieve_jti(self, db_session):
        """
        Test that a JTI can be added and queried successfully.
        """
        jti_token = "test-jti-1234"

        # Clean up first
        await self._cleanup_jti(db_session, jti_token)

        # Add a new record
        entry = JTIBlacklist(jti=jti_token)
        db_session.add(entry)
        await db_session.commit()

        # Fetch it back
        result = await db_session.get(JTIBlacklist, entry.id)
        assert result is not None
        assert result.jti == jti_token

        # Clean up
        await self._cleanup_jti(db_session, jti_token)
