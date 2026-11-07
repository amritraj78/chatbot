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
  Ye file bot ke served groups (chats) ko MongoDB aur Telegram DB Channel dono
  me track aur save karne ka kaam karti hai.

Kaise kaam karta hai?
  1. Jab bot kisi group me add hota hai ya koi command chalti hai, add_served_chat()
     chat ko MongoDB me save karta hai aur saath me Telegram Channel me bhi log karta hai.
  2. Broadcast (Gcast) aur Stats ke waqt get_served_chats() sari chats return karta hai.
================================================================================
"""

from nexichat import db

chatsdb = db.chatsdb

async def get_served_chats() -> list:
    chats = chatsdb.find({"chat_id": {"$lt": 0}})
    if not chats:
        return []
    chats_list = []
    for chat in await chats.to_list(length=1000000000):
        chats_list.append(chat)
    return chats_list


async def is_served_chat(chat_id: int) -> bool:
    chat = await chatsdb.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True


async def add_served_chat(chat_id: int, client=None, chat=None):
    is_served = await is_served_chat(chat_id)
    if is_served:
        return
    res = await chatsdb.insert_one({"chat_id": chat_id})
    if client and chat:
        try:
            from nexichat.database.telegram_db import log_chat_to_telegram
            await log_chat_to_telegram(client, chat)
        except Exception:
            pass
    return res


async def remove_served_chat(chat_id: int):
    is_served = await is_served_chat(chat_id)
    if not is_served:
        return
    return await chatsdb.delete_one({"chat_id": chat_id})
