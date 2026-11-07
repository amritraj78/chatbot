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
  Ye file Cloned Bots ke liye Tag-All / Mention-All functionality provide karti hai.
================================================================================
"""

import asyncio
import logging
from typing import Dict
from pyrogram import Client, filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from config import OWNER_ID
from nexichat import SUDOERS

logger = logging.getLogger(__name__)

ACTIVE_TAGALL: Dict[int, bool] = {}


async def is_admin_or_sudo(client: Client, message: Message) -> bool:
    """Check if sender is group admin, sudoer, or owner."""
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


@Client.on_message(filters.command(["tagall", "mention", "all"]))
async def tagall_command(client: Client, message: Message):
    """Mention all group members in safe batches of 5 with Anshika emojis."""
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await message.reply_text("❌ **Ye command sirf groups mein kaam karta hai ji!** 🌸")

    if not await is_admin_or_sudo(client, message):
        return await message.reply_text("❌ **Only administrators can use tagall!** 😴")

    chat_id = message.chat.id
    if ACTIVE_TAGALL.get(chat_id):
        return await message.reply_text("⚠️ **Ek tag-all process pehle se chal raha hai ji!**\nUse `/cancel` to stop it.")

    custom_text = " ".join(message.command[1:]).strip() if len(message.command) > 1 else "Utho sabhi, gupshup ka time ho gaya! 🌸✨"
    ACTIVE_TAGALL[chat_id] = True

    status_msg = await message.reply_text("📢 **ᴛᴀɢ-ᴀʟʟ sᴛᴀʀᴛᴇᴅ...** 🌸\n*Stop karne ke liye `/cancel` likhein!*")

    emojis = ["🌸", "✨", "💖", "🦋", "💫"]
    batch = []
    total_tagged = 0

    try:
        async for member in client.get_chat_members(chat_id):
            if not ACTIVE_TAGALL.get(chat_id):
                break

            if member.user and not member.user.is_bot and not member.user.is_deleted:
                batch.append(member.user)
                if len(batch) >= 5:
                    lines = [f"{emojis[i % len(emojis)]} {u.mention}" for i, u in enumerate(batch)]
                    tag_text = (
                        f"╭━━━━━━━〔 📢 **ANSHIKA ANNOUNCEMENT** 〕━━━━━━━╮\n\n"
                        f"  💬 **ᴍᴇssᴀɢᴇ :** {custom_text}\n\n"
                        + "\n".join(lines) +
                        f"\n\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
                    )
                    try:
                        await client.send_message(chat_id, tag_text)
                        total_tagged += len(batch)
                    except FloodWait as e:
                        await asyncio.sleep(e.value + 1)
                        await client.send_message(chat_id, tag_text)
                    except Exception as ex:
                        logger.debug(f"Tagall send notice: {ex}")

                    batch = []
                    await asyncio.sleep(2.5)

        if batch and ACTIVE_TAGALL.get(chat_id):
            lines = [f"{emojis[i % len(emojis)]} {u.mention}" for i, u in enumerate(batch)]
            tag_text = (
                f"╭━━━━━━━〔 📢 **ANSHIKA ANNOUNCEMENT** 〕━━━━━━━╮\n\n"
                f"  💬 **ᴍᴇssᴀɢᴇ :** {custom_text}\n\n"
                + "\n".join(lines) +
                f"\n\n╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
            try:
                await client.send_message(chat_id, tag_text)
                total_tagged += len(batch)
            except Exception:
                pass

        if ACTIVE_TAGALL.get(chat_id):
            await message.reply_text(f"✅ **Tag-all completed successfully!** 🌸\nTotal **{total_tagged}** members ko tag kar diya ji! 🥰")
    except Exception as e:
        logger.error(f"Error in tagall: {e}")
        await message.reply_text("❌ Tag-all mein thodi pareshani aayi ji!")
    finally:
        ACTIVE_TAGALL[chat_id] = False


@Client.on_message(filters.command(["cancel", "stopmention", "stoptag"]))
async def cancel_tagall_command(client: Client, message: Message):
    """Cancel an active tag-all process in this group."""
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return

    if not await is_admin_or_sudo(client, message):
        return await message.reply_text("❌ **Only administrators can cancel tagall!**")

    chat_id = message.chat.id
    if ACTIVE_TAGALL.get(chat_id):
        ACTIVE_TAGALL[chat_id] = False
        await message.reply_text("🛑 **Tag-all process rok diya gaya hai ji!** 🌸")
    else:
        await message.reply_text("ℹ️ **Koi active tag-all process nahi chal raha hai!**")
