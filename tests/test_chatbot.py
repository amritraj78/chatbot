import os
import unittest
from nexichat.database.chatbot import (
    is_chatbot_enabled,
    set_chatbot_enabled,
    save_chat_reply,
    get_chat_reply,
    save_qa_pair,
    get_qa_answer,
    save_sticker,
    get_random_sticker
)
from nexichat.modules.helpers.ai import (
    calculate_love,
    get_random_shayari,
    get_random_joke,
    generate_conversational_response,
    is_abusive,
    get_abuse_refusal,
    get_voice_reply,
    get_photo_reply,
    get_video_reply,
    get_animation_reply
)

class TestChatbotFeatures(unittest.IsolatedAsyncioTestCase):

    async def test_chatbot_database_toggle(self):
        chat_id = -10099887766
        # Default should be enabled (True)
        enabled_default = await is_chatbot_enabled(chat_id)
        self.assertTrue(enabled_default)

        # Disable chatbot
        await set_chatbot_enabled(chat_id, False)
        enabled_after_off = await is_chatbot_enabled(chat_id)
        self.assertFalse(enabled_after_off)

        # Re-enable chatbot
        await set_chatbot_enabled(chat_id, True)
        enabled_after_on = await is_chatbot_enabled(chat_id)
        self.assertTrue(enabled_after_on)

    async def test_learned_replies(self):
        await save_chat_reply("koyeb deployment", "text", "Koyeb deployment is ready and working!")
        reply = await get_chat_reply("koyeb deployment")
        self.assertIsNotNone(reply)
        self.assertEqual(reply["content"], "Koyeb deployment is ready and working!")

    async def test_qa_memory_learning(self):
        # AI learns a Q&A pair so it never forgets
        await save_qa_pair("capital of france", "Paris is the capital of France ji! 🌸")
        ans = await get_qa_answer("capital of france")
        self.assertIsNotNone(ans)
        self.assertIn("Paris", ans)

    async def test_sticker_learning(self):
        stk_id = "CAACAgIAAxkBAAEK7nxlffK7g4Z243_TEST_ID"
        await save_sticker(stk_id)
        stk = get_random_sticker()
        self.assertIsNotNone(stk)

    async def test_anti_abuse_filter(self):
        self.assertTrue(is_abusive("bsdk"))
        self.assertTrue(is_abusive("tum chutiya ho"))
        self.assertFalse(is_abusive("hello pyari bot"))
        
        # Test refusal message
        refusal = get_abuse_refusal()
        self.assertTrue(any(k in refusal.lower() for k in ["gand", "bad words", "gaali", "naraz", "respect"]))

    async def test_media_replies(self):
        v = get_voice_reply()
        p = get_photo_reply()
        vid = get_video_reply()
        anim = get_animation_reply()
        self.assertTrue(len(v) > 5)
        self.assertTrue(len(p) > 5)
        self.assertTrue(len(vid) > 5)
        self.assertTrue(len(anim) > 5)

    async def test_love_calculator(self):
        res = calculate_love("Amrit", "Chatbot")
        self.assertIn("Love Compatibility Test", res)
        self.assertIn("Amrit", res)
        self.assertIn("%", res)

    async def test_shayari(self):
        sh = get_random_shayari()
        self.assertIsInstance(sh, str)
        self.assertTrue(len(sh) > 10)

    async def test_joke(self):
        jk = get_random_joke()
        self.assertIsInstance(jk, str)
        self.assertTrue(len(jk) > 10)

    async def test_conversational_ai_math(self):
        resp = await generate_conversational_response("5 * 8")
        self.assertIn("40", resp)

    async def test_conversational_ai_creator(self):
        resp = await generate_conversational_response("who is your creator")
        # Anshika character maintains independence without mentioning owner
        self.assertTrue(any(word in resp.lower() for word in ["owner", "malik", "independent", "marzi"]))

    async def test_conversational_ai_identity(self):
        resp = await generate_conversational_response("who are you")
        self.assertIn("Anshika", resp)
        self.assertTrue("Chamoli" in resp or "Uttarakhand" in resp)

    async def test_conversational_ai_telugu(self):
        from nexichat.modules.helpers.ai import detect_language
        lang1 = detect_language("బాగున్నారా?")
        self.assertEqual(lang1, "telugu")
        lang2 = detect_language("ela unnav?")
        self.assertEqual(lang2, "telugu")

    async def test_conversational_ai_group_links(self):
        resp = await generate_conversational_response("group link")
        # Anshika talks naturally as a friend without unsolicited link spam
        self.assertTrue("group" in resp.lower() or "channel" in resp.lower() or "chat" in resp.lower())

    async def test_telegram_db_functions(self):
        from nexichat.database.telegram_db import get_db_chats, log_qa_to_telegram, log_reply_to_telegram
        chats = get_db_chats()
        self.assertTrue(len(chats) >= 1)
        self.assertNotIn("privatethink", chats)
        self.assertNotIn("amrit_feel", chats)
        self.assertIn("Yaarwinprofits", chats)
        # Should execute safely even without client connection
        await log_qa_to_telegram(None, "sample q", "sample a")
        await log_reply_to_telegram(None, "sample word", "text", "sample reply")

    async def test_sticker_fallback_guarantee(self):
        # Fallback should be returned if no sticker learned yet
        fb = "TEST_FALLBACK_FILE_ID"
        res = get_random_sticker(fallback=fb)
        self.assertIsNotNone(res)

    async def test_vivid_user_memory_database(self):
        from nexichat.database.chatbot import (
            update_vivid_user_memory,
            get_vivid_user_memory,
            format_vivid_user_context,
            clear_vivid_user_memory
        )
        test_uid = 9988776655
        await clear_vivid_user_memory(test_uid)

        # First interaction: user introduces themselves
        mem = await update_vivid_user_memory(
            user_id=test_uid,
            role="user",
            text="Hii Anshika! Mera naam Rohit hai aur main coding karta hoon",
            user_name="Rohit",
            username="rohit_coder"
        )
        self.assertEqual(mem["name"], "Rohit")
        self.assertEqual(mem["interactions"], 1)
        self.assertIn("coding", mem["topics"])

        # Second interaction: Anshika replies
        mem2 = await update_vivid_user_memory(
            user_id=test_uid,
            role="anshika",
            text="Hii Rohit! Waah coding toh bohot exciting hai!",
            user_name="Rohit"
        )
        self.assertEqual(mem2["interactions"], 2)

        # Context formatting for AI
        ctx = await format_vivid_user_context(test_uid)
        self.assertIn("Rohit", ctx)
        self.assertIn("coding", ctx)

        # Cleanup
        await clear_vivid_user_memory(test_uid)

    async def test_api_usage_tracking_and_daily_quota(self):
        from nexichat.database.chatbot import (
            track_api_call,
            track_db_fallback_call,
            get_api_usage_stats,
            format_api_usage_dashboard
        )
        await track_api_call("groq", success=True)
        await track_api_call("gemini", success=True)
        await track_api_call("waterfall_free", success=True)
        await track_db_fallback_call()

        stats = await get_api_usage_stats()
        self.assertGreaterEqual(stats["groq_calls"], 1)
        self.assertGreaterEqual(stats["gemini_calls"], 1)
        self.assertGreaterEqual(stats["waterfall_calls"], 1)
        self.assertGreaterEqual(stats["db_fallback_calls"], 1)
        self.assertIn("groq_used_pct", stats)
        self.assertIn("groq_left_pct", stats)
        self.assertEqual(stats["groq_quota"], 1000)
        self.assertEqual(stats["gemini_quota"], 1500)

        dashboard = await format_api_usage_dashboard()
        self.assertIn("VIP AI API USAGE & DAILY QUOTA", dashboard)
        self.assertIn("Groq AI Engine", dashboard)
        self.assertIn("Google Gemini AI", dashboard)


    def test_hinglish_to_hindi_transliteration(self):
        from nexichat.modules.helpers.media_gen import hinglish_to_hindi
        # Already Hindi
        self.assertEqual(hinglish_to_hindi("नमस्ते"), "नमस्ते")
        # Hinglish converts to Hindi
        res = hinglish_to_hindi("Hii kaise ho")
        self.assertTrue(len(res) > 0)
        # Should contain Devanagari characters
        has_devanagari = any("\u0900" <= c <= "\u097F" for c in res)
        self.assertTrue(has_devanagari)

    async def test_userbot_never_reveals_owner(self):
        class MockUser:
            is_bot = False
            first_name = "Lav"
        class MockClient:
            me = MockUser()

        mock_client = MockClient()
        resp_owner = await generate_conversational_response("owner kaun hai", client=mock_client)
        # Userbot must NOT reveal Amrit Raj or Villanns as owner
        self.assertNotIn("Amrit Raj", resp_owner)
        self.assertNotIn("@Villanns", resp_owner)
        # Should talk like an independent real girl
        self.assertTrue(any(k in resp_owner.lower() for k in ["owner", "malik", "ghulam", "boss", "real ladki"]))

    def test_polly_aditi_voice_generation(self):
        from nexichat.modules.helpers.media_gen import generate_voice_file
        path = generate_voice_file("Hii kaise ho!", voice="Aditi")
        self.assertIsNotNone(path)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(os.path.getsize(path) > 500)
    async def test_db_fallback_toggle(self):
        from nexichat.database.chatbot import (
            is_db_fallback_enabled,
            set_db_fallback_enabled,
            get_chatbot_mode,
            set_chatbot_mode
        )
        # Default mode is 'auto' (API first, auto DB fallback on quota exhaustion)
        self.assertEqual(await get_chatbot_mode(), "auto")
        self.assertTrue(await is_db_fallback_enabled())
        # Switch to database only
        await set_chatbot_mode("database")
        self.assertEqual(await get_chatbot_mode(), "database")
        self.assertTrue(await is_db_fallback_enabled())
        # Disable DB fallback (Strict API mode)
        await set_db_fallback_enabled(False)
        self.assertEqual(await get_chatbot_mode(), "api")
        self.assertFalse(await is_db_fallback_enabled())
        # Re-enable
        await set_db_fallback_enabled(True)
        self.assertEqual(await get_chatbot_mode(), "auto")
        self.assertTrue(await is_db_fallback_enabled())

    async def test_toxic_filtering_and_db_fallback(self):
        from nexichat.database.chatbot import is_toxic_or_canned_reply, save_chat_reply, get_chat_reply
        self.assertTrue(is_toxic_or_canned_reply("में"))
        self.assertTrue(is_toxic_or_canned_reply("heyy Rahul! 👋 finally message kiya"))
        self.assertTrue(is_toxic_or_canned_reply("Hyy farzii"))
        self.assertTrue(is_toxic_or_canned_reply("What are u finding for in the group"))
        self.assertFalse(is_toxic_or_canned_reply("Main badhiya hoon, aap batao kaise ho?"))

        # Should refuse to save toxic reply
        await save_chat_reply("rahul", "text", "heyy Rahul!")
        self.assertIsNone(await get_chat_reply("rahul"))

    async def test_persistent_dm_history(self):
        from nexichat.database.chatbot import save_dm_message, get_dm_history, clear_dm_history
        test_uid = 9988776655
        await clear_dm_history(test_uid)

        # Empty initially
        hist0 = await get_dm_history(test_uid)
        self.assertEqual(len(hist0), 0)

        # Save turns
        await save_dm_message(test_uid, "user", "mera naam rohan hai", user_name="Rohan")
        await save_dm_message(test_uid, "anshika", "Hii Rohan! Kaise ho aap?", user_name="Rohan")
        await save_dm_message(test_uid, "user", "kal mera physics ka exam hai", user_name="Rohan")
        await save_dm_message(test_uid, "anshika", "Best of luck! Ache se likhna!", user_name="Rohan")

        # Fetch history
        hist = await get_dm_history(test_uid, limit=10)
        self.assertEqual(len(hist), 4)
        self.assertEqual(hist[0]["role"], "user")
        self.assertIn("rohan", hist[0]["text"])
        self.assertEqual(hist[1]["role"], "anshika")
        self.assertIn("Kaise ho", hist[1]["text"])
        self.assertEqual(hist[2]["role"], "user")
        self.assertIn("physics", hist[2]["text"])

        # Clear history
        await clear_dm_history(test_uid)
        hist_cleared = await get_dm_history(test_uid)
        self.assertEqual(len(hist_cleared), 0)

    async def test_vivid_context_format(self):
        from nexichat.database.chatbot import update_vivid_user_memory, format_vivid_user_context
        test_uid = 9911223344
        await update_vivid_user_memory(test_uid, "user", "Mujhe coding aur python bohot pasand hai", user_name="Aman")
        ctx = await format_vivid_user_context(test_uid, "Aman")
        self.assertIn("Aman", ctx)
        self.assertIn("coding", ctx)

    async def test_dm_reset_command(self):
        test_uid = 7766554433
        from nexichat.database.chatbot import save_dm_message, get_dm_history
        await save_dm_message(test_uid, "user", "Secret info")
        reply = await generate_conversational_response("purani baatein bhool jao", user_id=test_uid)
        self.assertIn("bhula di", reply)
        hist = await get_dm_history(test_uid)
        self.assertEqual(len(hist), 0)

    def test_moderate_emojis(self):
        from nexichat.modules.helpers.ai import moderate_emojis, EMOJI_PATTERN
        text_with_emojis = "Arey kya hua yrr? Aise udaas mat ho na! 🥺❤️🌸"
        
        # Test 100 runs to verify 75-80% plain text distribution
        plain_count = 0
        single_emoji_count = 0
        for _ in range(100):
            res = moderate_emojis(text_with_emojis)
            found = EMOJI_PATTERN.findall(res)
            if len(found) == 0:
                plain_count += 1
            else:
                single_emoji_count += 1
                # Must never retain more than 1 emoji!
                self.assertLessEqual(len(found), 2)  # Single emoji + possible variation selector

        # Plain text should be the strong majority (approx 75%)
        self.assertGreaterEqual(plain_count, 55)
        self.assertGreaterEqual(single_emoji_count, 5)

        # Test variation selector cleanliness (no orphaned \ufe0f)
        heart_text = "Mujhe tumse pyar hai ❤️"
        res_heart = moderate_emojis(heart_text)
        self.assertNotIn("\ufe0f", res_heart.replace("❤️", ""))

    def test_clean_modern_girl_reply_brevity_and_emojis(self):
        from nexichat.modules.helpers.ai import clean_modern_girl_reply
        # Test Priya intercept
        ans = clean_modern_girl_reply("Mera naam Priya hai aur main aapki sahayata karungi 🌸✨")
        self.assertNotIn("Priya", ans)
        self.assertNotIn("sahayata", ans)


if __name__ == "__main__":
    unittest.main()

