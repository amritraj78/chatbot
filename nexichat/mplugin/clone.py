import logging
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.errors import PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from pyrogram.types import BotCommand
from nexichat.mplugin.helpers import is_owner
from config import API_HASH, API_ID, OWNER_ID
from nexichat import nexichat as app, save_clonebot_owner
from nexichat import db as mongodb

CLONES = set()
cloneownerdb = mongodb.cloneownerdb
clonebotdb = mongodb.clonebotdb
cloneuserdb = mongodb.cloneuserdb


@Client.on_message(filters.command(["clone", "host", "deploy"]))
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
                BotCommand("reactions", "Check or toggle reactions (/reactions on|off)"),
                BotCommand("chatbot", "Toggle AI chatbot (/chatbot on|off)"),
                BotCommand("ask", "Ask AI any question"),
                BotCommand("couples", "Couple of the day game 💍"),
                BotCommand("propose", "Group propose game 💕"),
                BotCommand("afk", "Set AFK status 😴"),
                BotCommand("tagall", "Mention all members in batches 📢"),
                BotCommand("cancel", "Cancel tag-all process 🛑"),
                BotCommand("love", "Love compatibility calculator"),
                BotCommand("shayri", "Poetic shayari generator"),
                BotCommand("clone", "Make your own reaction bot"),
                BotCommand("ping", "Check bot latency"),
                BotCommand("id", "Get user/chat ID"),
                BotCommand("stats", "Check bot stats"),
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

            await mi.edit_text(
                f"**Bot @{bot.username} has been successfully cloned and started ✅.**\n**Remove clone by :- /delclone**\n**Check all cloned bot list by:- /cloned**"
            )
        except PeerIdInvalid as e:
            await mi.edit_text(f"**Your bot successfully cloned👍**\n**You can check by /cloned**\n\n**But please start me (@{nexichat.username}) From owner id**")
        
        except BaseException as e:
            logging.exception("Error while cloning bot.")
            await mi.edit_text(
                f"⚠️ <b>Error:</b>\n\n<code>{e}</code>\n\n**Forward this message to @Villanns for assistance**"
            )
    else:
        await message.reply_text("**Provide Bot Token after /clone Command from @Botfather.**\n\n**Example:** `/clone bot token paste here`")


@Client.on_message(filters.command("cloned"))
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

@Client.on_message(
    filters.command(["deletecloned", "delcloned", "delclone", "deleteclone", "removeclone", "cancelclone"])
)
async def delete_cloned_bot(client, message):
    try:
        if len(message.command) < 2:
            await message.reply_text("**Provide Bot Token after /delclone Command from @Botfather.**\n\n**Example:** `/delclone bot token paste here`")
            return

        bot_token = " ".join(message.command[1:])
        ok = await message.reply_text("**Checking the bot token...**")

        cloned_bot = await clonebotdb.find_one({"token": bot_token})
        if cloned_bot:
            await clonebotdb.delete_one({"token": bot_token})
            
            await ok.edit_text(
                f"**🤖 your cloned bot has been removed from my database ✅**\n**🔄 Kindly revoke your bot token from @botfather otherwise your bot will stop when @{app.username} will restart ☠️**"
            )
        else:
            await message.reply_text("**⚠️ The provided bot token is not in the cloned list.**")
    except Exception as e:
        await message.reply_text(f"**An error occurred while deleting the cloned bot:** {e}")
        logging.exception(e)


@Client.on_message(filters.command("delallclone") & filters.user(int(OWNER_ID)))
async def delete_all_cloned_bots(client, message):
    try:
        a = await message.reply_text("**Deleting all cloned bots...**")
        await clonebotdb.delete_many({})
        CLONES.clear()
        await a.edit_text("**All cloned bots have been deleted successfully ✅**")
    except Exception as e:
        await a.edit_text(f"**An error occurred while deleting all cloned bots.** {e}")
        logging.exception(e)


# ==============================================================================
#                      USER ID CLONE (PYROGRAM V2 STRING SESSION)
# ==============================================================================

@Client.on_message(filters.command(["idclone", "cloneid", "userclone"]))
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
        from nexichat.modules.clone import USER_CLONES
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
                client,
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


@Client.on_message(filters.command(["delidclone", "deleteidclone", "delid", "removeidclone"]))
async def del_id_clone_txt(client, message):
    """Stop and delete a user ID clone."""
    try:
        from nexichat.modules.clone import USER_CLONES
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


@Client.on_message(filters.command(["idclones", "idcloned", "myidclones"]))
async def list_id_clones(client, message):
    """List all registered user ID clones."""
    try:
        from nexichat.modules.clone import USER_CLONES
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


@Client.on_message(filters.command("delallidclone") & filters.user(int(OWNER_ID)))
async def delete_all_user_clones_cmd(client, message):
    """Owner command: Stop and remove all ID clones."""
    try:
        from nexichat.modules.clone import USER_CLONES
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

