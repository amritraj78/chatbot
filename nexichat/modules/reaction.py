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
  Ye file bot ka "High-Speed Auto Reaction Engine" hai!
  
Kaise kaam karta hai?
  1. Instant Emojis: Jab bhi koi user ya channel message bhejta hai, ye bot
     turant Telegram HTTP MTProto endpoint par message_id par emoji react karta hai.
  2. Smart Contextual Triggers:
     - Morning / Love text -> ❤️, 🥰
     - Funny / Joke text -> 😂, 🤣, 😁
     - Question mark (?) -> 🤔, 👀
     - Fire / OP text -> 🔥, ⚡
     - Sad text -> 🥺, 🫂
  3. Commands:
     - /reactions on|off - Reactions chalu ya band karein.
     - /setreactions 👍 ❤️ 🔥 - Har group ke liye alag emojis set karein.
     - /resetreactions - Default emojis par reset karein.
================================================================================
"""

import random
import re
import logging
import asyncio
import requests
import config
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait, ReactionInvalid, ChatAdminRequired
from pyrogram.types import Message

from config import OWNER_ID
from nexichat import nexichat, SUDOERS
from nexichat.database.reactions import (
    DEFAULT_EMOJIS,
    get_chat_emojis,
    is_reactions_enabled,
    reset_chat_emojis,
    set_chat_emojis,
    set_reactions_enabled,
)
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user

from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)
_http_session = requests.Session()
_adapter = HTTPAdapter(pool_connections=25, pool_maxsize=30, max_retries=Retry(total=1, backoff_factor=0.1))
_http_session.mount("https://", _adapter)
_http_session.mount("http://", _adapter)


async def send_bot_reaction(bot_token: str, chat_id: int, message_id: int, emoji: str) -> bool:
    """Send an emoji reaction using Telegram Bot API setMessageReaction with fallback."""
    url = f"https://api.telegram.org/bot{bot_token}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}],
        "is_big": False
    }
    loop = asyncio.get_running_loop()
    try:
        resp = await loop.run_in_executor(
            None,
            lambda: _http_session.post(url, json=payload, timeout=4)
        )
        data = resp.json()
        if not data.get("ok"):
            desc = data.get("description", "")
            if "REACTION_INVALID" in desc and emoji != "❤️":
                # Fallback to universal heart reaction if group restricts this specific emoji
                fb_payload = dict(payload, reaction=[{"type": "emoji", "emoji": "❤️"}])
                fb_resp = await loop.run_in_executor(
                    None,
                    lambda: _http_session.post(url, json=fb_payload, timeout=3)
                )
                if fb_resp.json().get("ok"):
                    logger.info(f"Fallback reacted with ❤️ to msg {message_id} in chat {chat_id}")
                    return True
            logger.debug(f"Telegram Bot API reaction notice: {desc}")
            return False
        logger.info(f"Successfully reacted with {emoji} to msg {message_id} in chat {chat_id}")
        return True
    except Exception as e:
        logger.debug(f"Failed to send reaction via HTTP API: {e}")
        return False


async def is_admin_or_sudo(client: Client, message: Message) -> bool:
    """Check if the sender is an admin in the group or a bot sudoer/owner."""
    if not message.from_user:
        # In channels or anonymous admin posts
        if message.sender_chat and message.sender_chat.id == message.chat.id:
            return True
        return False

    user_id = message.from_user.id
    if user_id in SUDOERS or user_id == int(OWNER_ID):
        return True

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return True
        except Exception:
            return False

    return False


@nexichat.on_message(filters.command(["reactions", "reaction"]))
async def reaction_status_toggle(client: Client, message: Message):
    """
    Check current reaction status or toggle on/off:
    /reactions -> View status & emojis
    /reactions on -> Enable auto reactions
    /reactions off -> Disable auto reactions
    """
    chat_id = message.chat.id

    if len(message.command) > 1:
        # User wants to toggle on/off
        if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
            if not await is_admin_or_sudo(client, message):
                return await message.reply_text("❌ **Only chat administrators can modify reaction settings.**")

        action = message.command[1].lower()
        if action in ["on", "enable", "yes", "true"]:
            await set_reactions_enabled(chat_id, True)
            return await message.reply_text("✅ **Automatic reactions are now ENABLED for this chat!**")
        elif action in ["off", "disable", "no", "false"]:
            await set_reactions_enabled(chat_id, False)
            return await message.reply_text("🛑 **Automatic reactions are now DISABLED for this chat.**")
        else:
            return await message.reply_text("ℹ️ **Usage:** `/reactions on` or `/reactions off`")

    # If no argument, show current settings
    enabled = await is_reactions_enabled(chat_id)
    emojis = await get_chat_emojis(chat_id)
    status_text = "🟢 **ENABLED**" if enabled else "🔴 **DISABLED**"
    emojis_str = " ".join(emojis)

    text = (
        f"✨ **Reactions Settings for {message.chat.title or message.chat.first_name or 'Chat'}** ✨\n\n"
        f"**Status:** {status_text}\n"
        f"**Active Emojis:** {emojis_str}\n\n"
        f"**Commands:**\n"
        f"• `/reactions on` - Turn reactions ON\n"
        f"• `/reactions off` - Turn reactions OFF\n"
        f"• `/setreactions 👍 ❤️ 🔥` - Set custom emojis\n"
        f"• `/resetreactions` - Reset to default emojis"
    )
    await message.reply_text(text)


@nexichat.on_message(filters.command(["setreactions", "setreaction"]))
async def set_reactions_cmd(client: Client, message: Message):
    """
    Set custom emojis for this chat.
    Usage: /setreactions 👍 ❤️ 🔥 🥰
    """
    chat_id = message.chat.id

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
        if not await is_admin_or_sudo(client, message):
            return await message.reply_text("❌ **Only chat administrators can change reaction emojis.**")

    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ **Please provide one or more emojis after the command.**\n\n"
            "**Example:** `/setreactions 👍 ❤️ 🔥 🥰 👏`"
        )

    # Extract emojis from message text (skipping the command)
    raw_args = message.text.split(None, 1)[1]
    # Simple regex / extraction for unicode emojis and characters
    extracted = [e.strip() for e in re.findall(r'[^\s,]+', raw_args) if e.strip()]

    if not extracted:
        return await message.reply_text("❌ **No valid emojis found. Please provide valid Telegram reaction emojis.**")

    await set_chat_emojis(chat_id, extracted)
    await message.reply_text(
        f"✅ **Custom reaction emojis updated successfully!**\n\n"
        f"**Active Emojis ({len(extracted)}):** {' '.join(extracted)}"
    )


@nexichat.on_message(filters.command(["resetreactions", "resetreaction"]))
async def reset_reactions_cmd(client: Client, message: Message):
    """Reset reaction emojis back to default list."""
    chat_id = message.chat.id

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
        if not await is_admin_or_sudo(client, message):
            return await message.reply_text("❌ **Only chat administrators can reset reaction emojis.**")

    await reset_chat_emojis(chat_id)
    await message.reply_text(
        f"🔄 **Reaction emojis have been reset to default!**\n\n"
        f"**Default Emojis:** {' '.join(DEFAULT_EMOJIS)}"
    )


# Handler for automatic reactions on incoming messages and channel posts
@nexichat.on_message(
    (filters.incoming & (filters.group | filters.private | filters.channel)),
    group=10
)
async def auto_react_handler(client: Client, message: Message):
    """Automatically reacts to messages and channel posts."""
    try:
        # Ignore empty, service messages or media group extra triggers
        if message.empty or getattr(message, "service", False):
            return

        # Ignore bot commands so we don't react to commands like /start, /help, etc.
        text = message.text or message.caption
        if text and (text.startswith("/") or text.startswith("!") or text.startswith(".")):
            return

        chat_id = message.chat.id

        # Track served users and chats
        if message.chat.type == ChatType.PRIVATE and message.from_user:
            await add_served_user(message.from_user.id)
        elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
            await add_served_chat(chat_id)

        # Check if reactions are enabled in this chat
        if not await is_reactions_enabled(chat_id):
            return

        # Fetch emojis configured for this chat
        emojis = await get_chat_emojis(chat_id)
        if not emojis:
            emojis = DEFAULT_EMOJIS

        # Smart contextual reaction detection (Strict Telegram Bot API supported reactions)
        chosen_emoji = None
        lower_txt = (text or "").lower()
        if any(w in lower_txt for w in ["good morning", "gm", "suprabhat", "subah", "hello", "hi", "namaste", "pyar", "love"]):
            chosen_emoji = random.choice(["❤️", "🥰", "😍", "😘", "💖"])
        elif any(w in lower_txt for w in ["haha", "hehe", "lol", "lmao", "xd", "rofl", "haso", "joke", "funny"]):
            chosen_emoji = random.choice(["😂", "🤣", "😁", "😆"])
        elif any(w in lower_txt for w in ["?", "kaun", "kya", "kaha", "kyu", "kaisa", "why", "how", "what", "who"]):
            chosen_emoji = random.choice(["🤔", "🤨", "👀"])
        elif any(w in lower_txt for w in ["fire", "op", "bawal", "super", "mast", "king", "pro", "best"]):
            chosen_emoji = random.choice(["🔥", "⚡", "🎉", "👏", "🫡", "💯"])
        elif any(w in lower_txt for w in ["sad", "dukhi", "cry", "bye", "alvida", "miss"]):
            chosen_emoji = random.choice(["🥺", "😢", "💔", "😭"])

        if not chosen_emoji:
            chosen_emoji = random.choice(emojis)

        # React to the message using Telegram Bot API HTTP setMessageReaction
        token = getattr(client, "bot_token", None) or config.BOT_TOKEN
        await send_bot_reaction(token, chat_id, message.id, chosen_emoji)

    except FloodWait as e:
        logger.warning(f"FloodWait of {e.value}s while reacting in chat {message.chat.id}")
    except (ReactionInvalid, ChatAdminRequired):
        pass
    except Exception as e:
        logger.debug(f"Reaction failed for msg {message.id} in chat {message.chat.id}: {e}")
