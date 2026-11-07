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
  Ye file Reactions aur Welcome Card ke database settings save karti hai:
  1. DEFAULT_EMOJIS: Agar chat me koi custom emoji set na ho toh default emojis.
  2. is_reactions_enabled / set_reactions_enabled: Reactions on/off status.
  3. get_chat_emojis / set_chat_emojis / reset_chat_emojis: Custom emoji list.
  4. is_welcome_enabled / set_welcome_enabled: Welcome card on/off status.
================================================================================
"""

from typing import List
from nexichat import db

reactionsdb = db.reactions

# Default emojis used when no custom emojis are set for a chat (All 100% supported by Telegram Bot API)
DEFAULT_EMOJIS = ["👍", "❤️", "🔥", "🥰", "👏", "🎉", "🤩", "👌", "😍", "⚡", "🫡", "💯"]

async def is_reactions_enabled(chat_id: int) -> bool:
    """Check if automatic reactions are enabled for this chat (defaults to True)."""
    chat = await reactionsdb.find_one({"chat_id": chat_id})
    if not chat:
        return True
    return chat.get("enabled", True)

async def set_reactions_enabled(chat_id: int, enabled: bool):
    """Enable or disable reactions for a specific chat."""
    await reactionsdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": enabled}},
        upsert=True
    )

async def get_chat_emojis(chat_id: int) -> List[str]:
    """Get the list of emojis configured for a chat. Returns DEFAULT_EMOJIS if unset."""
    chat = await reactionsdb.find_one({"chat_id": chat_id})
    if not chat or "emojis" not in chat or not chat["emojis"]:
        return DEFAULT_EMOJIS
    return chat["emojis"]

async def set_chat_emojis(chat_id: int, emojis: List[str]):
    """Set custom reaction emojis for a specific chat."""
    await reactionsdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"emojis": emojis}},
        upsert=True
    )

async def reset_chat_emojis(chat_id: int):
    """Reset a chat's custom emojis back to the default list."""
    await reactionsdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"emojis": DEFAULT_EMOJIS}},
        upsert=True
    )


welcome_db = db.welcome_status

async def is_welcome_enabled(chat_id: int) -> bool:
    """Check if welcome messages are enabled for a chat (defaults to True)."""
    doc = await welcome_db.find_one({"chat_id": chat_id})
    if not doc:
        return True
    return doc.get("enabled", True)

async def set_welcome_enabled(chat_id: int, enabled: bool):
    """Enable or disable welcome messages for a chat."""
    await welcome_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": enabled}},
        upsert=True
    )


security_db = db.security_status

async def is_antilink_enabled(chat_id: int) -> bool:
    """Check if Anti-Link is enabled for a group (defaults to False)."""
    doc = await security_db.find_one({"chat_id": chat_id})
    if not doc:
        return False
    return doc.get("antilink", False)

async def set_antilink_enabled(chat_id: int, enabled: bool):
    """Enable or disable Anti-Link for a group."""
    await security_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"antilink": enabled}},
        upsert=True
    )

async def is_antispam_enabled(chat_id: int) -> bool:
    """Check if Anti-Spam is enabled for a group (defaults to True)."""
    doc = await security_db.find_one({"chat_id": chat_id})
    if not doc:
        return True
    return doc.get("antispam", True)

async def set_antispam_enabled(chat_id: int, enabled: bool):
    """Enable or disable Anti-Spam for a group."""
    await security_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"antispam": enabled}},
        upsert=True
    )
