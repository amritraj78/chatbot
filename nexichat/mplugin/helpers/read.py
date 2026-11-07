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
  Ye file bot ke sare texts, help menus, messages aur templates ko format karti hai.
  Isme Start, Help, About, Admin, aur Game commands ke clean standard formatted messages hain.
================================================================================
"""

from config import OWNER_USERNAME, SUPPORT_GRP, UPDATE_CHNL
from nexichat import nexichat

bot_name = getattr(nexichat, "name", "VIP REACTION BOT")
bot_username = getattr(nexichat, "username", "Reactions_rebot")

START = """╭────────────────────────────╮
│    ❖ VIP REACTION & AI ❖   │
╰────────────────────────────╯
🌸 **Hey {}! Welcome** 💖

Main aapki pyari **Anshika** hoon! ✨
I chat with you like a real friend, reply to stickers, photos, videos and react to messages! ⚡

╭────────────────────────────╮
│ ✦ **Persona:** Sweet Indian Girl 🌸
│ ✦ **Auto-React:** Groups & Channels ⚡
│ ✦ **Smart Chat:** Text, Sticker, Media 💬
│ ✦ **Memory:** Persistent DM Recall 🧠
│ ✦ **Creator:** [Amrit Raj](https://t.me/Villanns) 👑
╰────────────────────────────╯

✦ **Total Users:** `{}`
✦ **Total Chats:** `{}`
✦ **Uptime:** `{}`

👇 **Tap the buttons below to explore more!**"""

HELP_READ = f"""╭────────────────────────────╮
│    ❖ HELP & COMMANDS ❖     │
╰────────────────────────────╯
🌸 **Click on the buttons below to explore**
All available features, Anshika chat, reactions & tools!

╭────────────────────────────╮
│ • **Reactions:** Auto emoji reacts ⚡
│ • **AI Chatbot:** Sweet girl chat 🌸
│ • **Games:** Fun & love tests 🎮
│ • **Group:** Welcome & tagall 👥
│ • **Tools:** Ping, stats & clone 🛠️
│ • **Owner:** Control & DB switch 👑
╰────────────────────────────╯

💡 **Command Prefix:** All commands use `/`"""

TOOLS_DATA_READ = f"""╭────────────────────────────╮
│    ⚙️ UTILITY TOOLS ⚙️     │
╰────────────────────────────╯
╭────────────────────────────╮
│ • `/start` - Welcome message & menu
│ • `/help` - Full help guide
│ • `/ping` - Check bot latency
│ • `/speedtest` - Server speed test
│ • `/id` - Get user, chat & message ID
│ • `/stats` - View served users & chats
│ • `/link <chat_id>` - Get invite link
│ • `/storage` - Server disk & RAM health 💾
│ • `/exportdb` - Download DB backup 📁
│ • `/broadcast` - Global broadcast (Owner)
╰────────────────────────────╯
📡 **Developer:** [Amrit Raj](https://t.me/{OWNER_USERNAME}) 💞"""

CHATBOT_READ = f"""╭────────────────────────────╮
│    ⚡ AUTO REACTIONS ⚡    │
╰────────────────────────────╯
⚡ **High-Speed Auto-Reaction System**
Reacts instantly to messages in groups, channels and private chats!

╭────────────────────────────╮
│ • `/reactions` - View current settings
│ • `/reactions on` - Turn reactions ON
│ • `/reactions off` - Turn reactions OFF
│ • `/setreactions 👍 ❤️ 🔥` - Set custom reactions
│ • `/resetreactions` - Reset to default
│ • `/clone <token>` - Clone your own bot
│ • `/cloned` - List all cloned bots
│ • `/delclone <token>` - Delete bot clone
│ • `/idclone <session>` - Clone your ID
│ • `/idclones` - List all ID clones
│ • `/delidclone` - Delete your ID clone
╰────────────────────────────╯
📡 **Developer:** [Amrit Raj](https://t.me/{OWNER_USERNAME}) 💞"""

AI_CHATBOT_READ = f"""╭────────────────────────────╮
│  🌸 AI GIRL CHAT & MEMORY  │
╰────────────────────────────╯
💖 **Meet Anshika, your sweet companion!** 🌸
Main ek real school girl (Anshika) ki tarah chat karti hoon, text, stickers, photos aur videos ka natural Hinglish mein reply karti hoon!

╭────────────────────────────╮
│ • `/chatbot` - Open toggle menu
│ • `/chatbot on` - Enable in chat
│ • `/chatbot off` - Disable in chat
│ • `/ask <query>` - Ask anything
│ • `/love <name1> <name2>` - Love calculator %
│ • `/shayri` - Sweet Hindi shayari
│ • `/joke` - Funny jokes
│ • `/draw <prompt>` - AI image generator 🎨
│ • `/setname <nick>` - Set your nickname
│ • `/dbmode` - API / Database switch (Owner) 🗄️
│ • `/api` - Live API usage & quota 📊
╰────────────────────────────╯
💡 **DM Memory:** Main aapki purani sabhi baatein yaad rakhti hoon! 🥰
📡 **Developer:** [Amrit Raj](https://t.me/{OWNER_USERNAME}) 💞"""

SOURCE_READ = f"""╭────────────────────────────╮
│  🌟 PROJECT & COPYRIGHT 🌟  │
╰────────────────────────────╯
✦ **VIP Reaction & Anshika Chatbot**
✦ **Copyright © 2026 [Amrit Raj](https://t.me/{OWNER_USERNAME}). All Rights Reserved.**
✦ Unauthorized copying is strictly prohibited!

╭────────────────────────────╮
│ • **Repo:** [VIP-REACTION-BOT](https://github.com/amritraj78/VIP-REACTION-BOT)
│ • **Support:** [Amrit Feel](https://t.me/{SUPPORT_GRP})
│ • **Creator:** [Amrit Raj](https://t.me/{OWNER_USERNAME})
│ • **License:** Proprietary (Copyright Protected)
╰────────────────────────────╯"""

ADMIN_READ = f"""╭────────────────────────────╮
│    👑 OWNER & ADMIN 👑     │
╰────────────────────────────╯
╭────────────────────────────╮
│ • `/gcast <msg>` - Global broadcast
│ • `/stats` - Served users & chats
│ • `/storage` - Server disk & RAM health 💾
│ • `/exportdb` - Download DB backup 📁
│ • `/ping` - Check bot latency
│ • `/speedtest` - Server speed test
│ • `/id` - Get user, chat & msg ID
│ • `/clone <token>` - Make clone bot
│ • `/cloned` - List all clone bots
│ • `/delclone` - Delete clone bot
│ • `/idclone <session>` - Make ID clone
│ • `/idclones` - List all ID clones
│ • `/delidclone` - Delete ID clone
│ • `/dbmode [on/off]` - Toggle DB fallback mode 🗄️
│ • `/api` - Live AI quota dashboard 📊
╰────────────────────────────╯
📡 **Developer:** [Amrit Raj](https://t.me/{OWNER_USERNAME}) 💞"""

HELP_GAMES_READ = f"""╭────────────────────────────╮
│     🎮 GAMES & FUN 🎮      │
╰────────────────────────────╯
🌸 **Fun, Games & Love Commands**

╭────────────────────────────╮
│ • `/dice` - Dice match vs Anshika 🎲
│ • `🎲 🎯 🏀 ⚽ 🎰` - Send animated emoji
│ • `/toss` - Coin toss (Heads / Tails) 🪙
│ • `/truth` - Spicy truth questions 🤫
│ • `/dare` - Fun dare challenges 🎯
│ • `/flirt` - Sweet romantic flirts 💖
│ • `/roast` - Funny roasts 🔥
│ • `/love <name1> <name2>` - Love % test 🔮
│ • `/couples` - Today's group couple 💑
│ • `/propose` - Propose someone 💍
│ • `/shayri` - Sweet Hindi shayari 🌺
│ • `/joke` - Funny Hindi jokes 😂
│ • `/quote` - Inspirational quotes 🌟
╰────────────────────────────╯
📡 **Developer:** [Amrit Raj](https://t.me/{OWNER_USERNAME}) 💞"""

HELP_GROUP_READ = f"""╭────────────────────────────╮
│   👥 GROUP & WELCOME 👥    │
╰────────────────────────────╯
🌸 **Group Management & Welcome**

╭────────────────────────────╮
│ • `/welcome` - Check welcome status
│ • `/welcome on` - Enable welcome card
│ • `/welcome off` - Disable welcome card
│ • `/tagall <text>` - Tag all members 📢
│ • `/cancel` - Stop tagging 🛑
│ • `/afk [reason]` - Set AFK status 💤
│ • `/security` - Security shield 🛡️
│ • `/antilink` - Toggle anti-link 🚫
│ • `/antispam` - Toggle anti-spam ⚔️
│ • `/profile` or `/me` - View your VIP card
╰────────────────────────────╯
📡 **Developer:** [Amrit Raj](https://t.me/{OWNER_USERNAME}) 💞"""

ABOUT_READ = f"""╭────────────────────────────╮
│    ❖ ABOUT THIS BOT ❖      │
╰────────────────────────────╯
🌸 **VIP Reaction & Anshika Chatbot**
An all-in-one Telegram bot combining instant emoji reactions, a loving girl persona, games & AI tools!

╭────────────────────────────╮
│ • **Creator:** [Amrit Raj](https://t.me/{OWNER_USERNAME}) 👑
│ • **Support:** [Amrit Feel](https://t.me/{SUPPORT_GRP}) 👥
│ • **Updates:** [Private Think](https://t.me/{UPDATE_CHNL}) 📢
│ • **Language:** [Python 3](https://www.python.org) 🐍
│ • **Framework:** [Pyrogram](https://docs.pyrogram.org) ⚡
│ • **Database:** MongoDB & Telegram DB 🧠
╰────────────────────────────╯
✨ **Thank you for using our bot!**"""
