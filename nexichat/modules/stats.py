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
  Ye file User Statistics aur VIP Profile manage karti hai:
  1. /stats - Total served users aur groups ki count batati hai.
  2. /id - User ID, Chat ID, aur Replied Message ID nikal kar deti hai.
  3. /profile ya /me - User ka VIP Official ID Card, nickname, aur bot uptime dikhati hai.
================================================================================
"""

import time
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions

from config import OWNER_ID, SUPPORT_GRP
from nexichat import _boot_, get_readable_time, nexichat, SUDOERS
from nexichat.database.chats import get_served_chats
from nexichat.database.users import get_served_users
from nexichat.database.chatbot import get_user_nickname

logger = logging.getLogger(__name__)


@nexichat.on_message(filters.command("stats"))
async def stats(cli: Client, message: Message):
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    
    api_info = ""
    user_id = message.from_user.id if message.from_user else 0
    if user_id in SUDOERS or user_id == int(OWNER_ID):
        try:
            from nexichat.database.chatbot import get_api_usage_stats
            st = await get_api_usage_stats()
            api_info = (
                f"\n\n📊 **VIP AI API USAGE**\n"
                f"────────────────────────────\n"
                f"✦ **Groq AI:** `{st['groq_calls']}`/`{st['groq_quota']}` ({st['groq_used_pct']}% used | {st['groq_left_pct']}% left)\n"
                f"✦ **Gemini AI:** `{st['gemini_calls']}`/`{st['gemini_quota']}` ({st['gemini_used_pct']}% used | {st['gemini_left_pct']}% left)\n"
                f"✦ **Total Queries:** `{st['total_calls']}` | **DB Fallback:** `{st['db_fallback_calls']}`\n"
                f"────────────────────────────"
            )
        except Exception:
            pass

    await message.reply_text(
        f"""{(await cli.get_me()).mention} Reaction Bot Stats:

➻ **Chats:** {chats}
➻ **Users:** {users}{api_info}"""
    )


@nexichat.on_message(filters.command("id"))
async def getid(client: Client, message: Message):
    chat = message.chat
    your_id = message.from_user.id if message.from_user else 0
    message_id = message.id
    reply = message.reply_to_message

    text = f"**[ᴍᴇssᴀɢᴇ ɪᴅ:]({message.link})** `{message_id}`\n"
    text += f"**[ʏᴏᴜʀ ɪᴅ:](tg://user?id={your_id})** `{your_id}`\n"

    if not getattr(message, "command", None):
        message.command = (getattr(message, "text", "") or "").split()

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"**[ᴜsᴇʀ ɪᴅ:](tg://user?id={user_id})** `{user_id}`\n"
        except Exception:
            return await message.reply_text("ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ.", quote=True)

    chat_username = getattr(chat, "username", None)
    if chat_username:
        text += f"**[ᴄʜᴀᴛ ɪᴅ:](https://t.me/{chat_username})** `{chat.id}`\n\n"
    else:
        text += f"**ᴄʜᴀᴛ ɪᴅ :** `{chat.id}`\n\n"

    if (
        not getattr(reply, "empty", True)
        and not message.forward_from_chat
        and not reply.sender_chat
    ):
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ:]({reply.link})** `{reply.id}`\n"
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ:](tg://user?id={reply.from_user.id})** `{reply.from_user.id}`\n\n"

    if reply and reply.forward_from_chat:
        text += f"ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, {reply.forward_from_chat.title}, ʜᴀs ᴀɴ ɪᴅ ᴏғ `{reply.forward_from_chat.id}`\n\n"

    if reply and reply.sender_chat:
        text += f"ɪᴅ ᴏғ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ, ɪs `{reply.sender_chat.id}`"

    await message.reply_text(
        text,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        parse_mode=ParseMode.DEFAULT,
    )


@nexichat.on_message(filters.command(["profile", "me", "myinfo"]))
async def user_profile(client: Client, message: Message):
    user = message.from_user
    if not user:
        return
    
    uptime = get_readable_time(time.time() - _boot_)
    is_owner = (user.id == int(OWNER_ID))
    role = "👑 Owner / Boss" if is_owner else "💎 VIP Member"
    
    nickname = await get_user_nickname(user.id)
    nick_str = f"• **Nickname:** `{nickname}`\n" if nickname else ""
    
    text = f"""╭────────────────────────────╮
│    👑 USER VIP PROFILE 👑  │
╰────────────────────────────╯
🌸 **Hello {user.mention}!**
Here is your official VIP profile card.

╭────────────────────────────╮
│ • **Name:** {user.first_name}
│ • **User ID:** `{user.id}`
│ • **Username:** @{user.username if user.username else 'None'}
│ {nick_str}• **Status:** {role}
│ • **DC ID:** `{user.dc_id or 'Unknown'}`
│ • **Bot Uptime:** `{uptime}`
╰────────────────────────────╯
📡 **Powered by:** [Amrit Feel](https://t.me/{SUPPORT_GRP}) 💞"""
    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📷 Instagram", url="https://instagram.com/ex_amrit"),
            InlineKeyboardButton("👻 Snapchat", url="https://snapchat.com/add/ex_amrit"),
        ],
        [
            InlineKeyboardButton("👑 Creator", url="https://t.me/Villanns"),
            InlineKeyboardButton("⦿ Close ⦿", callback_data="CLOSE"),
        ]
    ])
    await message.reply_text(text, reply_markup=btn, link_preview_options=LinkPreviewOptions(is_disabled=True))
