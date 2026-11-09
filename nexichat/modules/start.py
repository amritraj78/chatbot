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
  Ye file bot ka Welcome Screen (/start) handle karti hai.
  Jab bhi koi user ya group bot ko start karta hai, ye unhe swagat sandesh aur
  interactive inline buttons (Help, About, Support, Updates) dikhati hai.
================================================================================
"""

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup
from pyrogram.enums import ChatType
from nexichat import nexichat
from nexichat.database.users import add_served_user
from nexichat.database.chats import add_served_chat
from nexichat.modules.helpers.inline import DEV_OP, get_start_buttons

@nexichat.on_message(filters.command("start"))
async def start_message(client: Client, message: Message):
    if message.chat.type == ChatType.PRIVATE:
        if message.from_user:
            await add_served_user(message.from_user.id, client=client, user=message.from_user)
    else:
        await add_served_chat(message.chat.id, client=client, chat=message.chat)

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
    bot_uname = getattr(bot_info, "username", None) or getattr(client, "username", None)
    await message.reply_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(get_start_buttons(bot_uname)),
        disable_web_page_preview=True,
    )


@nexichat.on_message(filters.command(["help", "commands", "menu"]))
async def help_command(client: Client, message: Message):
    """Display full categorized help menu with interactive inline buttons."""
    from nexichat.modules.helpers.inline import HELP_BTN
    from nexichat.modules.helpers.read import HELP_READ
    await message.reply_text(
        text=HELP_READ,
        reply_markup=InlineKeyboardMarkup(HELP_BTN),
        disable_web_page_preview=True,
    )

