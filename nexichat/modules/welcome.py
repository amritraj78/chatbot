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
  Ye file group me Naye Members ke aane par Royal Welcome Card bhejti hai
  aur kisi member ke left hone par Goodbye card bhejti hai.
  
Isme kaun-kaun se commands hain?
  - /welcome - Welcome status check karein.
  - /welcome on - Group me welcome chalu karein.
  - /welcome off - Group me welcome band karein.
================================================================================
"""

import logging
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message
)
import config
from config import OWNER_ID
from nexichat import nexichat, SUDOERS
from nexichat.database.reactions import is_welcome_enabled, set_welcome_enabled
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user

logger = logging.getLogger(__name__)


async def is_admin_or_sudo(client: Client, message: Message) -> bool:
    """Check if the sender is an admin or sudo."""
    if not message.from_user:
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


@nexichat.on_message(filters.command(["welcome"]))
async def welcome_toggle_cmd(client: Client, message: Message):
    """Toggle welcome messages: /welcome on | /welcome off"""
    chat_id = message.chat.id
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await message.reply_text("❌ Ye command sirf groups me use ki ja sakti hai ji!")

    if not await is_admin_or_sudo(client, message):
        return await message.reply_text("❌ Only administrators can change welcome settings.")

    if len(message.command) > 1:
        action = message.command[1].lower()
        if action in ["on", "enable", "yes"]:
            await set_welcome_enabled(chat_id, True)
            return await message.reply_text("🌸 **Welcome messages are now ENABLED for this group!** 🥰")
        elif action in ["off", "disable", "no"]:
            await set_welcome_enabled(chat_id, False)
            return await message.reply_text("🛑 **Welcome messages are now DISABLED for this group.** 😴")

    enabled = await is_welcome_enabled(chat_id)
    status_icon = "🟢 ENABLED" if enabled else "🔴 DISABLED"
    await message.reply_text(
        f"╭━━━━━━━〔 🌸 **WELCOME SETTINGS** 〕━━━━━━━╮\n\n"
        f"  ✦ **ɢʀᴏᴜᴘ :** {message.chat.title}\n"
        f"  ✦ **sᴛᴀᴛᴜs :** `{status_icon}`\n\n"
        f"**Commands:**\n"
        f"• `/welcome on` - Turn Welcome ON\n"
        f"• `/welcome off` - Turn Welcome OFF\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )


@nexichat.on_message(filters.new_chat_members)
async def new_member_welcome(client: Client, message: Message):
    """Sweet girl welcome card when a new member joins."""
    chat_id = message.chat.id
    if not await is_welcome_enabled(chat_id):
        return

    bot_info = await client.get_me()
    bot_name = bot_info.first_name or "VIP AI"

    for member in message.new_chat_members:
        if member.id == bot_info.id:
            # Bot was added to group
            await add_served_chat(chat_id, client=client, chat=message.chat)
            btn = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🌸 Support Group 🌸", url=f"https://t.me/{config.SUPPORT_GRP}"),
                    InlineKeyboardButton("✨ Updates ✨", url=f"https://t.me/{config.UPDATE_CHNL}"),
                ],
                [
                    InlineKeyboardButton("👑 Creator 👑", url=f"https://t.me/{config.OWNER_USERNAME}"),
                ]
            ])
            text = (
                f"╭━━━━━━━〔 ❖ **THANK YOU FOR ADDING ME** ❖ 〕━━━━━━━╮\n\n"
                f"  🌸 **ʜᴇʟʟᴏ {message.chat.title}!** 💖\n\n"
                f"  ɪ ᴀᴍ **{bot_name}**, ʏᴏᴜʀ sᴍᴀʀᴛ **ᴀɪ ɢɪʀʟғʀɪᴇɴᴅ & ᴀᴜᴛᴏ-ʀᴇᴀᴄᴛɪᴏɴ ʙᴏᴛ**! ✨\n"
                f"  Main sabhi messages par cute emojis react karungi aur pyari baatein karungi! 🥰\n\n"
                f"  ✦ **ᴄᴏᴍᴍᴀɴᴅs:** `/help`, `/chatbot on`, `/reactions on`\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
            return await message.reply_text(text, reply_markup=btn)

        # Normal user joined
        await add_served_user(member.id, client=client, user=member)
        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🌸 Support Group 🌸", url=f"https://t.me/{config.SUPPORT_GRP}"),
                InlineKeyboardButton("✨ Updates ✨", url=f"https://t.me/{config.UPDATE_CHNL}"),
            ],
            [
                InlineKeyboardButton("📷 ɪɴsᴛᴀɢʀᴀᴍ", url="https://instagram.com/ex_amrit"),
                InlineKeyboardButton("👻 sɴᴀᴘᴄʜᴀᴛ", url="https://snapchat.com/add/ex_amrit"),
            ]
        ])
        text = (
            f"╭━━━━━━━〔 🌸 **WELCOME TO {message.chat.title}** 🌸 〕━━━━━━━╮\n\n"
            f"  💖 **ʜᴇʏ {member.mention}! ᴡᴇʟᴄᴏᴍᴇ ʙᴀʙʏ** 🥰\n\n"
            f"  ɪ ᴀᴍ **{bot_name}**, ʏᴏᴜʀ ᴀɪ ɢɪʀʟғʀɪᴇɴᴅ & ᴄᴏᴍᴘᴀɴɪᴏɴ! ✨\n"
            f"  Masti se chat karo, stickers bhejo aur pyari pyari baatein karo! 🌸\n\n"
            f"  ✦ **ᴍᴇᴍʙᴇʀ ɪᴅ :** `{member.id}`\n"
            f"  ✦ **ᴄʀᴇᴀᴛᴏʀ :** [ᴀᴍʀɪᴛ ʀᴀᴊ](https://t.me/{config.OWNER_USERNAME}) 👑\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        # Try fetching user's profile photo for visual welcome card
        user_photo = None
        try:
            async for p in client.get_chat_photos(member.id, limit=1):
                user_photo = p.file_id
                break
        except Exception:
            pass

        if user_photo:
            try:
                await message.reply_photo(photo=user_photo, caption=text, reply_markup=btn)
                return
            except Exception:
                pass

        try:
            await message.reply_text(text, reply_markup=btn)
        except Exception:
            pass


@nexichat.on_message(filters.left_chat_member)
async def member_left_goodbye(client: Client, message: Message):
    """Sweet goodbye note when someone leaves."""
    chat_id = message.chat.id
    if not await is_welcome_enabled(chat_id):
        return

    left_user = message.left_chat_member
    if left_user:
        try:
            await message.reply_text(f"🥺 **Alvida {left_user.mention}!** Apna khayal rakhna aur jaldi wapas aana ji! 🌸👋")
        except Exception:
            pass
