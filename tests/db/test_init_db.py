import unittest
from unittest.mock import AsyncMock, patch
from backend.app.db import initialize_db


class TestInitializeDB(unittest.IsolatedAsyncioTestCase):

    @patch("backend.app.db.engine", autospec=True)
    async def test_initialize_db_success(self, mock_engine):
        mock_conn_ctx = AsyncMock()
        mock_conn = AsyncMock()
        mock_conn_ctx.__aenter__.return_value = mock_conn
        mock_engine.begin.return_value = mock_conn_ctx

        await initialize_db()

        mock_engine.begin.assert_called_once()
        mock_conn.run_sync.assert_called_once()
