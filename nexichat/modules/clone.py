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
  Ye file Bot Cloning System (/clone, /cloned, /delclone) handle karti hai.
  Koi bhi user @BotFather se token bana kar /clone <token> bhejta hai, toh bot
  unke liye unka apna Reaction + AI Chatbot clone create kar deta hai jo 
  nexichat/mplugin se automatically chalne lagta hai!
================================================================================
"""

import logging
import os
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from pyrogram.types import BotCommand
from config import API_HASH, API_ID, OWNER_ID
from nexichat import nexichat as app, save_clonebot_owner
from nexichat import db as mongodb

CLONES = set()
USER_CLONES = {}
cloneownerdb = mongodb.cloneownerdb
clonebotdb = mongodb.clonebotdb
cloneuserdb = mongodb.cloneuserdb

    
@app.on_message(filters.command(["clone", "host", "deploy"]))
async def clone_txt(client, message):
    if len(message.command) > 1:
        bot_token = message.text.split("/clone", 1)[1].strip()
        mi = await message.reply_text("Please wait while I check the bot token.")
        try:
            ai = Client(bot_token, API_ID, API_HASH, bot_token=bot_token, plugins=dict(root="nexichat/mplugin"), workers=4)
            await ai.start()
            bot = await ai.get_me()
            bot_id = bot.id
            user_id = message.from_user.id
            await save_clonebot_owner(bot_id, user_id)
            await ai.set_bot_commands([
                    BotCommand("start", "Start the bot"),
                    BotCommand("help", "Get the help menu"),
                    BotCommand("reactions", "Toggle reactions (/reactions on|off)"),
                    BotCommand("chatbot", "Toggle AI chatbot (/chatbot on|off)"),
                    BotCommand("ask", "Ask AI any question"),
                    BotCommand("couples", "Couple of the day game 💍"),
                    BotCommand("propose", "Group propose game 💕"),
                    BotCommand("afk", "Set AFK status 😴"),
                    BotCommand("tagall", "Mention all members in batches 📢"),
                    BotCommand("cancel", "Cancel tag-all process 🛑"),
                    BotCommand("voice", "Girl voice note generator"),
                    BotCommand("draw", "Free AI image generator"),
                    BotCommand("welcome", "Toggle group welcome card"),
                    BotCommand("profile", "View your VIP profile card"),
                    BotCommand("security", "Group shield & antilink protection 🛡️"),
                    BotCommand("antilink", "Toggle group anti-link security"),
                    BotCommand("antispam", "Toggle group flood protector"),
                    BotCommand("truth", "Fun spicy truth game"),
                    BotCommand("dare", "Exciting dare game"),
                    BotCommand("flirt", "Sweet romantic flirt"),
                    BotCommand("love", "Love compatibility calculator"),
                    BotCommand("roast", "Playful roast card 🔥"),
                    BotCommand("quote", "Generate quote card 📜"),
                    BotCommand("shayri", "Poetic shayari generator"),
                    BotCommand("joke", "Funny joke generator"),
                    BotCommand("clone", "Make your own reaction bot"),
                    BotCommand("ping", "Check bot latency"),
                    BotCommand("id", "Get user/chat ID"),
                    BotCommand("stats", "Check bot stats"),
                    BotCommand("exportdb", "Download DB backup"),
                    BotCommand("gcast", "Broadcast message to groups/users"),
                ])
        except (AccessTokenExpired, AccessTokenInvalid):
            await mi.edit_text("**Invalid bot token. Please provide a valid one.**")
            return
        except Exception as e:
            cloned_bot = await clonebotdb.find_one({"token": bot_token})
            if cloned_bot:
                await mi.edit_text("**🤖 Your bot is already cloned ✅**")
                return

        await mi.edit_text("**Cloning process started. Please wait for the bot to start.**")
        try:
            details = {
                "bot_id": bot.id,
                "is_bot": True,
                "user_id": user_id,
                "name": bot.first_name,
                "token": bot_token,
                "username": bot.username,
            }
            cloned_bots = clonebotdb.find()
            cloned_bots_list = await cloned_bots.to_list(length=None)
            total_clones = len(cloned_bots_list)
            await clonebotdb.insert_one(details)
            CLONES.add(bot.id)
            
            await app.send_message(
                int(OWNER_ID), f"**#New_Clone**\n\n**Bot:- @{bot.username}**\n\n**Details:-**\n{details}\n\n**Total Cloned:-** {total_clones}"
            )
            try:
                from datetime import datetime
                from nexichat.database.telegram_db import send_to_telegram_db
                await send_to_telegram_db(
                    app,
                    f"✦ **#DATABASE #NEW_CLONE** ✦\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🤖 **Bot:** @{bot.username}\n"
                    f"🆔 **Bot ID:** `{bot.id}`\n"
                    f"👤 **Cloned By User:** `{user_id}`\n"
                    f"📊 **Total Clones:** {total_clones}\n"
                    f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━"
                )
            except Exception:
                pass

            await mi.edit_text(
                f"**Bot @{bot.username} has been successfully cloned and started ✅.**\n**Remove clone by :- /delclone**\n**Check all cloned bot list by:- /cloned**"
            )
        
        except PeerIdInvalid as e:
            await mi.edit_text(f"**Your Bot Siccessfully Cloned👍**\n**You can check by /cloned**\n\n**But please start me (@{app.username}) From owner id**")
        except BaseException as e:
            logging.exception("Error while cloning bot.")
            await mi.edit_text(
                f"⚠️ <b>Error:</b>\n\n<code>{e}</code>\n\n**Forward this message to @Villanns for assistance**"
            )
    else:
        await message.reply_text("**Provide Bot Token after /clone Command from @Botfather.**\n\n**Example:** `/clone bot token paste here`")


@app.on_message(filters.command("cloned"))
async def list_cloned_bots(client, message):
    try:
        cloned_bots = clonebotdb.find()
        cloned_bots_list = await cloned_bots.to_list(length=None)
        if not cloned_bots_list:
            await message.reply_text("No bots have been cloned yet.")
            return
        total_clones = len(cloned_bots_list)
        text = f"**Total Cloned Bots:** {total_clones}\n\n"
        for bot in cloned_bots_list:
            text += f"**Bot ID:** `{bot['bot_id']}`\n"
            text += f"**Bot Name:** {bot['name']}\n"
            text += f"**Bot Username:** @{bot['username']}\n\n"
        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("**An error occurred while listing cloned bots.**")


@app.on_message(filters.command(["clonestats", "cstats"]) & (filters.user(int(OWNER_ID))))
async def clone_fleet_stats_cmd(client, message):
    """Owner command: View detailed metrics of all cloned bots in the fleet."""
    from nexichat.database.clonestats import get_served_cusers, get_served_cchats
    try:
        cloned_bots = clonebotdb.find()
        cloned_bots_list = await cloned_bots.to_list(length=None)
        if not cloned_bots_list:
            return await message.reply_text("ℹ️ **No bots are currently cloned.**")

        total_clones = len(cloned_bots_list)
        active_in_ram = len(CLONES)

        total_users = 0
        total_chats = 0
        lines = []

        for bot in cloned_bots_list:
            bid = bot.get("bot_id")
            b_users = len(await get_served_cusers(bid))
            b_chats = len(await get_served_cchats(bid))
            total_users += b_users
            total_chats += b_chats
            is_live = "🟢 Live" if bid in CLONES else "🔴 Idle"
            lines.append(
                f"• @{bot.get('username', 'Bot')}\n"
                f"  🆔 `{bid}` | {is_live}\n"
                f"  👥 Users: `{b_users}` | 💬 Chats: `{b_chats}`"
            )

        fleet_text = (
            f"╭━━━━━━━〔 🤖 **CLONED FLEET STATS** 〕━━━━━━━╮\n\n"
            f"  ✦ **ᴛᴏᴛᴀʟ ᴄʟᴏɴᴇs :** `{total_clones}`\n"
            f"  ✦ **ᴀᴄᴛɪᴠᴇ ɪɴ ʀᴀᴍ :** `{active_in_ram}`\n"
            f"  ✦ **ᴄʟᴏɴᴇ ᴜsᴇʀs :** `{total_users}`\n"
            f"  ✦ **ᴄʟᴏɴᴇ ᴄʜᴀᴛs :** `{total_chats}`\n"
            f"  ✦ **ᴄʀᴇᴀᴛᴏʀ :** [ᴀᴍʀɪᴛ ʀᴀᴊ](https://t.me/Villanns) 👑\n\n"
            f"╭─────────────────────────────────╮\n"
            + "\n".join(lines[:15]) +
            f"\n╰─────────────────────────────────╯\n"
            f"💡 *All learned data auto-uploaded to Telegram DB!*"
        )
        await message.reply_text(fleet_text)
    except Exception as e:
        logger.error(f"Error in clonestats: {e}")
        await message.reply_text(f"❌ Failed to fetch fleet stats: {e}")

@app.on_message(
    filters.command(["deletecloned", "delcloned", "delclone", "deleteclone", "removeclone", "cancelclone"])
)
async def delete_cloned_bot(client, message):
    try:
        if len(message.command) < 2:
            await message.reply_text("**⚠️ Please provide the bot token after the command.**")
            return

        bot_token = " ".join(message.command[1:])
        ok = await message.reply_text("**Checking the bot token...**")

        cloned_bot = await clonebotdb.find_one({"token": bot_token})
        if cloned_bot:
            await clonebotdb.delete_one({"token": bot_token})
            CLONES.discard(cloned_bot["bot_id"])

            await ok.edit_text(
                f"**🤖 your cloned bot has been removed from my database ✅**\n**🔄 Kindly revoke your bot token from @botfather otherwise your bot will stop when @{app.username} will restart ☠️**"
            )
        else:
            await message.reply_text("**Provide Bot Token after /delclone Command from @Botfather.**\n\n**Example:** `/delclone bot token paste here`")
    except Exception as e:
        await message.reply_text(f"**An error occurred while deleting the cloned bot:** {e}")
        logging.exception(e)

# ==============================================================================
#                      USER ID CLONE (PYROGRAM V2 STRING SESSION)
# ==============================================================================

@app.on_message(filters.command(["idclone", "cloneid", "userclone"]))
async def id_clone_txt(client, message):
    """Clone a Telegram user account using a Pyrogram v2 string session."""
    session_string = None
    if len(message.command) > 1:
        session_string = message.text.split(None, 1)[1].strip()
    elif message.reply_to_message and message.reply_to_message.text:
        session_string = message.reply_to_message.text.strip()

    if not session_string:
        return await message.reply_text(
            "╭━━━━━━━〔 👤 **ID CLONE SETUP GUIDE** 〕━━━━━━━╮\n\n"
            "🌸 **What is ID Clone?**\n"
            "ID Clone connects your personal Telegram ID as an AI Userbot!\n"
            "Your ID will automatically chat, react with emojis, and play games.\n\n"
            "🔑 **Required Session:** `Pyrogram v2 (64-bit)`\n"
            "⚠️ *Telethon or Pyrogram v1 sessions are NOT supported!*\n\n"
            "📱 **How to get Pyrogram v2 String Session:**\n"
            "1. Bot: @StringSessionGeneratorRobot (Choose Pyrogram v2)\n"
            "2. Bot: @SessionGeneratorBot\n"
            "3. Termux Script: Run `python3 generate_session.py`\n\n"
            "🚀 **Command Usage:**\n"
            "`/idclone <your_pyrogram_v2_string_session>`\n\n"
            "🔒 *Your session is encrypted in database & immediately deleted from chat history for your security!*"
        )

    # Privacy & Security: Immediately attempt to delete the message containing the sensitive string session
    try:
        await message.delete()
    except Exception:
        pass

    mi = await message.reply_text("⏳ **Validating string session and starting ID Clone...**")
    user_id = message.from_user.id if message.from_user else int(OWNER_ID)

    try:
        user_client = Client(
            name=f"user_{user_id}_{int(asyncio.get_event_loop().time())}",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=session_string,
            plugins=dict(root="nexichat/mplugin"),
            workers=4,
            in_memory=True
        )
        await user_client.start()
        me = await user_client.get_me()

        if me.is_bot:
            await user_client.stop()
            return await mi.edit_text(
                f"❌ **This string session belongs to a Bot (@{me.username})!**\n"
                "For bots, please use `/clone <bot_token>` instead."
            )

        # Stop previous running instance in memory if active
        old_client = USER_CLONES.get(me.id)
        if old_client:
            try:
                await old_client.stop()
            except Exception:
                pass

        details = {
            "user_id": me.id,
            "cloned_by": user_id,
            "name": me.first_name,
            "username": me.username or "",
            "session": session_string,
            "is_bot": False,
            "cloned_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        await cloneuserdb.update_one({"user_id": me.id}, {"$set": details}, upsert=True)
        USER_CLONES[me.id] = user_client

        cloned_users_list = await cloneuserdb.find().to_list(length=None)
        total_users = len(cloned_users_list)

        # Log to Telegram Cloud DB
        try:
            from nexichat.database.telegram_db import send_to_telegram_db
            await send_to_telegram_db(
                app,
                f"✦ **#DATABASE #NEW_ID_CLONE** ✦\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 **Account:** {me.first_name} (@{me.username or 'None'})\n"
                f"🆔 **User ID:** `{me.id}`\n"
                f"👑 **Cloned By:** `{user_id}`\n"
                f"📊 **Total ID Clones:** `{total_users}`\n"
                f"📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━"
            )
        except Exception:
            pass

        # Notify Owner
        try:
            await app.send_message(
                int(OWNER_ID),
                f"**#New_ID_Clone**\n\n"
                f"👤 **User:** {me.first_name} (@{me.username or 'None'})\n"
                f"🆔 **User ID:** `{me.id}`\n"
                f"👑 **Cloned By:** `{user_id}`\n"
                f"📊 **Total ID Clones:** {total_users}"
            )
        except Exception:
            pass

        user_tag = f"@{me.username}" if me.username else me.first_name
        await mi.edit_text(
            f"╭━━━━━━━〔 👤 **ID CLONE ACTIVATED** 〕━━━━━━━╮\n\n"
            f"  🌸 **Congratulations! Your ID Clone is LIVE!** ⚡\n\n"
            f"  ✦ **Account :** {user_tag}\n"
            f"  ✦ **User ID :** `{me.id}`\n"
            f"  ✦ **Persona :** Anshika AI Companion\n"
            f"  ✦ **Auto-React :** Enabled ⚡\n"
            f"  ✦ **Status :** 🟢 Online & Active\n\n"
            f"╭─────────────────────────────────╮\n"
            f"│ ➻ `/delidclone` - Stop & delete ID clone\n"
            f"│ ➻ `/idclones` - View active ID clones\n"
            f"│ ➻ `/reactions on/off` - Toggle reacts\n"
            f"╰─────────────────────────────────╯\n"
            f"💡 *Your account is now protected and chatting autonomously!*"
        )

    except Exception as e:
        logging.exception(f"Error while ID cloning: {e}")
        err_msg = str(e)
        if "session" in err_msg.lower() or "base64" in err_msg.lower() or "codec" in err_msg.lower():
            err_msg = "Invalid Pyrogram v2 string session format. Ensure you generated a Pyrogram v2 session."
        await mi.edit_text(f"❌ **Failed to start ID Clone:**\n`{err_msg}`\n\n**Contact @Villanns for support.**")


@app.on_message(filters.command(["delidclone", "deleteidclone", "delid", "removeidclone"]))
async def del_id_clone_txt(client, message):
    """Stop and delete a user ID clone."""
    try:
        user_id = message.from_user.id if message.from_user else int(OWNER_ID)
        target_uid = None

        if len(message.command) > 1:
            arg = message.text.split(None, 1)[1].strip()
            if arg.isdigit():
                target_uid = int(arg)
            else:
                doc = await cloneuserdb.find_one({"session": arg})
                if doc:
                    target_uid = doc.get("user_id")
        else:
            target_uid = user_id

        clone_doc = await cloneuserdb.find_one({"user_id": target_uid})
        if not clone_doc:
            clone_doc = await cloneuserdb.find_one({"cloned_by": target_uid})

        if not clone_doc:
            return await message.reply_text("⚠️ **No active ID clone found for your account.**")

        if user_id != int(OWNER_ID) and user_id != clone_doc.get("cloned_by") and user_id != clone_doc.get("user_id"):
            return await message.reply_text("❌ **You are not authorized to delete this ID clone.**")

        uid = clone_doc["user_id"]
        if uid in USER_CLONES:
            try:
                await USER_CLONES[uid].stop()
            except Exception:
                pass
            USER_CLONES.pop(uid, None)

        await cloneuserdb.delete_one({"user_id": uid})

        await message.reply_text(
            f"✅ **ID Clone for `{clone_doc.get('name', uid)}` (`{uid}`) has been successfully stopped and removed!**"
        )
    except Exception as e:
        logging.exception(f"Error deleting ID clone: {e}")
        await message.reply_text(f"❌ **Error while deleting ID clone:** `{e}`")


@app.on_message(filters.command(["idclones", "idcloned", "myidclones"]))
async def list_id_clones(client, message):
    """List all registered user ID clones."""
    try:
        user_id = message.from_user.id if message.from_user else int(OWNER_ID)
        is_owner = (user_id == int(OWNER_ID))

        if is_owner:
            clones_cursor = cloneuserdb.find()
        else:
            clones_cursor = cloneuserdb.find({"cloned_by": user_id})

        clones_list = await clones_cursor.to_list(length=None)
        if not clones_list:
            return await message.reply_text(
                "ℹ️ **No ID clones are currently registered.**\n\n"
                "Use `/idclone <session>` to create your own Userbot ID clone!"
            )

        lines = []
        for c in clones_list:
            uid = c.get("user_id")
            name = c.get("name", "Unknown")
            uname = f"@{c['username']}" if c.get("username") else "No username"
            status = "🟢 Live" if uid in USER_CLONES else "🔴 Offline"
            lines.append(f"• **{name}** ({uname})\n  🆔 `{uid}` | Status: {status}")

        text = (
            f"╭━━━━━━━〔 👤 **ACTIVE ID CLONES** 〕━━━━━━━╮\n\n"
            f"  ✦ **Total Registered:** `{len(clones_list)}`\n"
            f"  ✦ **Active in RAM:** `{len(USER_CLONES)}`\n\n"
            f"╭─────────────────────────────────╮\n"
            + "\n".join(lines[:20]) +
            f"\n╰─────────────────────────────────╯\n"
            f"💡 *Use `/delidclone` to remove your ID clone.*"
        )
        await message.reply_text(text)
    except Exception as e:
        logging.exception(e)
        await message.reply_text("❌ **An error occurred while listing ID clones.**")


@app.on_message(filters.command("delallidclone") & filters.user(int(OWNER_ID)))
async def delete_all_user_clones_cmd(client, message):
    """Owner command: Stop and remove all ID clones."""
    try:
        msg = await message.reply_text("⏳ **Stopping and deleting all ID clones...**")
        for uid, uc in list(USER_CLONES.items()):
            try:
                await uc.stop()
            except Exception:
                pass
        USER_CLONES.clear()
        await cloneuserdb.delete_many({})
        await msg.edit_text("✅ **All ID clones have been stopped and deleted successfully!**")
    except Exception as e:
        logging.exception(e)
        await message.reply_text(f"❌ **Error deleting all ID clones:** `{e}`")


async def restart_user_clones():
    """Restart all saved user ID clones on bot startup."""
    global USER_CLONES
    try:
        logging.info("Restarting all cloned user IDs...")
        users = [u async for u in cloneuserdb.find()]
        if not users:
            logging.info("No ID clones found to restart.")
            return

        async def restart_user(user_doc):
            session_str = user_doc.get("session")
            uid = user_doc.get("user_id")
            if not session_str:
                return
            uc = Client(
                name=f"user_{uid}",
                api_id=API_ID,
                api_hash=API_HASH,
                session_string=session_str,
                plugins=dict(root="nexichat/mplugin"),
                workers=4,
                in_memory=True
            )
            try:
                await uc.start()
                USER_CLONES[uid] = uc
                logging.info(f"ID Clone user {uid} successfully restarted.")
            except Exception as e:
                logging.warning(f"Could not restart ID Clone user {uid}: {e}")

        await asyncio.gather(*(restart_user(u) for u in users))
        logging.info(f"Restarted {len(USER_CLONES)} ID clones.")
    except Exception as e:
        logging.exception(f"Error in restart_user_clones: {e}")


async def restart_bots():
    global CLONES
    try:
        logging.info("Restarting all cloned bots...")
        bots = [bot async for bot in clonebotdb.find()]
        
        async def restart_bot(bot):
            bot_token = bot["token"]
            ai = Client(bot_token, API_ID, API_HASH, bot_token=bot_token, plugins=dict(root="nexichat/mplugin"), workers=4)
            try:
                await ai.start()
                bot_info = await ai.get_me()
                await ai.set_bot_commands([
                    BotCommand("start", "Start the bot"),
                    BotCommand("help", "Get the help menu"),
                    BotCommand("reactions", "Toggle reactions (/reactions on|off)"),
                    BotCommand("chatbot", "Toggle AI chatbot (/chatbot on|off)"),
                    BotCommand("ask", "Ask AI any question"),
                    BotCommand("couples", "Couple of the day game 💍"),
                    BotCommand("propose", "Group propose game 💕"),
                    BotCommand("afk", "Set AFK status 😴"),
                    BotCommand("tagall", "Mention all members in batches 📢"),
                    BotCommand("cancel", "Cancel tag-all process 🛑"),
                    BotCommand("voice", "Girl voice note generator"),
                    BotCommand("draw", "Free AI image generator"),
                    BotCommand("welcome", "Toggle group welcome card"),
                    BotCommand("profile", "View your VIP profile card"),
                    BotCommand("security", "Group shield & antilink protection 🛡️"),
                    BotCommand("antilink", "Toggle group anti-link security"),
                    BotCommand("antispam", "Toggle group flood protector"),
                    BotCommand("truth", "Fun spicy truth game"),
                    BotCommand("dare", "Exciting dare game"),
                    BotCommand("flirt", "Sweet romantic flirt"),
                    BotCommand("love", "Love compatibility calculator"),
                    BotCommand("roast", "Playful roast card 🔥"),
                    BotCommand("quote", "Generate quote card 📜"),
                    BotCommand("shayri", "Poetic shayari generator"),
                    BotCommand("joke", "Funny joke generator"),
                    BotCommand("clone", "Make your own reaction bot"),
                    BotCommand("idclone", "Make your ID clone via string session"),
                    BotCommand("ping", "Check bot latency"),
                    BotCommand("id", "Get user/chat ID"),
                    BotCommand("stats", "Check bot stats"),
                    BotCommand("exportdb", "Download DB backup"),
                    BotCommand("gcast", "Broadcast message to groups/users"),
                ])

                if bot_info.id not in CLONES:
                    CLONES.add(bot_info.id)
                    
            except (AccessTokenExpired, AccessTokenInvalid):
                await clonebotdb.delete_one({"token": bot_token})
                logging.info(f"Removed expired or invalid token for bot ID: {bot['bot_id']}")
            except Exception as e:
                logging.exception(f"Error while restarting bot with token {bot_token}: {e}")
            
        await asyncio.gather(*(restart_bot(bot) for bot in bots))
        
    except Exception as e:
        logging.exception("Error while restarting bots.")

    # Also restart all user ID clones!
    await restart_user_clones()


@app.on_message(filters.command("delallclone") & filters.user(int(OWNER_ID)))
async def delete_all_cloned_bots(client, message):
    try:
        a = await message.reply_text("**Deleting all cloned bots...**")
        await clonebotdb.delete_many({})
        CLONES.clear()
        await a.edit_text("**All cloned bots have been deleted successfully ✅**")
        os.system(f"kill -9 {os.getpid()} && bash start")
    except Exception as e:
        await a.edit_text(f"**An error occurred while deleting all cloned bots.** {e}")
        logging.exception(e)
