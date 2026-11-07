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
  Ye file group security, anti-spam aur anti-link shield ko handle karti hai:
  1. /antilink on|off - Group me links (t.me/..., http://...) auto-delete karta hai.
  2. /antispam on|off - Mass-mention aur spam forwards ko auto-delete karta hai.
  3. /security ya /shield - Group security dashboard aur toggle buttons dikhata hai.
  4. Admins aur Sudoers safe rehte hain (unke links delete nahi hote).
================================================================================
"""

import re
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from config import OWNER_ID
from nexichat import nexichat, SUDOERS
from nexichat.database.reactions import (
    is_antilink_enabled,
    set_antilink_enabled,
    is_antispam_enabled,
    set_antispam_enabled
)

logger = logging.getLogger(__name__)

LINK_REGEX = re.compile(r"(https?://\S+|t\.me/\S+|telegram\.me/\S+|www\.\S+)", re.IGNORECASE)


async def is_admin_or_sudo(client: Client, message: Message) -> bool:
    """Verify if user is chat admin, owner, or bot sudoer."""
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


def get_security_markup(antilink: bool, antispam: bool) -> InlineKeyboardMarkup:
    """Inline keyboard for interactive security dashboard."""
    link_btn = "🔴 Turn OFF Link Shield" if antilink else "🟢 Turn ON Link Shield"
    spam_btn = "🔴 Turn OFF Spam Shield" if antispam else "🟢 Turn ON Spam Shield"
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(link_btn, callback_data="sec_toggle_antilink"),
        ],
        [
            InlineKeyboardButton(spam_btn, callback_data="sec_toggle_antispam"),
        ],
        [
            InlineKeyboardButton("⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE"),
        ]
    ])


@nexichat.on_message(filters.command(["security", "shield", "protect"]))
async def security_status_cmd(client: Client, message: Message):
    """View and toggle group security settings."""
    chat_id = message.chat.id
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await message.reply_text("❌ **Security shield sirf groups ke liye hai ji!** 🌸")

    if not await is_admin_or_sudo(client, message):
        return await message.reply_text("❌ **Only administrators can view or modify security settings.**")

    antilink = await is_antilink_enabled(chat_id)
    antispam = await is_antispam_enabled(chat_id)

    link_icon = "🟢 **ACTIVE (Auto-Delete Links)**" if antilink else "🔴 **INACTIVE**"
    spam_icon = "🟢 **ACTIVE (Auto-Delete Mass Spams)**" if antispam else "🔴 **INACTIVE**"

    text = (
        f"╭━━━━━━━〔 🛡️ **GROUP SECURITY SHIELD** 〕━━━━━━━╮\n\n"
        f"  ✦ **ᴄʜᴀᴛ :** {message.chat.title}\n"
        f"  ✦ **ᴀɴᴛɪ-ʟɪɴᴋ :** {link_icon}\n"
        f"  ✦ **ᴀɴᴛɪ-sᴘᴀᴍ :** {spam_icon}\n\n"
        f"**Quick Commands:**\n"
        f"• `/antilink on` | `/antilink off` - Toggle link deletion\n"
        f"• `/antispam on` | `/antispam off` - Toggle spam deletion\n\n"
        f"🛡️ *Protects against scam bots, invite spam & mass forwards!*"
    )
    await message.reply_text(text, reply_markup=get_security_markup(antilink, antispam))


@nexichat.on_callback_query(filters.regex(r"^sec_toggle_(antilink|antispam)$"))
async def security_callback_handler(client: Client, query: CallbackQuery):
    """Handle interactive toggle buttons for security."""
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    if user_id not in SUDOERS and user_id != int(OWNER_ID):
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                return await query.answer("❌ Only administrators can modify security shield!", show_alert=True)
        except Exception:
            return await query.answer("❌ Verification failed.", show_alert=True)

    action = query.data.split("_")[2]
    if action == "antilink":
        curr = await is_antilink_enabled(chat_id)
        await set_antilink_enabled(chat_id, not curr)
        await query.answer(f"Anti-Link set to {not curr}!")
    elif action == "antispam":
        curr = await is_antispam_enabled(chat_id)
        await set_antispam_enabled(chat_id, not curr)
        await query.answer(f"Anti-Spam set to {not curr}!")

    antilink = await is_antilink_enabled(chat_id)
    antispam = await is_antispam_enabled(chat_id)

    link_icon = "🟢 **ACTIVE (Auto-Delete Links)**" if antilink else "🔴 **INACTIVE**"
    spam_icon = "🟢 **ACTIVE (Auto-Delete Mass Spams)**" if antispam else "🔴 **INACTIVE**"

    text = (
        f"╭━━━━━━━〔 🛡️ **GROUP SECURITY SHIELD** 〕━━━━━━━╮\n\n"
        f"  ✦ **ᴄʜᴀᴛ :** {query.message.chat.title}\n"
        f"  ✦ **ᴀɴᴛɪ-ʟɪɴᴋ :** {link_icon}\n"
        f"  ✦ **ᴀɴᴛɪ-sᴘᴀᴍ :** {spam_icon}\n\n"
        f"**Quick Commands:**\n"
        f"• `/antilink on` | `/antilink off` - Toggle link deletion\n"
        f"• `/antispam on` | `/antispam off` - Toggle spam deletion\n\n"
        f"🛡️ *Protects against scam bots, invite spam & mass forwards!*"
    )
    try:
        await query.message.edit_text(text, reply_markup=get_security_markup(antilink, antispam))
    except Exception:
        pass


@nexichat.on_message(filters.command("antilink"))
async def antilink_cmd(client: Client, message: Message):
    """Command toggle for Anti-Link: /antilink on|off"""
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await message.reply_text("❌ Group command only!")
    if not await is_admin_or_sudo(client, message):
        return await message.reply_text("❌ Admin command only!")

    if len(message.command) > 1:
        arg = message.command[1].lower()
        if arg in ["on", "enable", "yes"]:
            await set_antilink_enabled(message.chat.id, True)
            return await message.reply_text("🛡️ **Anti-Link Shield is now ENABLED!**\nUnauthorized links will be automatically deleted! 🌸")
        elif arg in ["off", "disable", "no"]:
            await set_antilink_enabled(message.chat.id, False)
            return await message.reply_text("🛑 **Anti-Link Shield is now DISABLED.**")
    return await message.reply_text("ℹ️ **Usage:** `/antilink on` or `/antilink off`")


@nexichat.on_message(filters.command("antispam"))
async def antispam_cmd(client: Client, message: Message):
    """Command toggle for Anti-Spam: /antispam on|off"""
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await message.reply_text("❌ Group command only!")
    if not await is_admin_or_sudo(client, message):
        return await message.reply_text("❌ Admin command only!")

    if len(message.command) > 1:
        arg = message.command[1].lower()
        if arg in ["on", "enable", "yes"]:
            await set_antispam_enabled(message.chat.id, True)
            return await message.reply_text("🛡️ **Anti-Spam Shield is now ENABLED!**\nMass-mentions and spam forwards will be deleted! 🌸")
        elif arg in ["off", "disable", "no"]:
            await set_antispam_enabled(message.chat.id, False)
            return await message.reply_text("🛑 **Anti-Spam Shield is now DISABLED.**")
    return await message.reply_text("ℹ️ **Usage:** `/antispam on` or `/antispam off`")


# High-priority security listener
@nexichat.on_message(
    (filters.group & ~filters.bot),
    group=1
)
async def auto_security_guard(client: Client, message: Message):
    """
    Automatic guard checking incoming messages for unauthorized links and mass spam.
    Runs with high priority (group=1) before reaction and chatbot handlers.
    """
    if not message.from_user:
        return

    chat_id = message.chat.id
    raw_text = message.text or message.caption or ""

    # Don't restrict group admins
    if await is_admin_or_sudo(client, message):
        return

    # 1. Anti-Link Filter
    if await is_antilink_enabled(chat_id):
        if LINK_REGEX.search(raw_text):
            try:
                await message.delete()
                warn = await message.reply_text(
                    f"⚠️ {message.from_user.mention}! Is group me unauthorized links allowed nahi hain ji! 🌸"
                )
                await asyncio.sleep(5)
                await warn.delete()
                return
            except Exception as e:
                logger.debug(f"Anti-link action notice: {e}")

    # 2. Anti-Spam Filter (mass mentions >= 5)
    if await is_antispam_enabled(chat_id):
        mention_count = len(re.findall(r"@\w+", raw_text))
        if mention_count >= 5:
            try:
                await message.delete()
                warn = await message.reply_text(
                    f"⚠️ {message.from_user.mention}! Mass spamming allowed nahi hai ji! 😴"
                )
                await asyncio.sleep(5)
                await warn.delete()
                return
            except Exception as e:
                logger.debug(f"Anti-spam action notice: {e}")
