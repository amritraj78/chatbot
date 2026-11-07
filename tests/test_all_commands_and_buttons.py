import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from pyrogram import Client
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import (
    CallbackQuery,
    Chat,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)

# Mock Pyrogram decorators to avoid event loop errors during test loading
from nexichat import nexichat
nexichat.on_message = MagicMock(return_value=lambda f: f)
nexichat.on_callback_query = MagicMock(return_value=lambda f: f)
Client.on_message = MagicMock(return_value=lambda f: f)
Client.on_callback_query = MagicMock(return_value=lambda f: f)


class TestAllCommandsAndButtons(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        # Mock Pyrogram Client
        self.client = MagicMock()
        me_user = MagicMock(spec=User)
        me_user.id = 123456789
        me_user.first_name = "Anshika Bot"
        me_user.username = "Reactions_rebot"
        self.client.me = me_user
        self.client.get_me = AsyncMock(return_value=me_user)
        self.client.get_users = AsyncMock(return_value=me_user)

        # Mock User
        self.user = MagicMock(spec=User)
        self.user.id = 987654321
        self.user.first_name = "Raj"
        self.user.mention = "[Raj](tg://user?id=987654321)"
        self.user.username = "raj_dev"
        self.user.dc_id = 4

        # Mock Chat
        self.chat = MagicMock(spec=Chat)
        self.chat.id = -1001987654321
        self.chat.title = "Test Group"
        self.chat.username = "testgroup"
        self.chat.type = ChatType.SUPERGROUP

        # Mock Message
        self.message = MagicMock(spec=Message)
        self.message.id = 101
        self.message.from_user = self.user
        self.message.chat = self.chat
        self.message.text = "/id"
        self.message.command = ["id"]
        self.message.link = "https://t.me/c/123/101"
        self.message.forward_from_chat = None
        self.message.reply_to_message = None
        self.message.reply_text = AsyncMock()
        self.message.reply = AsyncMock()
        self.message.reply_photo = AsyncMock()
        self.message.delete = AsyncMock()
        self.message.edit_text = AsyncMock()

    def tearDown(self):
        self.loop.close()

    def test_inline_keyboards_structure(self):
        """Verify all predefined inline keyboards in modules and mplugin have valid button rows."""
        from nexichat.modules.helpers import inline as m_inline
        from nexichat.mplugin.helpers import inline as p_inline

        keyboards = [
            ("START_BOT", m_inline.START_BOT),
            ("DEV_OP", m_inline.DEV_OP),
            ("PNG_BTN", m_inline.PNG_BTN),
            ("BACK", m_inline.BACK),
            ("HELP_BTN", m_inline.HELP_BTN),
            ("CLOSE_BTN", m_inline.CLOSE_BTN),
            ("CHATBOT_ON", m_inline.CHATBOT_ON),
            ("MUSIC_BACK_BTN", m_inline.MUSIC_BACK_BTN),
            ("S_BACK", m_inline.S_BACK),
            ("CHATBOT_BACK", m_inline.CHATBOT_BACK),
            ("HELP_START", m_inline.HELP_START),
            ("HELP_BUTN", m_inline.HELP_BUTN),
            ("ABOUT_BTN", m_inline.ABOUT_BTN),
            ("P_START_BOT", p_inline.START_BOT),
            ("P_DEV_OP", p_inline.DEV_OP),
            ("P_PNG_BTN", p_inline.PNG_BTN),
            ("P_BACK", p_inline.BACK),
            ("P_HELP_BTN", p_inline.HELP_BTN),
            ("P_CLOSE_BTN", p_inline.CLOSE_BTN),
            ("P_CHATBOT_ON", p_inline.CHATBOT_ON),
            ("P_MUSIC_BACK_BTN", p_inline.MUSIC_BACK_BTN),
            ("P_S_BACK", p_inline.S_BACK),
            ("P_CHATBOT_BACK", p_inline.CHATBOT_BACK),
            ("P_HELP_START", p_inline.HELP_START),
            ("P_HELP_BUTN", p_inline.HELP_BUTN),
            ("P_ABOUT_BTN", p_inline.ABOUT_BTN),
        ]

        for name, kb in keyboards:
            self.assertIsInstance(kb, list, f"{name} is not a list")
            for row in kb:
                self.assertIsInstance(row, list, f"{name} row is not a list")
                for btn in row:
                    self.assertIsInstance(btn, InlineKeyboardButton, f"{name} contains non-button")
                    self.assertTrue(bool(btn.text), f"{name} button has empty text")
                    self.assertTrue(bool(btn.callback_data or btn.url), f"{name} button missing action")

    def test_callback_navigation_handlers(self):
        """Test all navigation callback queries in callback.py."""
        from nexichat.modules import callback as m_cb
        from nexichat.mplugin import callback as p_cb

        nav_callbacks = [
            "HELP",
            "CLOSE",
            "BACK",
            "SBACK",
            "ABOUT",
            "ADMINS",
            "HELP_GAMES",
            "HELP_GROUP",
            "TOOLS_DATA",
            "BACK_HELP",
            "CHATBOT_BACK",
            "CHATBOT_CMD",
            "AI_CHATBOT_CMD",
            "soon",
        ]

        for data in nav_callbacks:
            # Test modules callback
            query = MagicMock(spec=CallbackQuery)
            query.data = data
            query.from_user = self.user
            query.message = self.message
            query.answer = AsyncMock()

            self.loop.run_until_complete(m_cb.cb_handler(self.client, query))
            query.answer.assert_called()

            # Test mplugin callback
            query_p = MagicMock(spec=CallbackQuery)
            query_p.data = data
            query_p.from_user = self.user
            query_p.message = self.message
            query_p.answer = AsyncMock()

            self.loop.run_until_complete(p_cb.cb_handler(self.client, query_p))
            query_p.answer.assert_called()

    def test_security_buttons_callback(self):
        """Test anti-link and anti-spam toggle buttons in security.py."""
        from nexichat.modules import security as m_sec
        from nexichat.mplugin import security as p_sec

        for action in ["sec_toggle_antilink", "sec_toggle_antispam"]:
            query = MagicMock(spec=CallbackQuery)
            query.data = action
            query.from_user = self.user
            query.message = self.message
            query.answer = AsyncMock()

            # Mock admin status
            member = MagicMock()
            member.status = ChatMemberStatus.ADMINISTRATOR
            self.client.get_chat_member = AsyncMock(return_value=member)

            with patch("nexichat.modules.security.is_antilink_enabled", AsyncMock(return_value=False)), \
                 patch("nexichat.modules.security.set_antilink_enabled", AsyncMock()), \
                 patch("nexichat.modules.security.is_antispam_enabled", AsyncMock(return_value=False)), \
                 patch("nexichat.modules.security.set_antispam_enabled", AsyncMock()):
                self.loop.run_until_complete(m_sec.security_callback_handler(self.client, query))
                query.answer.assert_called()

            # Test mplugin
            with patch("nexichat.mplugin.security.is_antilink_enabled", AsyncMock(return_value=False)), \
                 patch("nexichat.mplugin.security.set_antilink_enabled", AsyncMock()), \
                 patch("nexichat.mplugin.security.is_antispam_enabled", AsyncMock(return_value=False)), \
                 patch("nexichat.mplugin.security.set_antispam_enabled", AsyncMock()):
                query_p = MagicMock(spec=CallbackQuery)
                query_p.data = action
                query_p.from_user = self.user
                query_p.message = self.message
                query_p.answer = AsyncMock()
                self.loop.run_until_complete(p_sec.security_callback_handler(self.client, query_p))
                query_p.answer.assert_called()

    def test_chatbot_toggle_and_api_buttons(self):
        """Test chatbot enable/disable and api usage refresh buttons."""
        from nexichat.modules import chatbot as m_chat
        from nexichat.mplugin import chatbot as p_chat

        for action in ["cb_enable_chatbot", "cb_disable_chatbot"]:
            query = MagicMock(spec=CallbackQuery)
            query.data = action
            query.from_user = self.user
            query.message = self.message
            query.answer = AsyncMock()

            member = MagicMock()
            member.status = ChatMemberStatus.ADMINISTRATOR
            self.client.get_chat_member = AsyncMock(return_value=member)

            with patch("nexichat.modules.chatbot.set_chatbot_enabled", AsyncMock()), \
                 patch("nexichat.modules.chatbot.is_chatbot_enabled", AsyncMock(return_value=True)):
                self.loop.run_until_complete(m_chat.chatbot_callback_handler(self.client, query))
                query.answer.assert_called()

        # Test refresh api usage button
        query_api = MagicMock(spec=CallbackQuery)
        query_api.data = "cb_refresh_api_usage"
        query_api.from_user = self.user
        query_api.message = self.message
        query_api.answer = AsyncMock()

        with patch("nexichat.modules.chatbot.OWNER_ID", str(self.user.id)), \
             patch("nexichat.modules.chatbot.format_api_usage_dashboard", AsyncMock(return_value="API Dashboard")):
            self.loop.run_until_complete(m_chat.api_usage_callback_handler(self.client, query_api))
            query_api.answer.assert_called()

    def test_games_proposal_buttons(self):
        """Test accept and reject buttons for proposals."""
        from nexichat.modules import games as m_games

        proposer_id = 111222
        target_id = self.user.id

        for act in ["acc", "rej"]:
            query = MagicMock(spec=CallbackQuery)
            query.data = f"prop_{act}_{proposer_id}_{target_id}"
            query.from_user = self.user
            query.message = self.message
            query.answer = AsyncMock()

            self.loop.run_until_complete(m_games.propose_callback_handler(self.client, query))
            self.message.edit_text.assert_called()

    def test_sentinel_diagnostic_buttons(self):
        """Test Sentinel diagnostic & cache cleaner buttons."""
        from nexichat.modules import sentinel as m_sentinel

        for act in ["sentinel_clean_cache", "sentinel_refresh", "sentinel_info_clean"]:
            query = MagicMock(spec=CallbackQuery)
            query.data = act
            query.from_user = self.user
            query.message = self.message
            query.answer = AsyncMock()

            with patch("nexichat.modules.sentinel.OWNER_ID", str(self.user.id)), \
                 patch("nexichat.modules.sentinel.clean_cache", return_value=(2, 0.5)), \
                 patch("nexichat.modules.sentinel.get_disk_stats", return_value={"total_gb": 100.0, "used_gb": 50.0, "free_gb": 50.0, "percent": 50.0}), \
                 patch("nexichat.modules.sentinel.get_ram_stats", return_value={"total_mb": 512.0, "used_mb": 200.0, "free_mb": 312.0, "percent": 39.0}), \
                 patch("nexichat.modules.sentinel.get_cache_size", return_value=(0, 0.0)):
                self.loop.run_until_complete(m_sentinel.sentinel_callback_handler(self.client, query))
                query.answer.assert_called()

    def test_essential_commands_execution(self):
        """Test that all primary user commands execute without exception."""
        from nexichat.modules import start, ping, stats, security, reaction, games, welcome, afk, tagall

        # /start
        self.loop.run_until_complete(start.start_message(self.client, self.message))
        self.message.reply_text.assert_called()

        # /help
        self.message.reply_text.reset_mock()
        self.loop.run_until_complete(start.help_command(self.client, self.message))
        self.message.reply_text.assert_called()

        # /profile
        self.message.reply_text.reset_mock()
        self.loop.run_until_complete(stats.user_profile(self.client, self.message))
        self.message.reply_text.assert_called()

        # /id
        self.message.reply_text.reset_mock()
        self.message.reply_to_message = None
        self.loop.run_until_complete(stats.getid(self.client, self.message))
        self.message.reply_text.assert_called()

        # /ping
        resp_msg = MagicMock()
        resp_msg.edit_caption = AsyncMock()
        self.message.reply_photo = AsyncMock(return_value=resp_msg)
        self.loop.run_until_complete(ping.ping(self.client, self.message))
        self.message.reply_photo.assert_called()

        # /reactions
        self.message.reply_text.reset_mock()
        self.message.command = ["reactions"]
        with patch("nexichat.modules.reaction.is_reactions_enabled", AsyncMock(return_value=True)), \
             patch("nexichat.modules.reaction.get_chat_emojis", AsyncMock(return_value=["👍", "❤️"])):
            self.loop.run_until_complete(reaction.reaction_status_toggle(self.client, self.message))
            self.message.reply_text.assert_called()

        # /security
        self.message.reply_text.reset_mock()
        self.message.command = ["security"]
        with patch("nexichat.modules.security.is_antilink_enabled", AsyncMock(return_value=False)), \
             patch("nexichat.modules.security.is_antispam_enabled", AsyncMock(return_value=False)):
            self.loop.run_until_complete(security.security_status_cmd(self.client, self.message))
            self.message.reply_text.assert_called()

        # /welcome
        self.message.reply_text.reset_mock()
        self.message.command = ["welcome"]
        with patch("nexichat.modules.welcome.is_welcome_enabled", AsyncMock(return_value=True)):
            self.loop.run_until_complete(welcome.welcome_toggle_cmd(self.client, self.message))
            self.message.reply_text.assert_called()

        # /truth, /dare, /flirt, /roast, /toss, /quote, /couples, /propose
        for cmd_func in [
            games.truth_command,
            games.dare_command,
            games.flirt_command,
            games.roast_command,
            games.toss_command,
            games.quote_command,
            games.couple_command,
            games.propose_command,
        ]:
            self.message.reply_text.reset_mock()
            self.loop.run_until_complete(cmd_func(self.client, self.message))
            self.message.reply_text.assert_called()

    def test_extended_commands_execution(self):
        """Test extended commands: chatbot, ai, love, shayri, joke, draw, setname, afk, tagall, clone, storage."""
        from nexichat.modules import chatbot, afk, tagall, clone, sentinel

        # /chatbot
        self.message.reply_text.reset_mock()
        self.message.command = ["chatbot"]
        with patch("nexichat.modules.chatbot.is_chatbot_enabled", AsyncMock(return_value=True)):
            self.loop.run_until_complete(chatbot.chatbot_toggle_cmd(self.client, self.message))
            self.message.reply_text.assert_called()

        # /ask
        status_msg = MagicMock()
        status_msg.edit_text = AsyncMock()
        self.message.reply_text = AsyncMock(return_value=status_msg)
        self.message.text = "/ask hello anshika"
        self.message.command = ["ask", "hello", "anshika"]
        with patch("nexichat.modules.chatbot.generate_conversational_response", AsyncMock(return_value="Hii baby! 🌸")):
            self.loop.run_until_complete(chatbot.ask_ai_command(self.client, self.message))
            status_msg.edit_text.assert_called()

        # /love
        self.message.reply_text.reset_mock()
        self.message.text = "/love Rahul Anshika"
        self.message.command = ["love", "Rahul", "Anshika"]
        self.loop.run_until_complete(chatbot.love_command(self.client, self.message))
        self.message.reply_text.assert_called()

        # /shayri
        self.message.reply_text.reset_mock()
        self.loop.run_until_complete(chatbot.shayari_command(self.client, self.message))
        self.message.reply_text.assert_called()

        # /joke
        self.message.reply_text.reset_mock()
        self.loop.run_until_complete(chatbot.joke_command(self.client, self.message))
        self.message.reply_text.assert_called()

        # /setname
        self.message.reply_text.reset_mock()
        self.message.text = "/setname Shona"
        self.message.command = ["setname", "Shona"]
        with patch("nexichat.modules.chatbot.save_user_nickname", AsyncMock()):
            self.loop.run_until_complete(chatbot.setname_command(self.client, self.message))
            self.message.reply_text.assert_called()

        # /afk
        self.message.reply_text.reset_mock()
        self.message.text = "/afk studying for class 12"
        self.message.command = ["afk", "studying", "for", "class", "12"]
        with patch("nexichat.modules.afk.set_user_afk", AsyncMock()):
            self.loop.run_until_complete(afk.afk_command(self.client, self.message))
            self.message.reply_text.assert_called()

        # /tagall
        self.message.reply_text.reset_mock()
        self.message.text = "/tagall Good morning everyone"
        self.message.command = ["tagall", "Good", "morning", "everyone"]
        member = MagicMock()
        member.status = ChatMemberStatus.ADMINISTRATOR
        self.client.get_chat_member = AsyncMock(return_value=member)
        with patch("nexichat.modules.tagall.ACTIVE_TAGALL", {}):
            self.loop.run_until_complete(tagall.tagall_command(self.client, self.message))
            self.message.reply_text.assert_called()

        # /cancel tagall
        self.message.reply_text.reset_mock()
        self.message.command = ["cancel"]
        with patch("nexichat.modules.tagall.ACTIVE_TAGALL", {}):
            self.loop.run_until_complete(tagall.cancel_tagall_command(self.client, self.message))
            self.message.reply_text.assert_called()

        # /cloned
        self.message.reply_text.reset_mock()
        with patch("nexichat.modules.clone.cloneownerdb") as mock_db:
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=[])
            mock_db.find.return_value = mock_cursor
            self.loop.run_until_complete(clone.list_cloned_bots(self.client, self.message))
            self.message.reply_text.assert_called()

        # /idclones
        self.message.reply_text.reset_mock()
        with patch("nexichat.modules.clone.cloneuserdb") as mock_db:
            mock_cursor = MagicMock()
            mock_cursor.to_list = AsyncMock(return_value=[])
            mock_db.find.return_value = mock_cursor
            self.loop.run_until_complete(clone.list_id_clones(self.client, self.message))
            self.message.reply_text.assert_called()

        # /storage
        self.message.reply_text.reset_mock()
        with patch("nexichat.modules.sentinel.OWNER_ID", str(self.user.id)), \
             patch("nexichat.modules.sentinel.get_disk_stats", return_value={"total_gb": 100.0, "used_gb": 50.0, "free_gb": 50.0, "percent": 50.0}), \
             patch("nexichat.modules.sentinel.get_ram_stats", return_value={"total_mb": 512.0, "used_mb": 200.0, "free_mb": 312.0, "percent": 39.0}), \
             patch("nexichat.modules.sentinel.get_cache_size", return_value=(0, 0.0)):
            self.loop.run_until_complete(sentinel.storage_command(self.client, self.message))
            self.message.reply_text.assert_called()


if __name__ == "__main__":
    unittest.main()

