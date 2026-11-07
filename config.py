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
  Ye file pooray project ki Central Configuration file hai.
  Isme:
  1. Telegram API credentials (API_ID, API_HASH, BOT_TOKEN) load hote hain.
  2. Owner ID (5423666218 / @Villanns), Support Group (@amrit_feel) aur
     Updates Channel (@privatethink) set hote hain.
  3. Environment variables (.env file ya Koyeb Environment settings) se values
     fetch ki jaati hain.
================================================================================
"""

import os
import asyncio
from os import getenv

# Ensure an active event loop exists for Python 3.12+ compatibility with Pyrogram sync
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    if os.path.exists(".env"):
        with open(".env") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())


API_ID = "6435225"
# -------------------------------------------------------------
API_HASH = "4e984ea35f854762dcde906dce426c2d"
# --------------------------------------------------------------
BOT_TOKEN = getenv("BOT_TOKEN", None)
MONGO_URL = getenv("MONGO_URL", None)
OWNER_ID = int(getenv("OWNER_ID", "5423666218"))
SUPPORT_GRP = getenv("SUPPORT_GRP", "amrit_feel")
UPDATE_CHNL = getenv("UPDATE_CHNL", "privatethink")
DATABASE_GROUP = getenv("DATABASE_GROUP", "-1004415957871")
DATABASE_CHANNEL = getenv("DATABASE_CHANNEL", "Yaarwinprofits")
DATABASE_CHAT = getenv("DATABASE_CHAT", "-1004415957871")
OWNER_USERNAME = getenv("OWNER_USERNAME", "Villanns")
INSTAGRAM = getenv("INSTAGRAM", "ex_amrit")
SNAPCHAT = getenv("SNAPCHAT", "ex_amrit")
# Multi-Provider AI API Keys with Automatic Failover
_raw_groq = getenv("GROQ_API_KEYS", getenv("GROQ_API_KEY", ""))
GROQ_API_KEYS = [k.strip() for k in _raw_groq.split(",") if k.strip()]
GROQ_API_KEY = GROQ_API_KEYS[0] if GROQ_API_KEYS else None

_raw_gemini = getenv("GEMINI_API_KEYS", getenv("GEMINI_API_KEY", ""))
GEMINI_API_KEYS = [k.strip() for k in _raw_gemini.split(",") if k.strip()]
GEMINI_API_KEY = GEMINI_API_KEYS[0] if GEMINI_API_KEYS else None

NVIDIA_API_KEY = getenv("NVIDIA_API_KEY", None)
KOYEB_PUBLIC_URL = getenv("KOYEB_PUBLIC_URL", getenv("PING_URL", None))
STORAGE_THRESHOLD = int(getenv("STORAGE_THRESHOLD", "90"))

