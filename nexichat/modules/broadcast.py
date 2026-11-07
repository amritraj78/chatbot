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
  Ye file Owner & Sudoers ke liye Global Broadcast (/gcast) aur Database Export (/exportdb) handle karti hai:
  1. /gcast <message> - Sabhi served groups aur users ko ek sath broadcast message bhejta hai.
  2. /exportdb - Poore bot ka data (Learned Q&As, Nicknames, Users, Chats) ka JSON file bana kar
     Owner (@Villanns) ko Telegram par bhej deta hai for instant 1-click backup.
================================================================================
"""

import os
import json
import asyncio
import logging
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from config import OWNER_ID
from nexichat import nexichat as app, SUDOERS
from nexichat.database.clonestats import get_served_cchats, get_served_cusers
from nexichat.database.chats import get_served_chats
from nexichat.database.users import get_served_users

logger = logging.getLogger(__name__)

AUTO_SLEEP = 5
IS_BROADCASTING = False
broadcast_lock = asyncio.Lock()


@app.on_message(filters.command(["broadcast", "gcast"]) & SUDOERS)
async def broadcast_message(client: Client, message: Message):
    global IS_BROADCASTING
    bot_id = (await client.get_me()).id
    user_id = message.from_user.id
        
    async with broadcast_lock:
        if IS_BROADCASTING:
            return await message.reply_text(
                "A broadcast is already in progress. Please wait for it to complete."
            )

        IS_BROADCASTING = True
        try:
            query = message.text.split(None, 1)[1].strip()
        except IndexError:
            query = message.text.strip()
        except Exception as eff:
            return await message.reply_text(
                f"**Error**: {eff}"
            )
        try:
            if message.reply_to_message:
                broadcast_content = message.reply_to_message
                broadcast_type = "reply"
                flags = {
                    "-pin": "-pin" in query,
                    "-pinloud": "-pinloud" in query,
                    "-nogroup": "-nogroup" in query,
                    "-user": "-user" in query,
                }
            else:
                if len(message.command) < 2:
                    return await message.reply_text(
                        "**Please provide text after the command or reply to a message for broadcasting.**"
                    )
                
                flags = {
                    "-pin": "-pin" in query,
                    "-pinloud": "-pinloud" in query,
                    "-nogroup": "-nogroup" in query,
                    "-user": "-user" in query,
                }

                for flag in flags:
                    query = query.replace(flag, "").strip()

                if not query:
                    return await message.reply_text(
                        "Please provide a valid text message or a flag: -pin, -nogroup, -pinloud, -user"
                    )

                
                broadcast_content = query
                broadcast_type = "text"
            

            await message.reply_text("**Started broadcasting...**")

            if not flags.get("-nogroup", False):
                sent = 0
                pin_count = 0
                chats = await get_served_cchats(bot_id)

                for chat in chats:
                    chat_id = int(chat["chat_id"])
                    if chat_id == message.chat.id:
                        continue
                    try:
                        if broadcast_type == "reply":
                            m = await client.forward_messages(
                                chat_id, message.chat.id, [broadcast_content.id]
                            )
                        else:
                            m = await client.send_message(
                                chat_id, text=broadcast_content
                            )
                        sent += 1

                        if flags.get("-pin", False) or flags.get("-pinloud", False):
                            try:
                                await m.pin(
                                    disable_notification=flags.get("-pin", False)
                                )
                                pin_count += 1
                            except Exception as e:
                                continue

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"FloodWait of {flood_time} seconds encountered for chat {chat_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"Skipping chat {chat_id} due to excessive FloodWait."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        
                        continue

                await message.reply_text(
                    f"**Broadcasted to {sent} chats and pinned in {pin_count} chats.**"
                )

            if flags.get("-user", False):
                susr = 0
                users = await get_served_cusers(bot_id)

                for user in users:
                    user_id = int(user["user_id"])
                    try:
                        if broadcast_type == "reply":
                            m = await client.forward_messages(
                                user_id, message.chat.id, [broadcast_content.id]
                            )
                        else:
                            m = await client.send_message(
                                user_id, text=broadcast_content
                            )
                        susr += 1

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"FloodWait of {flood_time} seconds encountered for user {user_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"Skipping user {user_id} due to excessive FloodWait."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        
                        continue

                await message.reply_text(f"**Broadcasted to {susr} users.**")

        finally:
            IS_BROADCASTING = False


@app.on_message(filters.command(["exportdb", "backupdb"]) & (SUDOERS | filters.user(int(OWNER_ID))))
async def export_database(client, message):
    status_msg = await message.reply_text("⏳ **Exporting database, please wait...**")
    try:
        import json
        from nexichat.database.chatbot import _qa_cache, _nicknames_cache, _stickers_cache, _replies_cache
        from nexichat.database.chats import get_served_chats
        from nexichat.database.users import get_served_users

        served_users = await get_served_users()
        served_chats = await get_served_chats()

        backup_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "stats": {
                "served_users_count": len(served_users),
                "served_chats_count": len(served_chats),
                "qa_memory_count": len(_qa_cache),
                "nicknames_count": len(_nicknames_cache),
                "stickers_count": len(_stickers_cache),
                "learned_replies_count": len(_replies_cache)
            },
            "qa_memory": _qa_cache,
            "nicknames": {str(k): v for k, v in _nicknames_cache.items()},
            "served_users": [u.get("user_id") for u in served_users if isinstance(u, dict)],
            "served_chats": [c.get("chat_id") for c in served_chats if isinstance(c, dict)],
        }

        filename = f"db_backup_{int(time.time())}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

        await message.reply_document(
            document=filename,
            caption=(
                f"📁 **VIP Database Backup**\n\n"
                f"👥 Users: {len(served_users)}\n"
                f"💬 Chats: {len(served_chats)}\n"
                f"🧠 Q&A Learned: {len(_qa_cache)}\n"
                f"💖 Nicknames: {len(_nicknames_cache)}\n\n"
                f"👑 **Owner Backup Complete!**"
            )
        )
        if os.path.exists(filename):
            os.remove(filename)
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ **Export failed:** `{e}`")
