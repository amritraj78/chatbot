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
  Ye file bot ke Telegram Inline Keyboards aur Buttons (Start Menu, Help Menu,
  Reactions Settings, Tools, Games, Support Links) ko premium aesthetic
  Small Caps font me define karti hai.
================================================================================
"""

from pyrogram.types import InlineKeyboardButton

from config import SUPPORT_GRP, UPDATE_CHNL
from nexichat import nexichat

START_BOT = [
    [
        InlineKeyboardButton(text="🛠️ ᴏᴘᴇɴ ᴄᴏᴍᴍᴀɴᴅs ⚙️", callback_data="HELP"),
    ],
]

DEV_OP = [
    [
        InlineKeyboardButton(
            text="➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕",
            url=f"https://t.me/{getattr(nexichat, 'username', 'Reactions_rebot')}?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(text="📚 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs", callback_data="HELP"),
        InlineKeyboardButton(text="☁️ ᴀʙᴏᴜᴛ ᴍᴇ", callback_data="ABOUT"),
    ],
    [
        InlineKeyboardButton(text="👥 sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_GRP}"),
        InlineKeyboardButton(text="📢 ᴜᴘᴅᴀᴛᴇs", url=f"https://t.me/{UPDATE_CHNL}"),
    ],
]

PNG_BTN = [
    [
        InlineKeyboardButton(text="🛠️ ᴏᴘᴇɴ ᴄᴏᴍᴍᴀɴᴅs ⚙️", callback_data="HELP"),
    ],
    [
        InlineKeyboardButton(
            text="⦿ ᴄʟᴏsᴇ ⦿",
            callback_data="CLOSE",
        ),
    ],
]

BACK = [
    [
        InlineKeyboardButton(text="⦿ ʙᴀᴄᴋ ⦿", callback_data="BACK"),
    ],
]

HELP_BTN = [
    [
        InlineKeyboardButton(text="🌸 ᴀɪ ɢɪʀʟ ᴄʜᴀᴛ", callback_data="AI_CHATBOT_CMD"),
        InlineKeyboardButton(text="⚡ ʀᴇᴀᴄᴛɪᴏɴs", callback_data="CHATBOT_CMD"),
    ],
    [
        InlineKeyboardButton(text="🎮 ɢᴀᴍᴇs & ғᴜɴ", callback_data="HELP_GAMES"),
        InlineKeyboardButton(text="👥 ɢʀᴏᴜᴘ & ᴡᴇʟᴄᴏᴍᴇ", callback_data="HELP_GROUP"),
    ],
    [
        InlineKeyboardButton(text="🛠️ ᴛᴏᴏʟs & ᴜᴛɪʟs", callback_data="TOOLS_DATA"),
        InlineKeyboardButton(text="👑 ᴏᴡɴᴇʀ & ᴀᴅᴍɪɴ", callback_data="ADMINS"),
    ],
    [
        InlineKeyboardButton(text="☁️ ᴀʙᴏᴜᴛ ᴍᴇ", callback_data="ABOUT"),
        InlineKeyboardButton(text="⦿ ʙᴀᴄᴋ ⦿", callback_data="BACK"),
    ],
    [
        InlineKeyboardButton(text="⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE"),
    ],
]

CLOSE_BTN = [
    [
        InlineKeyboardButton(text="⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE"),
    ],
]

CHATBOT_ON = [
    [
        InlineKeyboardButton(text="🟢 ᴇɴᴀʙʟᴇ", callback_data="cb_enable_chatbot"),
        InlineKeyboardButton(text="🔴 ᴅɪsᴀʙʟᴇ", callback_data="cb_disable_chatbot"),
    ],
]

MUSIC_BACK_BTN = [
    [
        InlineKeyboardButton(text="Soon", callback_data="soon"),
    ],
]

S_BACK = [
    [
        InlineKeyboardButton(text="⦿ ʙᴀᴄᴋ ⦿", callback_data="SBACK"),
        InlineKeyboardButton(text="⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE"),
    ],
]

CHATBOT_BACK = [
    [
        InlineKeyboardButton(text="⦿ ʙᴀᴄᴋ ⦿", callback_data="CHATBOT_BACK"),
        InlineKeyboardButton(text="⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE"),
    ],
]

HELP_START = [
    [
        InlineKeyboardButton(text="« ʜᴇʟᴘ »", callback_data="HELP"),
        InlineKeyboardButton(text="⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE"),
    ],
]

HELP_BUTN = [
    [
        InlineKeyboardButton(text="« ғᴇᴀᴛᴜʀᴇs »", callback_data="HELP"),
    ],
    [
        InlineKeyboardButton(text="⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE"),
    ],
]

ABOUT_BTN = [
    [
        InlineKeyboardButton(text="👥 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url=f"https://t.me/{SUPPORT_GRP}"),
        InlineKeyboardButton(text="📢 ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{UPDATE_CHNL}"),
    ],
    [
        InlineKeyboardButton(text="📷 ɪɴsᴛᴀɢʀᴀᴍ", url="https://instagram.com/ex_amrit"),
        InlineKeyboardButton(text="👻 sɴᴀᴘᴄʜᴀᴛ", url="https://snapchat.com/add/ex_amrit"),
    ],
    [
        InlineKeyboardButton(text="👑 ᴄʀᴇᴀᴛᴏʀ", url="https://t.me/Villanns"),
        InlineKeyboardButton(text="🌟 sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ", url="https://github.com/amritraj78/VIP-REACTION-BOT"),
    ],
    [
        InlineKeyboardButton(text="« ʜᴇʟᴘ »", callback_data="HELP"),
        InlineKeyboardButton(text="⦿ ʙᴀᴄᴋ ⦿", callback_data="BACK"),
    ],
]
