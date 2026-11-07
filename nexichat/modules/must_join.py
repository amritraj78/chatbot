
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
  Ye file Force Subscribe (Must Join) feature implement karti hai.

Kaise kaam karta hai?
  1. Private chat me aane wale har naye user ko check karti hai ki usne Updates Channel
     (https://t.me/privatethink) join kiya hai ya nahi.
  2. Agar nahi kiya hai, toh bot user ko prompt karti hai join karne ke liye aur
     message processing stop_propagation() se pause kar deti hai.
================================================================================
"""

import logging
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden
from nexichat import nexichat as app
from config import UPDATE_CHNL as MUST_JOIN, OWNER_ID

logger = logging.getLogger(__name__)
_last_admin_warning = 0


@app.on_message(filters.incoming & filters.private, group=-1)
async def must_join_channel(app: Client, msg: Message):
    global _last_admin_warning
    if not MUST_JOIN:
        return

    # Don't restrict the bot owner
    if msg.from_user and msg.from_user.id == int(OWNER_ID):
        return

    try:
        try:
            await app.get_chat_member(MUST_JOIN, msg.from_user.id)
        except UserNotParticipant:
            if isinstance(MUST_JOIN, str) and not MUST_JOIN.startswith("-100") and not MUST_JOIN.isdigit():
                link = f"https://t.me/{MUST_JOIN.lstrip('@')}"
            else:
                try:
                    chat_info = await app.get_chat(MUST_JOIN)
                    link = chat_info.invite_link or f"https://t.me/{MUST_JOIN.lstrip('@')}"
                except Exception:
                    link = f"https://t.me/{MUST_JOIN.lstrip('@')}"
            try:
                await msg.reply_photo(
                    photo="https://envs.sh/Tn_.jpg",
                    caption=(
                        f"**👋 ʜᴇʟʟᴏ {msg.from_user.mention},**\n\n"
                        f"**ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ᴊᴏɪɴ ᴛʜᴇ [ᴄʜᴀɴɴᴇʟ]({link}) ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ʙᴏᴛ.** 🌸"
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("๏ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ๏", url=link)]]
                    ),
                )
                await msg.stop_propagation()
            except ChatWriteForbidden:
                pass
    except ChatAdminRequired:
        now = time.time()
        if now - _last_admin_warning > 1800:
            _last_admin_warning = now
            logger.warning(f"Bot needs to be promoted as Admin in channel @{str(MUST_JOIN).lstrip('@')} for Force Subscribe to verify members.")
            try:
                await app.send_message(
                    int(OWNER_ID),
                    f"⚠️ **[MUST JOIN NOTICE]**\n\n"
                    f"Please promote @{app.me.username} as an **Admin** in your Updates Channel (`@{str(MUST_JOIN).lstrip('@')}`) "
                    f"so the bot can check if users have joined before chatting! ✨"
                )
            except Exception:
                pass
    except Exception as e:
        logger.debug(f"Must join check notice: {e}")
