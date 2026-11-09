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
  Ye file Cloned Bots ke liye invite links aur group info export feature provide karti hai.

Kaise kaam karta hai?
  1. Clone bot owner ko permissions verify karne ke baad group invite link aur details deta hai.
================================================================================
"""

import os

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message
from nexichat.mplugin.helpers import is_owner


@Client.on_message(filters.command("givelink"))
async def give_link_command(client, message):
    chat = message.chat.id
    bot_id = client.me.id
    user_id = message.from_user.id
    if not await is_owner(bot_id, user_id):
        await message.reply_text("You don't have permission to use this command on this bot.")
        return
    link = await client.export_chat_invite_link(chat)
    await message.reply_text(f"**Here's the invite link for this chat:**\n\n{link}")


@Client.on_message(filters.command(["link", "invitelink"], prefixes=["/", "!", "%", ",", ".", "@", "#"]))
async def link_command_handler(client: Client, message: Message):
    bot_id = client.me.id
    user_id = message.from_user.id if message.from_user else 0
    if not await is_owner(bot_id, user_id):
        await message.reply_text("You don't have permission to use this command on this bot.")
        return
    if len(message.command) != 2:
        await message.reply("**Invalid usage. Correct format: /link group_id**")
        return

    group_id = message.command[1].strip()
    file_name = f"group_info_{group_id.replace('@', '')}.txt"

    try:
        try:
            chat_target = int(group_id)
        except ValueError:
            chat_target = group_id

        chat = await client.get_chat(chat_target)

        if chat is None:
            await message.reply("**Unable to get information for the specified group ID.**")
            return

        try:
            invite_link = await client.export_chat_invite_link(chat.id)
        except FloodWait as e:
            await message.reply(f"**FloodWait: {e.value} seconds.**")
            return

        group_data = {
            "id": chat.id,
            "type": str(chat.type),
            "title": chat.title,
            "members_count": chat.members_count,
            "description": chat.description,
            "invite_link": invite_link,
            "is_verified": chat.is_verified,
            "is_restricted": chat.is_restricted,
            "is_creator": chat.is_creator,
            "is_scam": chat.is_scam,
            "is_fake": chat.is_fake,
            "dc_id": chat.dc_id,
            "has_protected_content": chat.has_protected_content,
        }

        with open(file_name, "w", encoding="utf-8") as file:
            for key, value in group_data.items():
                file.write(f"{key}: {value}\n")

        await client.send_document(
            chat_id=message.chat.id,
            document=file_name,
            caption=f"📋 **ɢʀᴏᴜᴘ ɪɴғᴏʀᴍᴀᴛɪᴏɴ**\n• **ᴛɪᴛʟᴇ:** {chat.title}\n• **ɪᴅ:** `{chat.id}`\n\n🌸 **sᴄʀᴀᴘᴇᴅ ʙʏ:** @{client.username}",
        )

    except Exception as e:
        await message.reply(f"**Error:** {str(e)}")

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)
