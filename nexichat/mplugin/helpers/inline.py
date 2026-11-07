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
  Reactions Settings, Tools, Games, Support Links) ko standard clean font me define karti hai.
================================================================================
"""

from pyrogram.types import InlineKeyboardButton

from config import SUPPORT_GRP, UPDATE_CHNL
from nexichat import nexichat

START_BOT = [
    [
        InlineKeyboardButton(text="🛠️ Open Commands ⚙️", callback_data="HELP"),
    ],
]

DEV_OP = [
    [
        InlineKeyboardButton(
            text="➕ Add Me To Your Group ➕",
            url=f"https://t.me/{getattr(nexichat, 'username', 'Reactions_rebot')}?startgroup=true",
        ),
    ],
    [
        InlineKeyboardButton(text="📚 Help & Commands", callback_data="HELP"),
        InlineKeyboardButton(text="☁️ About Me", callback_data="ABOUT"),
    ],
    [
        InlineKeyboardButton(text="👥 Support", url=f"https://t.me/{SUPPORT_GRP}"),
        InlineKeyboardButton(text="📢 Updates", url=f"https://t.me/{UPDATE_CHNL}"),
    ],
]

PNG_BTN = [
    [
        InlineKeyboardButton(text="🛠️ Open Commands ⚙️", callback_data="HELP"),
    ],
    [
        InlineKeyboardButton(
            text="⦿ Close ⦿",
            callback_data="CLOSE",
        ),
    ],
]

BACK = [
    [
        InlineKeyboardButton(text="⦿ Back ⦿", callback_data="BACK"),
    ],
]

HELP_BTN = [
    [
        InlineKeyboardButton(text="🌸 AI Girl Chat", callback_data="AI_CHATBOT_CMD"),
        InlineKeyboardButton(text="⚡ Reactions", callback_data="CHATBOT_CMD"),
    ],
    [
        InlineKeyboardButton(text="🎮 Games & Fun", callback_data="HELP_GAMES"),
        InlineKeyboardButton(text="👥 Group & Welcome", callback_data="HELP_GROUP"),
    ],
    [
        InlineKeyboardButton(text="🛠️ Tools & Utils", callback_data="TOOLS_DATA"),
        InlineKeyboardButton(text="👑 Owner & Admin", callback_data="ADMINS"),
    ],
    [
        InlineKeyboardButton(text="☁️ About Me", callback_data="ABOUT"),
        InlineKeyboardButton(text="⦿ Back ⦿", callback_data="BACK"),
    ],
    [
        InlineKeyboardButton(text="⦿ Close ⦿", callback_data="CLOSE"),
    ],
]

CLOSE_BTN = [
    [
        InlineKeyboardButton(text="⦿ Close ⦿", callback_data="CLOSE"),
    ],
]

CHATBOT_ON = [
    [
        InlineKeyboardButton(text="🟢 Enable", callback_data="cb_enable_chatbot"),
        InlineKeyboardButton(text="🔴 Disable", callback_data="cb_disable_chatbot"),
    ],
]

MUSIC_BACK_BTN = [
    [
        InlineKeyboardButton(text="Soon", callback_data="soon"),
    ],
]

S_BACK = [
    [
        InlineKeyboardButton(text="⦿ Back ⦿", callback_data="SBACK"),
        InlineKeyboardButton(text="⦿ Close ⦿", callback_data="CLOSE"),
    ],
]

CHATBOT_BACK = [
    [
        InlineKeyboardButton(text="⦿ Back ⦿", callback_data="CHATBOT_BACK"),
        InlineKeyboardButton(text="⦿ Close ⦿", callback_data="CLOSE"),
    ],
]

HELP_START = [
    [
        InlineKeyboardButton(text="« Help »", callback_data="HELP"),
        InlineKeyboardButton(text="⦿ Close ⦿", callback_data="CLOSE"),
    ],
]

HELP_BUTN = [
    [
        InlineKeyboardButton(text="« Features »", callback_data="HELP"),
    ],
    [
        InlineKeyboardButton(text="⦿ Close ⦿", callback_data="CLOSE"),
    ],
]

ABOUT_BTN = [
    [
        InlineKeyboardButton(text="👥 Support Group", url=f"https://t.me/{SUPPORT_GRP}"),
        InlineKeyboardButton(text="📢 Updates Channel", url=f"https://t.me/{UPDATE_CHNL}"),
    ],
    [
        InlineKeyboardButton(text="📷 Instagram", url="https://instagram.com/ex_amrit"),
        InlineKeyboardButton(text="👻 Snapchat", url="https://snapchat.com/add/ex_amrit"),
    ],
    [
        InlineKeyboardButton(text="👑 Creator", url="https://t.me/Villanns"),
        InlineKeyboardButton(text="🌟 Source Code", url="https://github.com/amritraj78/VIP-REACTION-BOT"),
    ],
    [
        InlineKeyboardButton(text="« Help »", callback_data="HELP"),
        InlineKeyboardButton(text="⦿ Back ⦿", callback_data="BACK"),
    ],
]
