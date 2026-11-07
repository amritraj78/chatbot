import sys
import unittest
from unittest.mock import MagicMock

# Mock third-party libraries if they are not installed in the test environment
for mod_name in [
    "dotenv", "pymongo", "motor", "motor.motor_asyncio",
    "pyrogram", "pyrogram.enums", "pyrogram.types",
    "pyrogram.errors", "uvloop", "Abg", "speedtest", "psutil"
]:
    if mod_name not in sys.modules:
        m = MagicMock()
        m.on_message = MagicMock(return_value=lambda f: f)
        m.on_callback_query = MagicMock(return_value=lambda f: f)
        sys.modules[mod_name] = m

from nexichat.core.diagnostics import (
    validate_environment,
    explain_telegram_login_error,
    is_port_available,
    find_available_port,
)
from nexichat.core.banner import get_startup_banner


class TestCoreArchitecture(unittest.TestCase):
    def test_validate_environment_missing_token(self):
        mock_conf = MagicMock()
        mock_conf.BOT_TOKEN = None
        is_valid, report = validate_environment(mock_conf)
        self.assertFalse(is_valid)
        self.assertIn("BOT_TOKEN is MISSING", report)

    def test_validate_environment_invalid_format(self):
        mock_conf = MagicMock()
        mock_conf.BOT_TOKEN = "invalid_token_without_colon"
        mock_conf.OWNER_ID = 5423666218
        is_valid, report = validate_environment(mock_conf)
        self.assertFalse(is_valid)
        self.assertIn("BOT_TOKEN FORMAT IS INVALID", report)

    def test_validate_environment_invalid_owner_id(self):
        mock_conf = MagicMock()
        mock_conf.BOT_TOKEN = "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ123456"
        mock_conf.OWNER_ID = "not_a_number"
        is_valid, report = validate_environment(mock_conf)
        self.assertFalse(is_valid)
        self.assertIn("OWNER_ID MUST BE A NUMERIC USER ID", report)

    def test_validate_environment_success(self):
        mock_conf = MagicMock()
        mock_conf.BOT_TOKEN = "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ123456"
        mock_conf.OWNER_ID = 5423666218
        mock_conf.API_ID = "123456"
        mock_conf.API_HASH = "abcdef123456"
        is_valid, report = validate_environment(mock_conf)
        self.assertTrue(is_valid)
        self.assertIsNone(report)

    def test_explain_telegram_login_error(self):
        class MockTokenError(Exception):
            pass
        MockTokenError.__name__ = "AccessTokenInvalid"

        msg = explain_telegram_login_error(Exception("AccessTokenInvalid: token expired"))
        self.assertIn("BOT_TOKEN HAS BEEN REVOKED", msg)

    def test_port_finder(self):
        self.assertTrue(is_port_available(18889))
        port = find_available_port(18888)
        self.assertIsInstance(port, int)
        self.assertTrue(port >= 18888)

    def test_startup_banner_render(self):
        banner = get_startup_banner(
            username="TestReactionBot",
            owner_id=5423666218,
            db_mode="In-Memory RAM Engine",
            port=8000,
            workers=8
        )
        self.assertIn("TestReactionBot", banner)
        self.assertIn("5423666218", banner)
        self.assertIn("Workers: 8", banner)
        self.assertIn("Amrit Raj", banner)


if __name__ == "__main__":
    unittest.main()
