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
  Ye file Cloned Bots ke users aur chats ko separately isolate karke store karti hai.

Kaise kaam karta hai?
  1. Har clone bot ka apna alag collection banta hai `{bot_id}_users` aur `{bot_id}_chats`.
  2. Isse main bot aur cloned bots ka database mix nahi hota.
================================================================================
"""

from nexichat import db as mongodb

cloneownerdb = mongodb.cloneownerdb
clonebotdb = mongodb.clonebotdb

def get_bot_users_collection(bot_id):
    from nexichat import db as mongodb
    return mongodb[f"{bot_id}_users"]

def get_bot_chats_collection(bot_id):
    from nexichat import db as mongodb
    return mongodb[f"{bot_id}_chats"]

async def is_served_cuser(bot_id, user_id: int) -> bool:
    usersdb = get_bot_users_collection(bot_id)
    user = await usersdb.find_one({"user_id": user_id})
    if not user:
        return False
    return True

async def add_served_cuser(bot_id, user_id: int, client=None, user=None):
    usersdb = get_bot_users_collection(bot_id)
    is_served = await is_served_cuser(bot_id, user_id)
    if is_served:
        return
    res = await usersdb.insert_one({"user_id": user_id})
    if user:
        try:
            from nexichat.database.telegram_db import log_user_to_telegram
            await log_user_to_telegram(client, user)
        except Exception:
            pass
    return res

async def get_served_cusers(bot_id) -> list:
    usersdb = get_bot_users_collection(bot_id)
    return await usersdb.find({"user_id": {"$gt": 0}}).to_list(length=None)

async def is_served_cchat(bot_id, chat_id: int) -> bool:
    chatsdb = get_bot_chats_collection(bot_id)
    chat = await chatsdb.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True

async def add_served_cchat(bot_id, chat_id: int, client=None, chat=None):
    chatsdb = get_bot_chats_collection(bot_id)
    is_served = await is_served_cchat(bot_id, chat_id)
    if is_served:
        return
    res = await chatsdb.insert_one({"chat_id": chat_id})
    if chat:
        try:
            from nexichat.database.telegram_db import log_chat_to_telegram
            await log_chat_to_telegram(client, chat)
        except Exception:
            pass
    return res

async def get_served_cchats(bot_id) -> list:
    chatsdb = get_bot_chats_collection(bot_id)
    return await chatsdb.find({"chat_id": {"$lt": 0}}).to_list(length=None)
