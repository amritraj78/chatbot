import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import os


class TestSentinel(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            from nexichat import nexichat
            nexichat.loop = self.loop
            if hasattr(nexichat, "dispatcher"):
                nexichat.dispatcher.loop = self.loop
        except Exception:
            pass

    def tearDown(self):
        self.loop.close()


    def test_disk_stats(self):
        from nexichat.modules.sentinel import get_disk_stats
        stats = get_disk_stats()
        self.assertIn("total_gb", stats)
        self.assertIn("used_gb", stats)
        self.assertIn("free_gb", stats)
        self.assertIn("percent", stats)
        self.assertGreaterEqual(stats["percent"], 0.0)

    def test_ram_stats(self):
        from nexichat.modules.sentinel import get_ram_stats
        stats = get_ram_stats()
        self.assertIn("total_mb", stats)
        self.assertIn("used_mb", stats)
        self.assertIn("percent", stats)
        self.assertGreaterEqual(stats["percent"], 0.0)

    def test_cache_cleaning(self):
        from nexichat.modules.sentinel import clean_cache, CACHE_DIR
        test_file = os.path.join(CACHE_DIR, "temp_test_sentinel.tmp")
        with open(test_file, "w") as f:
            f.write("temporary data for testing")

        self.assertTrue(os.path.exists(test_file))
        deleted, freed = clean_cache(max_age_seconds=0)
        self.assertGreaterEqual(deleted, 1)
        self.assertFalse(os.path.exists(test_file))

    @patch("nexichat.modules.sentinel.clean_cache", return_value=(5, 12.5))
    @patch("nexichat.modules.sentinel.get_disk_stats")
    def test_check_and_alert_storage_triggers_alert(self, mock_disk, mock_clean):
        from nexichat.modules import sentinel
        sentinel._last_auto_clean_report_time = 0.0
        mock_disk.return_value = {
            "total_gb": 10.0,
            "used_gb": 9.5,
            "free_gb": 0.5,
            "percent": 95.0,
        }
        mock_client = MagicMock()
        mock_client.send_message = AsyncMock()

        sentinel._reported_disk_milestones = set()
        self.loop.run_until_complete(sentinel.check_and_alert_storage(mock_client))
        mock_client.send_message.assert_called()
        sent_messages = [call[0][1] for call in mock_client.send_message.call_args_list]
        self.assertTrue(any("MILESTONE" in msg for msg in sent_messages))
        self.assertTrue(any("AUTO-CLEAN" in msg for msg in sent_messages))


if __name__ == "__main__":
    unittest.main()
