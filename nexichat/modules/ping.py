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
  Ye file bot ki latency (ping speed in milliseconds), uptime, aur system status
  (CPU, RAM, Disk) check karti hai jab koi user /ping command bhejta hai.

Kaise kaam karta hai?
  1. User /ping command deta hai.
  2. Bot command receive hote hi time calculate karta hai.
  3. Sentinel module se real-time RAM & Disk metrics fetch karta hai.
  4. Response me ping ms, RAM%, Disk%, Uptime, aur owner links show karta hai.
================================================================================
"""

import random
import time
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import OWNER_USERNAME
from nexichat import _boot_, get_readable_time, nexichat
from nexichat.database.chats import add_served_chat
from nexichat.database.users import add_served_user
from nexichat.database.clonestats import add_served_cuser, add_served_cchat



PNG_BTN = [
    [
        InlineKeyboardButton(text="🛠️ σρεи ¢σммαиdꜱ ⚙️", callback_data="HELP"),
    ],
    [
        InlineKeyboardButton(
            text="⦿ ᴄʟᴏsᴇ ⦿",
            callback_data="CLOSE",
        ),
    ],
]




IMG = [
    "https://graph.org/file/210751796ff48991b86a3.jpg",
    "https://graph.org/file/7b4924be4179f70abcf33.jpg",
    "https://graph.org/file/f6d8e64246bddc26b4f66.jpg",
    "https://graph.org/file/63d3ec1ca2c965d6ef210.jpg",
    "https://graph.org/file/9f12dc2a668d40875deb5.jpg",
    "https://graph.org/file/0f89cd8d55fd9bb5130e1.jpg",
    "https://graph.org/file/e5eb7673737ada9679b47.jpg",
    "https://graph.org/file/2e4dfe1fa5185c7ff1bfd.jpg",
    "https://graph.org/file/36af423228372b8899f20.jpg",
    "https://graph.org/file/c698fa9b221772c2a4f3a.jpg",
    "https://graph.org/file/61b08f41855afd9bed0ab.jpg",
    "https://graph.org/file/744b1a83aac76cb3779eb.jpg",
    "https://graph.org/file/814cd9a25dd78480d0ce1.jpg",
    "https://graph.org/file/e8b472bcfa6680f6c6a5d.jpg",
]


async def bot_sys_stats():
    bot_uptime = int(time.time() - _boot_)
    UP = f"{get_readable_time((bot_uptime))}"
    try:
        from nexichat.modules.sentinel import get_disk_stats, get_ram_stats
        disk = get_disk_stats()
        ram = get_ram_stats()
        cpu = "Online"
        mem = f"{ram['percent']}%"
        disk_str = f"{disk['percent']}%"
        return UP, cpu, mem, disk_str
    except Exception:
        return UP, "Online", "Normal", "Normal"


@nexichat.on_message(filters.command("ping"))
async def ping(client: Client, message: Message):
    bot_id = client.me.id
    start = datetime.now()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp_msg = await message.reply_photo(
        photo=random.choice(IMG),
        caption="ᴘɪɴɢɪɴɢ...",
    )

    ms = (datetime.now() - start).microseconds / 1000
    await resp_msg.edit_caption(
        caption=f"нey вαву!!\n{(await client.get_me()).mention} ʀᴇᴀᴄᴛɪᴏɴ ʙᴏᴛ ιѕ alιve 🥀 αnd worĸιng ғιne wιтн a pιng oғ\n\n**➥** `{ms}` ms\n**➲ ᴄᴘᴜ:** {CPU}\n**➲ ʀᴀᴍ:** {RAM}\n**➲ ᴅɪsᴋ:** {DISK}\n**➲ ᴜᴘᴛɪᴍᴇ »** {UP}\n\n<b>||**๏ мαdє ωιтн ❣️ ву [ᴠɪᴘ ʙᴏʏ](https://t.me/{OWNER_USERNAME}) **||</b>",
        reply_markup=InlineKeyboardMarkup(PNG_BTN),
    )
    if message.chat.type == ChatType.PRIVATE:
        await add_served_cuser(bot_id, message.from_user.id)
        await add_served_user(message.from_user.id)
    else:
        await add_served_cchat(bot_id, message.chat.id)
        await add_served_chat(message.chat.id)
