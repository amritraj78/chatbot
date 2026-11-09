import os
import json
import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock, patch

try:
    from tests.mock_helper import setup_mocks
    setup_mocks()
except ImportError:
    import mock_helper
    mock_helper.setup_mocks()

from nexichat.core.instagram_bot import (
    InstagramChatbotClient,
    InstagramUserbot,
    start_instagram_bot,
    stop_instagram_bot,
    SESSION_FILE_PATH,
)


class TestInstagramBot(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.test_session_file = os.path.join("cache", "test_ig_session.json")
        if os.path.exists(self.test_session_file):
            try:
                os.remove(self.test_session_file)
            except OSError:
                pass

    def tearDown(self):
        if os.path.exists(self.test_session_file):
            try:
                os.remove(self.test_session_file)
            except OSError:
                pass
        self.loop.close()

    def test_client_send_direct_text_thread(self):
        client = InstagramChatbotClient.__new__(InstagramChatbotClient)
        client.uuid = "mock-uuid-1234"
        client._call_api = MagicMock(return_value={"status": "ok"})

        res = client.send_direct_text(text="Hello from test", thread_id="thread_999")
        self.assertEqual(res["status"], "ok")
        client._call_api.assert_called_once()
        args, kwargs = client._call_api.call_args
        self.assertEqual(args[0], "direct_v2/threads/broadcast/text/")
        params = kwargs.get("params", {})
        self.assertEqual(params["thread_ids"], "[thread_999]")
        self.assertEqual(params["text"], "Hello from test")

    def test_client_send_direct_text_recipient_user(self):
        client = InstagramChatbotClient.__new__(InstagramChatbotClient)
        client.uuid = "mock-uuid-1234"
        client._call_api = MagicMock(return_value={"status": "ok"})

        res = client.send_direct_text(text="Hi user", recipient_user_id="user_12345")
        self.assertEqual(res["status"], "ok")
        args, kwargs = client._call_api.call_args
        params = kwargs.get("params", {})
        self.assertEqual(params["recipient_users"], "[[user_12345]]")
        self.assertEqual(params["text"], "Hi user")

    def test_client_send_direct_text_validation_error(self):
        client = InstagramChatbotClient.__new__(InstagramChatbotClient)
        client.uuid = "mock-uuid-1234"
        with self.assertRaises(ValueError):
            client.send_direct_text(text="Invalid call")

    def test_client_inbox_and_thread_endpoints(self):
        client = InstagramChatbotClient.__new__(InstagramChatbotClient)
        client._call_api = MagicMock(return_value={"status": "ok"})

        client.get_inbox_threads(cursor="cursor_abc")
        client._call_api.assert_called_with("direct_v2/inbox/", query={"cursor": "cursor_abc"})

        client.get_thread_detail("th_123", cursor="cur_xyz")
        client._call_api.assert_called_with("direct_v2/threads/th_123/", query={"cursor": "cur_xyz"})

    def test_session_save_and_load(self):
        userbot = InstagramUserbot(
            username="test_user",
            password="test_password",
            session_file=self.test_session_file,
        )

        mock_client = MagicMock()
        mock_client.settings = {
            "uuid": "test-uuid",
            "device_id": "test-device",
            "cookie": "session_id=123",
        }

        userbot.save_session_callback(mock_client)
        self.assertTrue(os.path.exists(self.test_session_file))

        loaded = userbot.load_cached_settings()
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["cookie"], "session_id=123")
        self.assertEqual(loaded["uuid"], "test-uuid")

    @patch("nexichat.core.instagram_bot.InstagramChatbotClient")
    def test_login_with_cached_settings(self, mock_client_cls):
        userbot = InstagramUserbot(
            username="test_user",
            password="test_password",
            session_file=self.test_session_file,
        )
        # Create cached session file
        with open(self.test_session_file, "w") as f:
            json.dump({"cookie": "test_cookie", "uuid": "u123"}, f)

        mock_client_instance = MagicMock()
        mock_client_cls.return_value = mock_client_instance

        success = userbot.login()
        self.assertTrue(success)
        mock_client_cls.assert_called_with(
            "test_user", "test_password", settings={"cookie": "test_cookie", "uuid": "u123"}
        )

    @patch("nexichat.core.instagram_bot.InstagramChatbotClient")
    def test_login_fallback_on_expired_cached_session(self, mock_client_cls):
        from nexichat.core.instagram_bot import ClientCookieExpiredError

        userbot = InstagramUserbot(
            username="test_user",
            password="test_password",
            session_file=self.test_session_file,
        )
        with open(self.test_session_file, "w") as f:
            json.dump({"cookie": "expired_cookie"}, f)

        mock_client_instance = MagicMock()
        # First call with settings raises expired error, second call without settings succeeds
        mock_client_cls.side_effect = [
            ClientCookieExpiredError("Expired"),
            mock_client_instance,
        ]

        success = userbot.login()
        self.assertTrue(success)
        self.assertEqual(mock_client_cls.call_count, 2)

    @patch("nexichat.core.instagram_bot.generate_conversational_response", new_callable=AsyncMock)
    def test_worker_loop_replies_to_dm(self, mock_ai_response):
        mock_ai_response.return_value = "Sweet AI reply!"

        userbot = InstagramUserbot(
            username="test_user",
            password="test_password",
            poll_interval=0.02,
            session_file=self.test_session_file,
        )

        mock_client = MagicMock()
        mock_client.authenticated_user_id = "99999"  # Our bot's ID

        empty_inbox = {"inbox": {"threads": []}}
        new_dm_inbox = {
            "inbox": {
                "threads": [
                    {
                        "thread_id": "thread_abc",
                        "users": [
                            {"pk": 11111, "username": "friend_user", "full_name": "Friend"}
                        ],
                        "items": [
                            {
                                "item_id": "msg_001",
                                "user_id": 11111,  # Sent by friend
                                "item_type": "text",
                                "text": "Hello bot!",
                            }
                        ],
                    }
                ]
            }
        }
        # First call is seeding, subsequent calls are the loop
        mock_client.get_inbox_threads.side_effect = [empty_inbox, new_dm_inbox, new_dm_inbox, new_dm_inbox]
        mock_client.send_direct_text = MagicMock(return_value={"status": "ok"})
        userbot.client = mock_client

        async def run_test():
            userbot.is_running = True
            worker_task = asyncio.create_task(userbot.worker_loop())
            await asyncio.sleep(0.1)
            userbot.is_running = False
            await worker_task

        self.loop.run_until_complete(run_test())

        # Check that AI was called with the message text and sender name
        mock_ai_response.assert_called_with(
            user_text="Hello bot!",
            user_name="Friend",
            user_id=11111,
        )
        # Check that direct_send was called to reply
        mock_client.send_direct_text.assert_called_with(
            text="Sweet AI reply!",
            thread_id="thread_abc",
        )
        self.assertIn("msg_001", userbot.seen_message_ids)

    def test_worker_loop_ignores_own_messages(self):
        userbot = InstagramUserbot(
            username="test_user",
            password="test_password",
            poll_interval=0.02,
            session_file=self.test_session_file,
        )
        mock_client = MagicMock()
        mock_client.authenticated_user_id = "99999"
        empty_inbox = {"inbox": {"threads": []}}
        own_msg_inbox = {
            "inbox": {
                "threads": [
                    {
                        "thread_id": "thread_abc",
                        "users": [],
                        "items": [
                            {
                                "item_id": "msg_002",
                                "user_id": 99999,  # Sent by ourselves!
                                "item_type": "text",
                                "text": "My own message",
                            }
                        ],
                    }
                ]
            }
        }
        mock_client.get_inbox_threads.side_effect = [empty_inbox, own_msg_inbox, own_msg_inbox]
        mock_client.send_direct_text = MagicMock()
        userbot.client = mock_client

        async def run_test():
            userbot.is_running = True
            worker_task = asyncio.create_task(userbot.worker_loop())
            await asyncio.sleep(0.1)
            userbot.is_running = False
            await worker_task

        self.loop.run_until_complete(run_test())

    @patch("nexichat.core.instagram_bot.config")
    def test_start_instagram_bot_when_disabled(self, mock_config):
        mock_config.INSTAGRAM_BOT_ENABLED = False

        res = self.loop.run_until_complete(start_instagram_bot())
        self.assertIsNone(res)


if __name__ == "__main__":
    unittest.main()
