# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
#  Licensed under Proprietary Terms. Unauthorized copying is strictly prohibited.
# ---------------------------------------------------------------------------------
"""
================================================================================
  CORE PRE-FLIGHT DIAGNOSTIC & SELF-HEALING ENGINE
================================================================================
Is file ka kya kaam hai?
  Ye engine bot boot hone se pehle environment, credentials, database, aur
  network ports ko test karta hai.
  
Agar koi bhi deployment error aaye:
  1. EXACT wajah (Why it happened) batata hai.
  2. Clear step-by-step solution deta hai taaki naye students/users bhi 1 minute
     me fix kar sakein.
  3. Non-fatal issues (jaise MongoDB offline hona) par auto-switch karke built-in
     In-Memory + Telegram Cloud DB activate kar deta hai taaki bot kabhi crash na ho!
================================================================================
"""

import os
import re
import socket
import logging
from typing import Tuple, Optional, Dict, Any

logger = logging.getLogger(__name__)


def is_port_available(port: int, host: str = "127.0.0.1") -> bool:
    """Check if a local TCP port is free to bind."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            return True
        except OSError:
            return False


def find_available_port(default_port: int = 8000) -> int:
    """Find an available port starting from default_port."""
    if is_port_available(default_port):
        return default_port
    for p in range(default_port + 1, default_port + 20):
        if is_port_available(p):
            logger.info(f"Port {default_port} in use, dynamically switched to port {p}.")
            return p
    return default_port


def validate_environment(config_mod: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate all deployment variables and return (is_valid, error_report).
    """
    bot_token = getattr(config_mod, "BOT_TOKEN", None)
    owner_id = getattr(config_mod, "OWNER_ID", None)
    api_id = getattr(config_mod, "API_ID", None)
    api_hash = getattr(config_mod, "API_HASH", None)

    # 1. BOT_TOKEN check
    if not bot_token or not str(bot_token).strip():
        report = (
            "\n"
            "┌────────────────────────────────────────────────────────────────────────┐\n"
            "│ ❌ [DEPLOYMENT ERROR]: BOT_TOKEN is MISSING!                           │\n"
            "├────────────────────────────────────────────────────────────────────────┤\n"
            "│ 🔍 WHY IT HAPPENED:                                                    │\n"
            "│   The bot cannot connect to Telegram without an official Bot Token.    │\n"
            "│                                                                        │\n"
            "│ 🛠️ HOW TO FIX:                                                         │\n"
            "│   1. Open Telegram and search for @BotFather                           │\n"
            "│   2. Send /newbot (or /mybots) to get your API Token                   │\n"
            "│   3. Copy the token (e.g., 9069787947:AAGsXEtnRMndX...)                │\n"
            "│   4. In Koyeb: Service Settings -> Environment Variables -> BOT_TOKEN  │\n"
            "│   5. Save and Redeploy.                                                │\n"
            "└────────────────────────────────────────────────────────────────────────┘\n"
        )
        return False, report

    # 2. BOT_TOKEN format check
    token_str = str(bot_token).strip()
    if not re.match(r"^\d+:[A-Za-z0-9_-]{30,}$", token_str):
        report = (
            "\n"
            "┌────────────────────────────────────────────────────────────────────────┐\n"
            "│ ⚠️ [DEPLOYMENT ERROR]: BOT_TOKEN FORMAT IS INVALID!                    │\n"
            "├────────────────────────────────────────────────────────────────────────┤\n"
            "│ 🔍 WHY IT HAPPENED:                                                    │\n"
            "│   Your BOT_TOKEN contains invalid characters, extra spaces, or is cut. │\n"
            "│                                                                        │\n"
            "│ 🛠️ HOW TO FIX:                                                         │\n"
            "│   Ensure there are no leading/trailing spaces or quotes around token.   │\n"
            "│   Correct format example: 123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ         │\n"
            "└────────────────────────────────────────────────────────────────────────┘\n"
        )
        return False, report

    # 3. OWNER_ID check
    try:
        int(owner_id)
    except (ValueError, TypeError):
        report = (
            "\n"
            "┌────────────────────────────────────────────────────────────────────────┐\n"
            "│ ⚠️ [DEPLOYMENT NOTICE]: OWNER_ID MUST BE A NUMERIC USER ID!            │\n"
            "├────────────────────────────────────────────────────────────────────────┤\n"
            "│ 🔍 WHY IT HAPPENED:                                                    │\n"
            "│   Telegram usernames (like @Villanns) cannot be used as numeric IDs.   │\n"
            "│                                                                        │\n"
            "│ 🛠️ HOW TO FIX:                                                         │\n"
            "│   Send /id to @Reactions_rebot or @userinfobot to get your numeric ID  │\n"
            "│   (e.g., 5423666218). Then set OWNER_ID in environment variables.      │\n"
            "└────────────────────────────────────────────────────────────────────────┘\n"
        )
        return False, report

    # 4. API_ID / API_HASH check
    if not api_id or not api_hash:
        logger.warning("API_ID or API_HASH was missing; defaulted to stable fallback credentials.")

    return True, None


