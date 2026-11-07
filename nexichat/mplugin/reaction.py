# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT (Cloned Bot Plugin)
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
#  Licensed under Proprietary Terms. Unauthorized copying is strictly prohibited.
# ---------------------------------------------------------------------------------
"""
================================================================================
  FILE EXPLANATION & HINTS (Cloned Plugin Reaction Engine)
================================================================================
Is file ka kya kaam hai?
  Ye file Cloned Bots ke liye High-Speed Auto Reaction Engine hai. Cloned bots
  bhi context-based emojis (morning/love, funny, questions, fire) turant react
  karti hain.
================================================================================
"""

import random
import re
import logging
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait, ReactionInvalid, ChatAdminRequired
from pyrogram.types import Message
from nexichat.database.reactions import (
    DEFAULT_EMOJIS,
    get_chat_emojis,
    is_reactions_enabled,
    reset_chat_emojis,
    set_chat_emojis,
    set_reactions_enabled,
)
from nexichat.database.clonestats import add_served_cchat, add_served_cuser
from nexichat.mplugin.helpers.cowner import is_owner

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
                fb_payload = dict(payload, reaction=[{"type": "emoji", "emoji": "❤️"}])
                fb_resp = await loop.run_in_executor(
                    None,
                    lambda: _http_session.post(url, json=fb_payload, timeout=3)
                )
                if fb_resp.json().get("ok"):
                    return True
            logger.debug(f"Cloned Bot API reaction notice: {desc}")
            return False
        return True
    except Exception as e:
        logger.debug(f"Failed to send cloned bot reaction: {e}")
        return False


async def is_clone_admin_or_owner(client: Client, message: Message) -> bool:
    """Check if the user is an admin of the chat or owner of the cloned bot."""
    if not message.from_user:
        if message.sender_chat and message.sender_chat.id == message.chat.id:
            return True
        return False

    user_id = message.from_user.id
    bot_id = client.me.id

    if await is_owner(bot_id, user_id):
        return True

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return True
        except Exception:
            return False

    return False


@Client.on_message(filters.command(["reactions", "reaction"]))
async def reaction_status_toggle(client: Client, message: Message):
    """View status or toggle reactions for cloned bots."""
    chat_id = message.chat.id

    if len(message.command) > 1:
        if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
            if not await is_clone_admin_or_owner(client, message):
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


@Client.on_message(filters.command(["setreactions", "setreaction"]))
async def set_reactions_cmd(client: Client, message: Message):
    """Set custom emojis for this chat on cloned bots."""
    chat_id = message.chat.id

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
        if not await is_clone_admin_or_owner(client, message):
            return await message.reply_text("❌ **Only chat administrators can change reaction emojis.**")

    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ **Please provide one or more emojis after the command.**\n\n"
            "**Example:** `/setreactions 👍 ❤️ 🔥 🥰 👏`"
        )

    raw_args = message.text.split(None, 1)[1]
    extracted = [e.strip() for e in re.findall(r'[^\s,]+', raw_args) if e.strip()]

    if not extracted:
        return await message.reply_text("❌ **No valid emojis found. Please provide valid Telegram reaction emojis.**")

    await set_chat_emojis(chat_id, extracted)
    await message.reply_text(
        f"✅ **Custom reaction emojis updated successfully!**\n\n"
        f"**Active Emojis ({len(extracted)}):** {' '.join(extracted)}"
    )


@Client.on_message(filters.command(["resetreactions", "resetreaction"]))
async def reset_reactions_cmd(client: Client, message: Message):
    """Reset reaction emojis back to default list on cloned bots."""
    chat_id = message.chat.id

    if message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
        if not await is_clone_admin_or_owner(client, message):
            return await message.reply_text("❌ **Only chat administrators can reset reaction emojis.**")

    await reset_chat_emojis(chat_id)
    await message.reply_text(
        f"🔄 **Reaction emojis have been reset to default!**\n\n"
        f"**Default Emojis:** {' '.join(DEFAULT_EMOJIS)}"
    )


@Client.on_message(
    (filters.incoming & (filters.group | filters.private | filters.channel)),
    group=10
)
async def clone_auto_react_handler(client: Client, message: Message):
    """Automatically reacts to messages and channel posts on cloned bots."""
    try:
        # Ignore empty, service messages or media group extra triggers
        if message.empty or getattr(message, "service", False):
            return

        # Ignore own messages (critical for userbot ID clones)
        if client.me and message.from_user and message.from_user.id == client.me.id:
            return

        text = message.text or message.caption
        if text and (text.startswith("/") or text.startswith("!") or text.startswith(".")):
            return

        chat_id = message.chat.id
        bot_id = client.me.id

        if message.chat.type == ChatType.PRIVATE and message.from_user:
            await add_served_cuser(bot_id, message.from_user.id)
        elif message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
            await add_served_cchat(bot_id, chat_id)

        if not await is_reactions_enabled(chat_id):
            return

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

        token = getattr(client, "bot_token", None) or getattr(client, "token", None)
        if token:
            await send_bot_reaction(token, chat_id, message.id, chosen_emoji)
        else:
            try:
                await client.send_reaction(chat_id, message.id, chosen_emoji)
            except Exception as e:
                logger.debug(f"Userbot reaction notice: {e}")

    except FloodWait as e:
        logger.warning(f"FloodWait of {e.value}s while reacting in chat {message.chat.id}")
    except (ReactionInvalid, ChatAdminRequired):
        pass
    except Exception as e:
        logger.debug(f"Clone reaction failed: {e}")
