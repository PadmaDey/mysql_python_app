import unittest
from unittest.mock import patch, MagicMock
from backend.app.db import connection


class TestDBConnection(unittest.TestCase):

    @patch("backend.app.db.connection.connect")
    def test_connect_to_db_success(self, mock_connect):
        # Setup
        mock_conn = MagicMock()
        mock_conn.is_connected.return_value = True
        mock_connect.return_value = mock_conn

        # Call
        result = connection.connect_to_db()

        # Assert
        mock_connect.assert_called_once()
        self.assertEqual(result, mock_conn)

    @patch("backend.app.db.connection.connect")
    def test_connect_to_db_failure(self, mock_connect):
        # Raise exception on connect
        mock_connect.side_effect = Exception("Connection failed")

        with self.assertRaises(Exception) as ctx:
            connection.connect_to_db()
        
        self.assertIn("Connection failed", str(ctx.exception))

    def test_get_cursor_success(self):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        cursor_result = connection.get_cursor(mock_conn)
        self.assertEqual(cursor_result, mock_cursor)

    def test_get_cursor_failure(self):
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("Cursor error")

        with self.assertRaises(Exception) as ctx:
            connection.get_cursor(mock_conn)
        
        self.assertIn("Cursor error", str(ctx.exception))
