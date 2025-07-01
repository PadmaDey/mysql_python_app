import unittest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.auth.user import get_user
from backend.app.models.user import User


class TestGetUser(unittest.IsolatedAsyncioTestCase):

    async def test_user_found(self):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_user = User(id=1, name="Test", email="test@example.com", password_hash="hash")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db.execute.return_value = mock_result

        result = await get_user("test@example.com", db=mock_db)
        self.assertEqual(result, mock_user)

    async def test_user_not_found(self):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with self.assertRaises(HTTPException) as context:
            await get_user("notfound@example.com", db=mock_db)

        self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(context.exception.detail, "User not found")

    @patch("backend.app.core.auth.user.logger")
    async def test_db_error_raises_500(self, mock_logger):
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.execute.side_effect = Exception("DB Error")

        with self.assertRaises(HTTPException) as context:
            await get_user("error@example.com", db=mock_db)

        self.assertEqual(context.exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(context.exception.detail, "Internal Server Error")
        mock_logger.error.assert_called_once()
