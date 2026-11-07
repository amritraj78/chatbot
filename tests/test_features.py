import sys
import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

# Mock third-party libraries if they are not installed in the test environment
for mod_name in [
    "dotenv", "pymongo", "motor", "motor.motor_asyncio",
    "pyrogram", "pyrogram.enums", "pyrogram.types",
    "pyrogram.errors", "pyrogram.errors.exceptions",
    "pyrogram.errors.exceptions.bad_request_400",
    "uvloop", "Abg", "flask", "speedtest", "psutil"
]:
    if mod_name not in sys.modules:
        m = MagicMock()
        m.on_message = MagicMock(return_value=lambda f: f)
        m.on_callback_query = MagicMock(return_value=lambda f: f)
        sys.modules[mod_name] = m

# Make nexichat instance's on_message return a pass-through decorator
from nexichat import nexichat
nexichat.on_message = MagicMock(return_value=lambda f: f)
nexichat.on_callback_query = MagicMock(return_value=lambda f: f)



class TestReactionFeatures(unittest.TestCase):
    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def tearDown(self):
        self.loop.close()

    def test_default_emojis(self):
        from nexichat.database.reactions import DEFAULT_EMOJIS
        self.assertIsInstance(DEFAULT_EMOJIS, list)
        self.assertTrue(len(DEFAULT_EMOJIS) > 0)
        self.assertIn("👍", DEFAULT_EMOJIS)
        self.assertIn("❤️", DEFAULT_EMOJIS)

    def test_database_reactions_enabled(self):
        from nexichat.database import reactions
        mock_collection = MagicMock()

        # Test default True when not found in DB
        mock_collection.find_one = AsyncMock(return_value=None)
        with patch.object(reactions, 'reactionsdb', mock_collection):
            res = self.loop.run_until_complete(reactions.is_reactions_enabled(-100123))
            self.assertTrue(res)

        # Test False when explicitly disabled
        mock_collection.find_one = AsyncMock(return_value={"chat_id": -100123, "enabled": False})
        with patch.object(reactions, 'reactionsdb', mock_collection):
            res = self.loop.run_until_complete(reactions.is_reactions_enabled(-100123))
            self.assertFalse(res)

        # Test set_reactions_enabled update call
        mock_collection.update_one = AsyncMock()
        with patch.object(reactions, 'reactionsdb', mock_collection):
            self.loop.run_until_complete(reactions.set_reactions_enabled(-100123, False))
            mock_collection.update_one.assert_called_once_with(
                {"chat_id": -100123},
                {"$set": {"enabled": False}},
                upsert=True
            )

    def test_database_custom_emojis(self):
        from nexichat.database import reactions
        mock_collection = MagicMock()

        # Test get_chat_emojis fallback to default
        mock_collection.find_one = AsyncMock(return_value=None)
        with patch.object(reactions, 'reactionsdb', mock_collection):
            res = self.loop.run_until_complete(reactions.get_chat_emojis(-100123))
            self.assertEqual(res, reactions.DEFAULT_EMOJIS)

        # Test get_chat_emojis with custom emojis
        custom = ["🔥", "⚡", "🎉"]
        mock_collection.find_one = AsyncMock(return_value={"chat_id": -100123, "emojis": custom})
        with patch.object(reactions, 'reactionsdb', mock_collection):
            res = self.loop.run_until_complete(reactions.get_chat_emojis(-100123))
            self.assertEqual(res, custom)

        # Test set_chat_emojis
        mock_collection.update_one = AsyncMock()
        with patch.object(reactions, 'reactionsdb', mock_collection):
            self.loop.run_until_complete(reactions.set_chat_emojis(-100123, custom))
            mock_collection.update_one.assert_called_once_with(
                {"chat_id": -100123},
                {"$set": {"emojis": custom}},
                upsert=True
            )

        # Test reset_chat_emojis resets to default list
        mock_collection.update_one = AsyncMock()
        with patch.object(reactions, 'reactionsdb', mock_collection):
            self.loop.run_until_complete(reactions.reset_chat_emojis(-100123))
            mock_collection.update_one.assert_called_once_with(
                {"chat_id": -100123},
                {"$set": {"emojis": reactions.DEFAULT_EMOJIS}},
                upsert=True
            )

    def test_all_modules_list(self):
        from nexichat.modules import ALL_MODULES
        self.assertIn("reaction", ALL_MODULES)
        self.assertNotIn("~reaction", ALL_MODULES)
        self.assertIn("start", ALL_MODULES)
        self.assertIn("ping", ALL_MODULES)
        self.assertIn("clone", ALL_MODULES)
        self.assertIn("afk", ALL_MODULES)
        self.assertIn("tagall", ALL_MODULES)
        self.assertIn("chatbot", ALL_MODULES)
        self.assertIn("games", ALL_MODULES)
        self.assertIn("welcome", ALL_MODULES)
        self.assertIn("sentinel", ALL_MODULES)

    def test_auto_react_ignores_commands(self):
        from nexichat.modules import reaction
        mock_client = MagicMock()
        mock_msg = MagicMock()
        mock_msg.text = "/start"
        mock_msg.caption = None
        mock_msg.react = AsyncMock()

        # Should ignore /start and NOT react
        with patch("nexichat.modules.reaction.send_bot_reaction", AsyncMock()) as mock_react:
            self.loop.run_until_complete(reaction.auto_react_handler(mock_client, mock_msg))
            mock_react.assert_not_called()

    def test_auto_react_reacts_to_normal_message(self):
        from nexichat.modules import reaction
        mock_client = MagicMock()
        mock_client.bot_token = "test_token"
        mock_msg = MagicMock()
        mock_msg.empty = False
        mock_msg.service = False
        mock_msg.id = 555
        mock_msg.text = "testing 1 2 3 neutral text"
        mock_msg.caption = None
        mock_msg.chat.id = -100999
        mock_msg.chat.type = "group"
        mock_msg.from_user = MagicMock()
        mock_msg.from_user.id = 123456

        with patch("nexichat.modules.reaction.is_reactions_enabled", AsyncMock(return_value=True)), \
             patch("nexichat.modules.reaction.get_chat_emojis", AsyncMock(return_value=["🔥"])), \
             patch("nexichat.modules.reaction.add_served_chat", AsyncMock()), \
             patch("nexichat.modules.reaction.send_bot_reaction", AsyncMock()) as mock_react:
            self.loop.run_until_complete(reaction.auto_react_handler(mock_client, mock_msg))
            mock_react.assert_called_once_with("test_token", -100999, 555, "🔥")

    def test_auto_react_contextual_reaction(self):
        from nexichat.modules import reaction
        mock_client = MagicMock()
        mock_client.bot_token = "test_token"
        mock_msg = MagicMock()
        mock_msg.empty = False
        mock_msg.service = False
        mock_msg.id = 556
        mock_msg.text = "haha lol funny"
        mock_msg.caption = None
        mock_msg.chat.id = -100999
        mock_msg.chat.type = "group"
        mock_msg.from_user = MagicMock()
        mock_msg.from_user.id = 123456

        with patch("nexichat.modules.reaction.is_reactions_enabled", AsyncMock(return_value=True)), \
             patch("nexichat.modules.reaction.add_served_chat", AsyncMock()), \
             patch("nexichat.modules.reaction.send_bot_reaction", AsyncMock()) as mock_react:
            self.loop.run_until_complete(reaction.auto_react_handler(mock_client, mock_msg))
            mock_react.assert_called_once()
            args = mock_react.call_args[0]
            self.assertIn(args[3], ["😂", "🤣", "😁", "😆"])

    def test_dice_game_command(self):
        from nexichat.modules import games
        mock_client = MagicMock()
        mock_msg = MagicMock()
        mock_msg.chat.id = -100123
        mock_msg.from_user.first_name = "Rahul"
        mock_msg.text = "/dice"
        mock_msg.command = ["dice"]
        mock_msg.dice = None

        mock_user_dice = MagicMock()
        mock_user_dice.dice.value = 5
        mock_msg.reply_dice = AsyncMock(return_value=mock_user_dice)

        mock_bot_dice = MagicMock()
        mock_bot_dice.dice.value = 3
        mock_client.send_dice = AsyncMock(return_value=mock_bot_dice)

        mock_status = MagicMock()
        mock_status.edit_text = AsyncMock()
        mock_msg.reply_text = AsyncMock(return_value=mock_status)

        self.loop.run_until_complete(games.interactive_dice_match(mock_client, mock_msg))
        mock_msg.reply_dice.assert_called_once_with(emoji="🎲")
        mock_client.send_dice.assert_called_once_with(-100123, emoji="🎲")
        mock_status.edit_text.assert_called_once()
        self.assertIn("Anshika", mock_status.edit_text.call_args[0][0])

    def test_animated_dice_emoji_match(self):
        from nexichat.modules import games
        mock_client = MagicMock()
        mock_msg = MagicMock()
        mock_msg.chat.id = -100123
        mock_msg.from_user.first_name = "Rahul"
        mock_msg.text = None
        mock_msg.command = None
        mock_msg.dice = MagicMock()
        mock_msg.dice.emoji = "🎲"
        mock_msg.dice.value = 4

        mock_bot_dice = MagicMock()
        mock_bot_dice.dice.value = 6
        mock_client.send_dice = AsyncMock(return_value=mock_bot_dice)

        mock_status = MagicMock()
        mock_status.edit_text = AsyncMock()
        mock_msg.reply_text = AsyncMock(return_value=mock_status)

        self.loop.run_until_complete(games.interactive_dice_match(mock_client, mock_msg))
        mock_client.send_dice.assert_called_once_with(-100123, emoji="🎲")
        mock_status.edit_text.assert_called_once()
        self.assertIn("Anshika", mock_status.edit_text.call_args[0][0])

    def test_afk_system_and_formatting(self):
        from nexichat.database.chatbot import set_user_afk, get_user_afk, remove_user_afk
        from nexichat.modules.afk import format_duration
        
        # Test duration formatting
        self.assertEqual(format_duration(45), "45 seconds")
        self.assertEqual(format_duration(150), "2 minutes")
        self.assertEqual(format_duration(3660), "1h 1m")

        # Test AFK set, get, remove
        user_id = 99887766
        self.loop.run_until_complete(set_user_afk(user_id, "Study time"))
        afk_info = self.loop.run_until_complete(get_user_afk(user_id))
        self.assertIsNotNone(afk_info)
        self.assertEqual(afk_info["reason"], "Study time")
        self.assertTrue(afk_info["afk"])

        removed = self.loop.run_until_complete(remove_user_afk(user_id))
        self.assertEqual(removed["reason"], "Study time")
        after_remove = self.loop.run_until_complete(get_user_afk(user_id))
        self.assertIsNone(after_remove)

    def test_couples_deterministic_seed(self):
        import hashlib
        import random
        chat_id = -100999
        today_str = "2026-11-05"
        seed1 = int(hashlib.md5(f"{chat_id}_{today_str}".encode()).hexdigest(), 16)
        seed2 = int(hashlib.md5(f"{chat_id}_{today_str}".encode()).hexdigest(), 16)
        self.assertEqual(seed1, seed2)
        
        rng1 = random.Random(seed1)
        rng2 = random.Random(seed2)
        self.assertEqual(rng1.randint(1, 100), rng2.randint(1, 100))

    def test_propose_validation(self):
        from nexichat.modules.games import propose_callback_handler
        mock_client = MagicMock()
        mock_query = MagicMock()
        mock_query.data = "prop_acc_111_222"
        mock_query.from_user.id = 333  # Non-target user trying to click
        mock_query.answer = AsyncMock()

        self.loop.run_until_complete(propose_callback_handler(mock_client, mock_query))
        mock_query.answer.assert_called_once()
        self.assertIn("ye proposal aapke liye nahi hai", mock_query.answer.call_args[0][0])

    def test_ai_waterfall_fast_response(self):
        from nexichat.modules.helpers.ai import generate_conversational_response
        res = self.loop.run_until_complete(
            generate_conversational_response("explain how to make purple colour", "TestUser", is_question_mode=True)
        )
        self.assertIsNotNone(res)
        # Should be an actual answer, not empty or error
        self.assertTrue(len(res) >= 10)

    def test_telegram_db_targets_configuration(self):
        from nexichat.database.telegram_db import get_db_chats
        chats = get_db_chats()
        self.assertIn("-1004415957871", chats)
        self.assertIn("chatbotsaved", chats)
        self.assertIn("Yaarwinprofits", chats)

    def test_cloned_bot_telegram_db_fallback(self):
        from nexichat.database.telegram_db import send_to_telegram_db

        # Cloned bot client that always throws permission error
        mock_clone_client = MagicMock()
        mock_clone_client.send_message = AsyncMock(side_effect=Exception("ChatAdminRequired"))

        # Main bot client that succeeds
        mock_main_bot = MagicMock()
        mock_main_bot.is_connected = True
        mock_main_bot.send_message = AsyncMock()

        with patch("nexichat.nexichat", mock_main_bot):
            self.loop.run_until_complete(
                send_to_telegram_db(mock_clone_client, "✦ #DATABASE #QA_LEARNED ✦\nTest question")
            )
            # Main bot should have been invoked as fallback to deliver the message
            self.assertTrue(mock_main_bot.send_message.called)

    def test_telegram_db_sync_manual_and_auto_formats(self):
        from nexichat.database.telegram_db import sync_database_from_telegram
        from nexichat.database.chatbot import _qa_cache, _replies_cache

        # Create mock message history with diverse formats
        msg1 = MagicMock()
        msg1.sticker = None
        msg1.text = "✦ **#DATABASE #QA_LEARNED** ✦\n❓ **Question:** what is water\n💡 **Answer:** Water is H2O life fluid! 💧"

        msg2 = MagicMock()
        msg2.sticker = None
        msg2.text = "Q: who are you\nA: Main Anshika hoon, Class 12 student Chamoli se! 🌸"

        msg3 = MagicMock()
        msg3.sticker = None
        msg3.text = "Trigger: good morning\nReply: Shubh Prabhat ji! Have a wonderful day! ☀️"

        async def mock_history(chat_id, limit=200):
            for m in [msg1, msg2, msg3]:
                yield m

        mock_client = MagicMock()
        mock_client.get_chat_history = mock_history

        self.loop.run_until_complete(sync_database_from_telegram(mock_client))
        self.assertIn("what is water", _qa_cache)
        self.assertIn("who are you", _qa_cache)
        reply_words = [r.get("word") for r in _replies_cache]
        self.assertIn("good morning", reply_words)

    def test_get_chat_reply_signature_flexibility(self):
        from nexichat.database.chatbot import save_chat_reply, get_chat_reply
        self.loop.run_until_complete(save_chat_reply("koyeb_fast", "text", "Lightning fast performance!"))
        
        # Positional
        res1 = self.loop.run_until_complete(get_chat_reply("koyeb_fast"))
        self.assertIsNotNone(res1)
        self.assertEqual(res1.get("content"), "Lightning fast performance!")

        # Keyword clean_text
        res2 = self.loop.run_until_complete(get_chat_reply(clean_text="koyeb_fast"))
        self.assertIsNotNone(res2)
        self.assertEqual(res2.get("content"), "Lightning fast performance!")

    def test_social_links_config(self):
        import config
        self.assertEqual(getattr(config, "INSTAGRAM", None), "ex_amrit")
        self.assertEqual(getattr(config, "SNAPCHAT", None), "ex_amrit")
        self.assertEqual(getattr(config, "OWNER_USERNAME", None), "Villanns")

    def test_lru_cache_bounds(self):
        import nexichat.database.chatbot as cb
        # Test stickers cache bound (max 500)
        cb._stickers_cache = [f"stk_{i}" for i in range(500)]
        self.loop.run_until_complete(cb.save_sticker("stk_new"))
        self.assertEqual(len(cb._stickers_cache), 500)
        self.assertEqual(cb._stickers_cache[-1], "stk_new")

    def test_spontaneous_voice_regex(self):
        import re
        pattern = r"\b(voice\s*(?:bhejo|sunao|karo|me\s*bolo)|kuch\s*bolo\s*na|awaz\s*sunao|sing\s*a?\s*song|gana\s*gao|bolke\s*batao|apni\s*awaz|audio\s*bhejo)\b"
        self.assertTrue(bool(re.search(pattern, "priya voice bhejo please", re.IGNORECASE)))
        self.assertTrue(bool(re.search(pattern, "kuch bolo na", re.IGNORECASE)))
        self.assertTrue(bool(re.search(pattern, "apni awaz sunao", re.IGNORECASE)))
        self.assertFalse(bool(re.search(pattern, "how are you today", re.IGNORECASE)))

    def test_multi_turn_context_memory(self):
        from nexichat.database.chatbot import append_user_context, get_user_context, clear_user_context
        uid = 77889900
        clear_user_context(uid)
        self.assertEqual(len(get_user_context(uid)), 0)

        append_user_context(uid, "user", "Mera naam Rahul hai")
        append_user_context(uid, "priya", "Namaste Rahul ji!")
        ctx = get_user_context(uid)
        self.assertEqual(len(ctx), 2)
        self.assertEqual(ctx[0]["role"], "user")
        self.assertEqual(ctx[1]["text"], "Namaste Rahul ji!")

        clear_user_context(uid)
        self.assertEqual(len(get_user_context(uid)), 0)

    def test_language_detection(self):
        from nexichat.modules.helpers.ai import detect_language
        self.assertEqual(detect_language("नमस्ते आप कैसे हैं?"), "hindi")
        self.assertEqual(detect_language("Hello friend how are you"), "english")
        self.assertEqual(detect_language("kaise ho bhai sab badhiya?"), "hinglish")

    def test_security_antilink_and_antispam_db(self):
        from nexichat.database.reactions import (
            is_antilink_enabled,
            set_antilink_enabled,
            is_antispam_enabled,
            set_antispam_enabled
        )
        chat_id = -100445566
        # Anti-link
        self.loop.run_until_complete(set_antilink_enabled(chat_id, True))
        self.assertTrue(self.loop.run_until_complete(is_antilink_enabled(chat_id)))
        self.loop.run_until_complete(set_antilink_enabled(chat_id, False))
        self.assertFalse(self.loop.run_until_complete(is_antilink_enabled(chat_id)))

        # Anti-spam
        self.loop.run_until_complete(set_antispam_enabled(chat_id, True))
        self.assertTrue(self.loop.run_until_complete(is_antispam_enabled(chat_id)))

    def test_sudoers_add_get_remove(self):
        from nexichat.database.sudoers import add_sudo, get_sudoers, remove_sudo
        uid = 9988776655
        self.loop.run_until_complete(add_sudo(uid))
        sudoers = self.loop.run_until_complete(get_sudoers())
        self.assertIn(uid, sudoers)
        self.loop.run_until_complete(remove_sudo(uid))
        sudoers_after = self.loop.run_until_complete(get_sudoers())
        self.assertNotIn(uid, sudoers_after)

    def test_diagnostics_health_report(self):
        from nexichat.core.diagnostics import get_system_health_report
        rep = get_system_health_report()
        self.assertEqual(rep["status"], "healthy")
        self.assertIn("ram_mb", rep)
        self.assertIn("uptime", rep)
        self.assertIn("pid", rep)


    def test_runtime_error_reporting_rate_limit(self):
        from nexichat.core.diagnostics import report_exception_to_owner
        mock_client = MagicMock()
        mock_client.send_message = AsyncMock(return_value=True)
        # First alert should succeed
        res1 = self.loop.run_until_complete(report_exception_to_owner(mock_client, "test_ctx", ValueError("Boom!")))
        self.assertTrue(res1)
        # Duplicate alert within 60s should be rate-limited (return False)
        res2 = self.loop.run_until_complete(report_exception_to_owner(mock_client, "test_ctx", ValueError("Boom!")))
        self.assertFalse(res2)

    def test_similarity_caching_jaccard(self):
        from nexichat.database.chatbot import _jaccard_token_similarity
        sim1 = _jaccard_token_similarity("tumhara naam kya hai", "tumhara naam kya hai")
        self.assertAlmostEqual(sim1, 1.0)
        sim2 = _jaccard_token_similarity("aapka naam kya hai priya", "aapka naam kya hai")
        self.assertGreater(sim2, 0.70)
        sim3 = _jaccard_token_similarity("aaj mausam kaisa hai", "delhi ka temperature kitna hai")
        self.assertLess(sim3, 0.50)


    def test_id_clone_database_and_operations(self):
        from nexichat.modules.clone import cloneuserdb
        uid = 123456789
        dummy_session = "1BVtsOMQBu7...dummy_session..."
        details = {
            "user_id": uid,
            "cloned_by": 987654321,
            "name": "Test User",
            "username": "testuser",
            "session": dummy_session,
            "is_bot": False,
            "cloned_at": "2026-11-06 12:00:00"
        }
        # Insert
        self.loop.run_until_complete(cloneuserdb.update_one({"user_id": uid}, {"$set": details}, upsert=True))
        found = self.loop.run_until_complete(cloneuserdb.find_one({"user_id": uid}))
        self.assertIsNotNone(found)
        self.assertEqual(found["user_id"], uid)
        self.assertEqual(found["name"], "Test User")

        # Delete
        self.loop.run_until_complete(cloneuserdb.delete_one({"user_id": uid}))
        after_del = self.loop.run_until_complete(cloneuserdb.find_one({"user_id": uid}))
        self.assertIsNone(after_del)

    def test_id_clone_empty_guidance(self):
        from nexichat.modules.clone import id_clone_txt
        mock_msg = MagicMock()
        mock_msg.command = ["idclone"]
        mock_msg.reply_to_message = None
        mock_msg.reply_text = AsyncMock()

        self.loop.run_until_complete(id_clone_txt(MagicMock(), mock_msg))
        mock_msg.reply_text.assert_called_once()
        guide_text = mock_msg.reply_text.call_args[0][0]
        self.assertIn("ID CLONE SETUP GUIDE", guide_text)
        self.assertIn("Pyrogram v2", guide_text)

    def test_generate_session_script_valid(self):
        import os
        import py_compile
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "generate_session.py")
        self.assertTrue(os.path.exists(script_path), "generate_session.py must exist")
        # Ensure it compiles cleanly with zero syntax errors
        py_compile.compile(script_path, doraise=True)


if __name__ == "__main__":
    unittest.main()


