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
  Ye file Koyeb ya VPS server ki internet connection speed (download speed,
  upload speed, latency) measure karti hai using Ookla speedtest engine.

Kaise kaam karta hai?
  1. User /speedtest ya /spt command bhejta hai.
  2. Background asyncio executor thread me speedtest run hota hai (taki bot freeze na ho).
  3. Server ping, ISP, location aur download/upload result image ke sath reply karta hai.
================================================================================
"""

import asyncio
import speedtest
from pyrogram import filters
from pyrogram.types import Message
from nexichat import nexichat

server_result_template = (
    "✯ sᴩᴇᴇᴅᴛᴇsᴛ ʀᴇsᴜʟᴛs ✯\n\n"
    "ᴄʟɪᴇɴᴛ:\n"
    "» ɪsᴩ: {isp}\n"
    "» ᴄᴏᴜɴᴛʀʏ: {country}\n\n"
    "sᴇʀᴠᴇʀ:\n"
    "» ɴᴀᴍᴇ: {server_name}\n"
    "» ᴄᴏᴜɴᴛʀʏ: {server_country}, {server_cc}\n"
    "» sᴩᴏɴsᴏʀ: {sponsor}\n"
    "» ʟᴀᴛᴇɴᴄʏ: {latency} ms\n"
    "» ᴩɪɴɢ: {ping} ms"
)

def run_speedtest():
    test = speedtest.Speedtest()
    test.get_best_server()
    test.download()
    test.upload()
    results = test.results.dict()
    share_link = test.results.share() if test.results.share() else None
    results["share"] = share_link
    return results

@nexichat.on_message(filters.command(["speedtest", "spt"], prefixes=["/"]))
async def speedtest_function(client, message: Message):
    m = await message.reply_text("ʀᴜɴɴɪɴɢ ꜱᴩᴇᴇᴅ...")
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_speedtest)

        output = server_result_template.format(
            isp=result["client"]["isp"],
            country=result["client"]["country"],
            server_name=result["server"]["name"],
            server_country=result["server"]["country"],
            server_cc=result["server"]["cc"],
            sponsor=result["server"]["sponsor"],
            latency=result["server"]["latency"],
            ping=result["ping"],
        )

        if result["share"]:
            await message.reply_photo(photo=result["share"], caption=output)
        else:
            await message.reply_text(output)

        await m.delete()
    except Exception as e:
        await m.edit_text(f"Error: {e}")