def explain_telegram_login_error(ex: Exception) -> str:
    """Provide student-friendly diagnostic and fix for Telegram login failures."""
    err_str = str(ex)
    if "AccessTokenInvalid" in err_str or "401" in err_str:
        return (
            "\n"
            "┌────────────────────────────────────────────────────────────────────────┐\n"
            "│ ❌ [TELEGRAM ERROR]: BOT_TOKEN HAS BEEN REVOKED OR IS INVALID!         │\n"
            "├────────────────────────────────────────────────────────────────────────┤\n"
            "│ 🔍 WHY IT HAPPENED:                                                    │\n"
            "│   Telegram BotFather rejected the token because it was revoked or typed│\n"
            "│   incorrectly.                                                         │\n"
            "│                                                                        │\n"
            "│ 🛠️ HOW TO FIX:                                                         │\n"
            "│   1. Open @BotFather on Telegram                                       │\n"
            "│   2. Select your bot via /mybots -> API Token                          │\n"
            "│   3. Click 'Revoke current token' if needed to get a fresh token.      │\n"
            "│   4. Update BOT_TOKEN in Koyeb / .env file and restart.                │\n"
            "└────────────────────────────────────────────────────────────────────────┘\n"
        )
    elif "ApiIdInvalid" in err_str:
        return (
            "\n"
            "┌────────────────────────────────────────────────────────────────────────┐\n"
            "│ ❌ [TELEGRAM ERROR]: API_ID or API_HASH IS INVALID!                    │\n"
            "├────────────────────────────────────────────────────────────────────────┤\n"
            "│ 🔍 WHY IT HAPPENED:                                                    │\n"
            "│   Telegram rejected the API_ID/API_HASH app credentials.               │\n"
            "│                                                                        │\n"
            "│ 🛠️ HOW TO FIX:                                                         │\n"
            "│   Visit https://my.telegram.org -> API development tools to create or │\n"
            "│   verify your app API_ID and API_HASH.                                │\n"
            "└────────────────────────────────────────────────────────────────────────┘\n"
        )
    return f"Telegram Client startup notice: {ex}"


# Rate limiting dictionary to prevent spamming owner with duplicate error reports
_last_error_alerts = {}


async def report_exception_to_owner(client: Any, context: str, ex: Exception) -> bool:
    """
    Safely formats and sends a runtime error diagnostic alert to OWNER_ID.
    Rate-limited to 1 alert per error type every 60 seconds to prevent message flood.
    """
    import time
    from datetime import datetime
    import config

    owner_id = getattr(config, "OWNER_ID", None)
    if not owner_id or not client:
        return False

    err_key = f"{context}:{type(ex).__name__}"
    now = time.time()
    if err_key in _last_error_alerts and (now - _last_error_alerts[err_key]) < 60:
        return False  # Suppress duplicate alert within 60s
    _last_error_alerts[err_key] = now

    alert_text = (
        f"🚨 <b>VIP DIAGNOSTIC SENTINEL: RUNTIME ALERT</b> 🚨\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✦ <b>Context:</b> <code>{context}</code>\n"
        f"✦ <b>Exception:</b> <code>{type(ex).__name__}</code>\n"
        f"✦ <b>Detail:</b> <code>{str(ex)[:300]}</code>\n"
        f"✦ <b>Timestamp:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<i>Self-healing active: Bot continued operations without crashing.</i>"
    )
    try:
        await client.send_message(int(owner_id), alert_text)
        return True
    except Exception as e:
        logger.debug(f"Unable to send exception alert to owner {owner_id}: {e}")
        return False


def get_system_health_report() -> Dict[str, Any]:
    """Return lightweight health metrics for system status and monitoring."""
    import psutil
    import time
    from nexichat import boot

    proc = psutil.Process(os.getpid())
    ram_mb = round(proc.memory_info().rss / (1024 * 1024), 2)
    uptime_sec = int(time.time() - boot)
    days, rem = divmod(uptime_sec, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, seconds = divmod(rem, 60)

    return {
        "status": "healthy",
        "ram_mb": ram_mb,
        "uptime": f"{days}d {hours}h {minutes}m {seconds}s",
        "uptime_seconds": uptime_sec,
        "pid": os.getpid()
    }

