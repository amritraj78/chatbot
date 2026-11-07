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
  Ye file bot ke private chat users ko track aur save karti hai MongoDB aur
  Telegram Database Channel me.

Kaise kaam karta hai?
  1. Jab koi naya user bot ko private me start karta hai, add_served_user() use
     database me record karta hai aur Telegram channel par user details log karta hai.
  2. Broadcast (Gcast) ke time get_served_users() se sare users fetch kiye jaate hain.
================================================================================
"""

from nexichat import db

usersdb = db.users


async def is_served_user(user_id: int) -> bool:
    user = await usersdb.find_one({"user_id": user_id})
    if not user:
        return False
    return True


async def get_served_users() -> list:
    users_list = []
    async for user in usersdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list


async def add_served_user(user_id: int, client=None, user=None):
    is_served = await is_served_user(user_id)
    if is_served:
        return
    res = await usersdb.insert_one({"user_id": user_id})
    if client and user:
        try:
            from nexichat.database.telegram_db import log_user_to_telegram
            await log_user_to_telegram(client, user)
        except Exception:
            pass
    return res
