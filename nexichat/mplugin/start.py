# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT (Cloned Bot Plugin)
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
#  Licensed under Proprietary Terms. Unauthorized copying is strictly prohibited.
# ---------------------------------------------------------------------------------
"""
================================================================================
  FILE EXPLANATION & HINTS (Cloned Plugin Start)
================================================================================
Is file ka kya kaam hai?
  Ye file Cloned Bots ke liye Welcome (/start) message handle karti hai.
================================================================================
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup
from pyrogram.enums import ChatType
from nexichat.database.clonestats import add_served_cuser, add_served_cchat
from nexichat.mplugin.helpers.inline import DEV_OP

@Client.on_message(filters.command("start"))
async def start_message(client: Client, message: Message):
    bot_id = client.me.id
    if message.chat.type == ChatType.PRIVATE:
        if message.from_user:
            await add_served_cuser(bot_id, message.from_user.id)
    else:
        await add_served_cchat(bot_id, message.chat.id)

    first_name = message.from_user.first_name if message.from_user else "Friend"
    bot_info = await client.get_me()
    bot_title = (bot_info.first_name or "VIP REACTION").upper()

    text = (
        f"🌸 **ᴀɴsʜɪᴋᴀ ᴀɪ ᴄʜᴀᴛʙᴏᴛ**\n"
        f"ᴠ2.0\n\n"
        f"ʜᴇʏ {first_name} 👋\n\n"
        f"ɪ ᴀᴍ ᴀɴsʜɪᴋᴀ, ᴀ ʜɪɢʜ-ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ ᴀɪ ᴄʜᴀᴛʙᴏᴛ ᴅᴇsɪɢɴᴇᴅ ᴛᴏ ᴄʜᴀᴛ, ʀᴇᴀᴄᴛ ᴀɴᴅ ᴇɴᴛᴇʀᴛᴀɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘs:\n\n"
        f"• 🌸 **sᴡᴇᴇᴛ ɪɴᴅɪᴀɴ ɢɪʀʟ ᴄʜᴀᴛ** (ᴛᴇxᴛ, sᴛɪᴄᴋᴇʀs, ᴍᴇᴅɪᴀ)\n"
        f"• ⚡ **ᴀᴜᴛᴏ-ʀᴇᴀᴄᴛɪᴏɴs** (ɢʀᴏᴜᴘs & ᴄʜᴀɴɴᴇʟs)\n"
        f"• 🧠 **ᴘᴇʀsɪsᴛᴇɴᴛ ᴅᴍ ᴍᴇᴍᴏʀʏ ʀᴇᴄᴀʟʟ**\n"
        f"• 🎮 **ғᴜɴ ɢᴀᴍᴇs, ʟᴏᴠᴇ ᴛᴇsᴛs & sʜᴀʏᴀʀɪs**\n"
        f"• 👑 **ᴄʀᴇᴀᴛᴏʀ:** [ᴀᴍʀɪᴛ ʀᴀᴊ](https://t.me/Villanns)\n\n"
        f"ᴊᴜsᴛ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ɢʀᴀɴᴛ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs!"
    )
    await message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(DEV_OP),
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command(["help", "commands", "menu"]))
async def help_command(client: Client, message: Message):
    """Display full categorized help menu with interactive inline buttons for clone bots."""
    from nexichat.mplugin.helpers.inline import HELP_BTN
    from nexichat.mplugin.helpers.read import HELP_READ
    await message.reply_text(
        text=HELP_READ,
        reply_markup=InlineKeyboardMarkup(HELP_BTN),
        disable_web_page_preview=True,
    )
