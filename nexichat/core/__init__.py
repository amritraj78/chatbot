# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
#  Licensed under Proprietary Terms. Unauthorized copying is strictly prohibited.
# ---------------------------------------------------------------------------------
"""
Core architectural package for VIP Reaction & AI Chatbot.
Provides diagnostics, keep-alive daemons, and system banners.
"""

from nexichat.core.diagnostics import (
    validate_environment,
    explain_telegram_login_error,
    find_available_port,
    report_exception_to_owner,
    get_system_health_report,
)
from nexichat.core.keepalive import (
    start_flask_server,
    run_koyeb_keepalive
)
from nexichat.core.banner import (
    log_startup_banner,
    get_startup_banner
)

__all__ = [
    "validate_environment",
    "explain_telegram_login_error",
    "find_available_port",
    "report_exception_to_owner",
    "get_system_health_report",
    "start_flask_server",
    "run_koyeb_keepalive",
    "log_startup_banner",
    "get_startup_banner",
]
