import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import os


class TestNewFeatures(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_nickname_storage(self):
        from nexichat.database import chatbot
        self.loop.run_until_complete(chatbot.save_user_nickname(999888, "Sweetie"))
        nick = self.loop.run_until_complete(chatbot.get_user_nickname(999888))
        self.assertEqual(nick, "Sweetie")

    def test_welcome_status(self):
        from nexichat.database import reactions
        self.loop.run_until_complete(reactions.set_welcome_enabled(-1001234, False))
        status = self.loop.run_until_complete(reactions.is_welcome_enabled(-1001234))
        self.assertFalse(status)

        self.loop.run_until_complete(reactions.set_welcome_enabled(-1001234, True))
        status = self.loop.run_until_complete(reactions.is_welcome_enabled(-1001234))
        self.assertTrue(status)

    @patch("nexichat.modules.helpers.media_gen._media_session.get")
    @patch("nexichat.modules.helpers.media_gen._media_session.post")
    def test_generate_voice_file(self, mock_post, mock_get):
        from nexichat.modules.helpers.media_gen import generate_voice_file
        # Mock Polly post failing over or succeeding
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {"speak_url": "https://streamlabs.com/polly/audio.mp3"}
        mock_post.return_value = mock_post_resp

        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.content = b"a" * 1024
        mock_get.return_value = mock_get_resp

        filepath = generate_voice_file("Namaste aap kaise hain?", "hi")
        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith(".mp3"))
        if os.path.exists(filepath):
            os.remove(filepath)

    @patch("nexichat.modules.helpers.media_gen._media_session.get")
    def test_generate_ai_image(self, mock_get):
        from nexichat.modules.helpers.media_gen import generate_ai_image
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.content = b"a" * 3000
        mock_get.return_value = mock_resp

        filepath = generate_ai_image("cute baby anime robot")
        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith(".jpg"))
        if os.path.exists(filepath):
            os.remove(filepath)

    def test_games_commands(self):
        from nexichat.modules import games
        mock_msg = MagicMock()
        mock_msg.reply_text = AsyncMock()

        self.loop.run_until_complete(games.truth_command(MagicMock(), mock_msg))
        mock_msg.reply_text.assert_called_once()
        self.assertIn("TRUTH", mock_msg.reply_text.call_args[0][0])

        mock_msg.reply_text.reset_mock()
        self.loop.run_until_complete(games.dare_command(MagicMock(), mock_msg))
        mock_msg.reply_text.assert_called_once()
        self.assertIn("DARE", mock_msg.reply_text.call_args[0][0])

        mock_msg.reply_text.reset_mock()
        self.loop.run_until_complete(games.toss_command(MagicMock(), mock_msg))
        mock_msg.reply_text.assert_called_once()
        self.assertIn("sɪᴋᴋᴀ", mock_msg.reply_text.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
