# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
#  Licensed under Proprietary Terms. Unauthorized copying is strictly prohibited.
# ---------------------------------------------------------------------------------
"""
================================================================================
  CORE BANNER & SYSTEM DIAGNOSTIC REPORT
================================================================================
Is file ka kya kaam hai?
  Ye module bot startup ke waqt professional aesthetic banner aur deployment
  status matrix generate karta hai.
================================================================================
"""

import sys
import platform
import logging

logger = logging.getLogger(__name__)


def get_startup_banner(username: str, owner_id: int, db_mode: str, port: int, workers: int = 8) -> str:
    """Generate aesthetic ASCII startup banner with live runtime metrics."""
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    os_name = platform.system()

    banner = (
        "\n"
        "╔═══════════════════════════════════════════════════════════════════════════╗\n"
        "║                    VIP REACTION & AI CHATBOT (ANSHIKA AI)                 ║\n"
        "║              Copyright (c) 2026 Amrit Raj. All Rights Reserved.           ║\n"
        "╠═══════════════════════════════════════════════════════════════════════════╣\n"
        f"║  • Bot Username   : @{username:<48} ║\n"
        f"║  • Creator / Sudo : {str(owner_id):<48} ║\n"
        f"║  • Social Handles : Insta: @ex_amrit | Snap: @ex_amrit | TG: @Villanns      ║\n"
        f"║  • Database Engine: {db_mode:<48} ║\n"
        f"║  • Python Runtime : Python {py_ver} on {os_name:<34} ║\n"
        f"║  • Concurrency    : Pyrogram Workers: {workers} (Koyeb 512MB Optimized)     ║\n"
        f"║  • Cloud Watchdog : Active (Memory & Disk Auto-Clean Sentinel)            ║\n"
        f"║  • Web Health Srv : Active on Port {port:<38} ║\n"
        "║  • AI Brain Engine: Groq LPU + Gemini 3.5 + Modern Girl Multi-Tier        ║\n"
        "║  • Anti-Flood Shield : Leaky-Bucket 5 msgs / 10s Rate Limiter             ║\n"
        "╚═══════════════════════════════════════════════════════════════════════════╝\n"
    )
    return banner


def log_startup_banner(username: str, owner_id: int, db_mode: str, port: int, workers: int = 8):
    """Log the aesthetic startup banner to logger."""
    banner = get_startup_banner(username, owner_id, db_mode, port, workers)
    logger.info(banner)
