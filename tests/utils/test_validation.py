import unittest
import asyncio
from datetime import timezone
from backend.app.utils.validation import get_current_utc_time

class TestValidationUtils(unittest.TestCase):

    def test_get_current_utc_time(self):
        # Run the async function
        result = asyncio.run(get_current_utc_time())

        # Assert it's a datetime
        self.assertEqual(result.tzinfo, timezone.utc)
        self.assertTrue(result.isoformat().endswith('+00:00'))

        # Sanity check: should not be None
        self.assertIsNotNone(result)
