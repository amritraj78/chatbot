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
  Ye pooray bot ka Main Entry Point hai (python3 -m nexichat se execute hota hai).
  
Execution Flow:
  1. Pre-flight diagnostics: Credentials & environment variables validate karta hai.
     Agar koi error ho, toh exact reason aur step-by-step fix print karta hai.
  2. Flask Web Health Server & Koyeb 24/7 Keep-Alive daemon launch karta hai.
  3. Pyrogram Client login karke Telegram se connect hota hai.
  4. Sare command modules (reaction, chatbot, games, afk, tagall, etc.) dynamically import karta hai.
  5. Storage & RAM Sentinel Watchdog monitor start karta hai.
  6. Telegram Cloud Database sync initiate karta hai.
  7. Idle mode me continuous chalte rehta hai.
================================================================================
"""

import os
import asyncio
try:
    _loop = asyncio.get_event_loop()
    if _loop.is_closed():
        raise RuntimeError("loop closed")
except RuntimeError:
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

import importlib
from pyrogram import idle
from pyrogram.types import BotCommand

import config
from config import OWNER_ID
from nexichat import LOGGER, nexichat, load_clone_owners
from nexichat.modules import ALL_MODULES
from nexichat.modules.clone import restart_bots
from nexichat.core import (
    validate_environment,
    explain_telegram_login_error,
    find_available_port,
    start_flask_server,
    run_koyeb_keepalive,
    log_startup_banner,
)


async def anony_boot():
    LOGGER.info("═══════════════════════════════════════════════")
    LOGGER.info("🚀 Starting VIP Reaction & AI Chatbot Engine...")
    LOGGER.info("═══════════════════════════════════════════════")

    # 1. Pre-Flight Diagnostic Check
    is_valid, report = validate_environment(config)
    if not is_valid:
        LOGGER.error(report)
        return

    # 2. Determine Web Port & Launch Keep-Alive Health Server
    env_port = int(os.environ.get("PORT", 8000))
    port = find_available_port(env_port)
    start_flask_server(port)
    public_url = getattr(config, "KOYEB_PUBLIC_URL", None)
    asyncio.create_task(run_koyeb_keepalive(port, public_url))

    # 3. Start Pyrogram Client
    try:
        await nexichat.start()
        db_mode = "MongoDB Atlas" if config.MONGO_URL else "In-Memory RAM Engine + Telegram Cloud DB"
        log_startup_banner(nexichat.username, OWNER_ID, db_mode, port, workers=8)

        try:
            await nexichat.send_message(
                int(OWNER_ID),
                f"**{nexichat.mention} Is started✅**\n\n"
                f"✦ **Engine:** Anshika AI\n"
                f"✦ **Health Port:** `{port}`\n"
                f"✦ **RAM & Storage Sentinel:** Active 🛡️"
            )
        except Exception:
            LOGGER.info(f"@{nexichat.username} Started. (Tip: Send /start from owner account {OWNER_ID} to enable private alerts).")

        asyncio.create_task(restart_bots())
        await load_clone_owners()

    except Exception as ex:
        diag = explain_telegram_login_error(ex)
        LOGGER.error(diag)
        return

    # 4. Load All Command Modules Dynamically
    for all_module in ALL_MODULES:
        try:
            importlib.import_module("nexichat.modules." + all_module)
            LOGGER.info(f"📦 Successfully imported : {all_module}")
        except Exception as err:
            LOGGER.error(f"❌ Failed to load module '{all_module}': {err}", exc_info=True)

    # 5. Restore & Sync Database from Telegram Cloud & Initialize DB Indexes
    try:
        from nexichat.database.chatbot import ensure_database_indexes
        asyncio.create_task(ensure_database_indexes())
        from nexichat.database.telegram_db import sync_database_from_telegram, start_periodic_telegram_sync
        asyncio.create_task(sync_database_from_telegram(nexichat))
        asyncio.create_task(start_periodic_telegram_sync(nexichat, interval_seconds=600))
    except Exception as ex:
        LOGGER.warning(f"Telegram DB sync task startup notice: {ex}")

    # 6. Storage & RAM Sentinel Monitor (Alerts owner if storage >= 90% and auto-cleans cache)
    try:
        from nexichat.modules.sentinel import sentinel_monitor_loop
        asyncio.create_task(sentinel_monitor_loop(nexichat))
    except Exception as ex:
        LOGGER.warning(f"Storage sentinel monitor startup notice: {ex}")

    # 7. Register Global Bot Commands in Telegram UI
    try:
        await nexichat.set_bot_commands(
            commands=[
                BotCommand("start", "Start the bot & main menu"),
                BotCommand("help", "Help & all commands guide"),
                BotCommand("chatbot", "Toggle Anshika AI chat (on/off)"),
                BotCommand("reactions", "Toggle reactions (on/off)"),
                BotCommand("ask", "Ask Anshika AI any question"),
                BotCommand("couples", "Couple of the day game 💍"),
                BotCommand("propose", "Group propose game 💕"),
                BotCommand("afk", "Set AFK status 😴"),
                BotCommand("tagall", "Mention all members in batches 📢"),
                BotCommand("cancel", "Cancel tag-all process 🛑"),
                BotCommand("dice", "Dice match game vs Anshika 🎲"),
                BotCommand("toss", "Flip coin (Heads/Tails) 🪙"),
                BotCommand("truth", "Fun spicy truth game"),
                BotCommand("dare", "Exciting dare game"),
                BotCommand("flirt", "Sweet romantic flirt"),
                BotCommand("love", "Love compatibility test"),
                BotCommand("roast", "Playful roast card 🔥"),
                BotCommand("quote", "Generate quote card 📜"),
                BotCommand("shayri", "Sweet Hindi shayari"),
                BotCommand("joke", "Funny joke generator"),
                BotCommand("voice", "Girl voice note generator"),
                BotCommand("draw", "Free AI image generator"),
                BotCommand("welcome", "Group welcome card toggle"),
                BotCommand("profile", "View your VIP profile card"),
                BotCommand("security", "Group shield & antilink protection 🛡️"),
                BotCommand("antilink", "Toggle group anti-link security"),
                BotCommand("antispam", "Toggle group flood protector"),
                BotCommand("storage", "Koyeb RAM & Disk sentinel (Owner)"),
                BotCommand("clone", "Make your own reaction bot"),
                BotCommand("cloned", "List all cloned bots"),
                BotCommand("ping", "Check bot latency"),
                BotCommand("id", "Get user/chat ID"),
                BotCommand("stats", "Check bot stats"),
                BotCommand("exportdb", "Download DB backup (Owner)"),
                BotCommand("gcast", "Broadcast message to groups/users"),
            ]
        )
        LOGGER.info("Bot commands set successfully.")
    except Exception as ex:
        LOGGER.error(f"Failed to set bot commands: {ex}")

    LOGGER.info(f"@{nexichat.username} Started.")
    try:
        await idle()
    except (asyncio.CancelledError, KeyboardInterrupt):
        LOGGER.info("Shutdown signal received.")
    finally:
        LOGGER.info("🛑 Gracefully stopping nexichat & releasing Pyrogram SQLite sessions...")
        try:
            if getattr(nexichat, "is_connected", False):
                await nexichat.stop()
        except Exception as e:
            LOGGER.debug(f"Stop exception notice: {e}")
        LOGGER.info("✅ All sessions safely flushed. Ready for clean Koyeb rebuild.")


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(anony_boot())
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        LOGGER.info("VIP Reaction Bot stopped safely.")
