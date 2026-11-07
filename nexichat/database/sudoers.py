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
  Ye file Bot ke authorized Sudoers (co-admins) ko database me save, fetch aur
  remove karne ka kaam karti hai.

Kaise kaam karta hai?
  1. get_sudoers(): MongoDB me `sudoers` collection se authorized user IDs fetch karta hai.
  2. add_sudo(user_id): Naye sudo user ko add karta hai.
  3. remove_sudo(user_id): Sudo user ko remove karta hai.
================================================================================
"""

from nexichat import mongodb

sudoersdb = mongodb.sudoers

async def get_sudoers() -> list:
    sudoers = sudoersdb.find_one({"sudo": "sudo"})
    if hasattr(sudoers, "__await__"):
        sudoers = await sudoers
    if not sudoers:
        return []
    return sudoers.get("sudoers", [])


async def add_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    if user_id not in sudoers:
        sudoers.append(user_id)
    res = sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    if hasattr(res, "__await__"):
        await res
    return True


async def remove_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    if user_id in sudoers:
        sudoers.remove(user_id)
    res = sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    if hasattr(res, "__await__"):
        await res
    return True

