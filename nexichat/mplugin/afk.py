# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT (Cloned Bot Plugin)
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
  Ye file Cloned Bots ke liye AFK (Away From Keyboard) System provide karti hai.
================================================================================
"""

import time
from typing import Dict
from pyrogram import Client, filters
from pyrogram.enums import ChatAction, MessageEntityType
from pyrogram.types import Message

from nexichat.database.chatbot import set_user_afk, get_user_afk, remove_user_afk

_afk_notified: Dict[int, float] = {}


def format_duration(seconds: float) -> str:
    """Format seconds into readable time string."""
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds} seconds"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minutes"
    hours = minutes // 60
    rem_min = minutes % 60
    if hours < 24:
        return f"{hours}h {rem_min}m"
    days = hours // 24
    rem_hours = hours % 24
    return f"{days}d {rem_hours}h"


@Client.on_message(filters.command(["afk"]))
async def afk_command(client: Client, message: Message):
    """Set AFK status with optional reason."""
    user = message.from_user
    if not user:
        return

    reason = " ".join(message.command[1:]).strip() if len(message.command) > 1 else "Busy with life / offline"
    await set_user_afk(user.id, reason)

    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass

    text = (
        f"╭━━━━━━━〔 😴 **AFK STATUS SET** 〕━━━━━━━╮\n\n"
        f"  ✦ **ᴜsᴇʀ :** {user.mention}\n"
        f"  ✦ **sᴛᴀᴛᴜs :** Away From Keyboard (AFK)\n"
        f"  ✦ **ʀᴇᴀsᴏɴ :** `{reason}`\n\n"
        f"  🌸 *Anshika: Jaldi aana ji, hum sab aapko bohot miss karenge!* ✨\n\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    await message.reply_text(text)


@Client.on_message(filters.incoming & (filters.group | filters.private), group=1)
async def afk_listener(client: Client, message: Message):
    """
    1. If an AFK user speaks, remove their AFK and welcome them back.
    2. If anyone mentions or replies to an AFK user, notify them.
    """
    global _afk_notified
    user = message.from_user
    if not user:
        return

    # 1. Check if the sender was AFK
    user_afk = await get_user_afk(user.id)
    if user_afk and not (message.text and message.text.startswith(("/afk", "!afk"))):
        await remove_user_afk(user.id)
        elapsed = time.time() - user_afk.get("time", time.time())
        duration_str = format_duration(elapsed)
        
        try:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        except Exception:
            pass

        text = (
            f"╭━━━━━━━〔 🌸 **WELCOME BACK!** 〕━━━━━━━╮\n\n"
            f"  ✦ **ᴜsᴇʀ :** {user.mention} is now back online! 🥰\n"
            f"  ✦ **ᴀғᴋ ᴅᴜʀᴀᴛɪᴏɴ :** `{duration_str}`\n\n"
            f"  🌸 *Anshika: Aap wapas aa gaye, sach mein bohot khushi hui ji!* 💖✨\n\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        await message.reply_text(text)

    # 2. Check if this message replies to an AFK user
    now = time.time()
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user = message.reply_to_message.from_user
        if replied_user.id != user.id and not replied_user.is_bot:
            replied_afk = await get_user_afk(replied_user.id)
            if replied_afk:
                last_notice = _afk_notified.get(replied_user.id, 0)
                if now - last_notice > 12:
                    _afk_notified[replied_user.id] = now
                    elapsed = now - replied_afk.get("time", now)
                    dur_str = format_duration(elapsed)
                    reason_str = replied_afk.get("reason", "Busy")
                    text = (
                        f"╭━━━━━━━〔 💤 **AFK NOTICE** 〕━━━━━━━╮\n\n"
                        f"  ✦ **ᴜsᴇʀ :** {replied_user.mention} is currently AFK!\n"
                        f"  ✦ **ʀᴇᴀsᴏɴ :** `{reason_str}`\n"
                        f"  ✦ **sɪɴᴄᴇ :** `{dur_str} ago`\n\n"
                        f"  🌸 *Anshika: Unko thoda time do na ji, aate hi reply karenge!* 🌸\n\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
                    )
                    await message.reply_text(text)

    # 3. Check if someone was mentioned via @username or text mention
    if message.entities:
        for ent in message.entities:
            target_user = None
            if ent.type == MessageEntityType.TEXT_MENTION and ent.user:
                target_user = ent.user
            if target_user and target_user.id != user.id and not target_user.is_bot:
                t_afk = await get_user_afk(target_user.id)
                if t_afk:
                    last_notice = _afk_notified.get(target_user.id, 0)
                    if now - last_notice > 12:
                        _afk_notified[target_user.id] = now
                        elapsed = now - t_afk.get("time", now)
                        dur_str = format_duration(elapsed)
                        reason_str = t_afk.get("reason", "Busy")
                        text = (
                            f"╭━━━━━━━〔 💤 **AFK NOTICE** 〕━━━━━━━╮\n\n"
                            f"  ✦ **ᴜsᴇʀ :** {target_user.mention} is currently AFK!\n"
                            f"  ✦ **ʀᴇᴀsᴏɴ :** `{reason_str}`\n"
                            f"  ✦ **sɪɴᴄᴇ :** `{dur_str} ago`\n\n"
                            f"  🌸 *Anshika: Jaise hi aayenge, main unhe bata dungi ji!* 🌸\n\n"
                            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
                        )
                        await message.reply_text(text)
