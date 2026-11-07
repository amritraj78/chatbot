# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
#  Licensed under Proprietary Terms. Unauthorized copying is strictly prohibited.
# ---------------------------------------------------------------------------------
"""
================================================================================
  KOYEB 24/7 KEEP-ALIVE DAEMON & WEB HEALTH SERVER
================================================================================
Is file ka kya kaam hai?
  Koyeb Free Tier containers agar 15-30 minute tak koi HTTP traffic na mile toh
  sleep/idle mode me chale jaate hain.
  
Ye daemon kaise solve karta hai?
  1. Lightweight Flask server PORT 8000 (ya assigned PORT) par run karta hai.
  2. Background me har 4 minute par local /health aur remote KOYEB_PUBLIC_URL ko
     ping karta rehta hai.
  3. Isse Koyeb ko hamesha inbound traffic milta rehta hai aur bot lifetime tak
     bina sleep huye active rehta hai!
================================================================================
"""

import os
import random
import asyncio
import logging
import threading
import urllib.request
from flask import Flask, jsonify

logger = logging.getLogger(__name__)

app = Flask("VIP_Reaction_HealthServer")

# Suppress flask development server banner spam
logging.getLogger("werkzeug").setLevel(logging.WARNING)


@app.route("/")
def home():
    return jsonify({
        "service": "VIP Reaction & AI Chatbot",
        "status": "online",
        "author": "Amrit Raj (@Villanns)",
        "telegram": "https://t.me/amrit_feel",
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": os.environ.get("HOSTNAME", "localhost")
    })


def start_flask_server(port: int = 8000):
    """Start the Flask web health server in a background daemon thread."""
    def _run():
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

    flask_thread = threading.Thread(target=_run, name="FlaskHealthServer", daemon=True)
    flask_thread.start()
    logger.info(f"Flask Web Health Server active on port {port}.")


async def run_koyeb_keepalive(port: int, public_url: str = None):
    """
    Background keep-alive loop that continuously pings health endpoints
    to prevent Koyeb free tier suspension.
    """
    local_url = f"http://127.0.0.1:{port}/health"

    # Auto-detect public URL from common platform environment variables if not provided
    if not public_url:
        public_url = (
            os.environ.get("KOYEB_PUBLIC_URL")
            or os.environ.get("PING_URL")
            or (f"https://{os.environ.get('KOYEB_APP_NAME')}.koyeb.app" if os.environ.get("KOYEB_APP_NAME") else None)
        )

    while True:
        try:
            # 90-120s interval to prevent Koyeb free tier edge proxy idle timeout
            sleep_duration = 90 + random.randint(5, 30)
            await asyncio.sleep(sleep_duration)

            # 1. Local loopback ping
            req_local = urllib.request.Request(local_url, headers={"User-Agent": "KoyebKeepAlive/2.0"})
            with urllib.request.urlopen(req_local, timeout=8) as resp:
                pass

            # 2. Public URL ping (traverses Koyeb edge router to guarantee 24/7 active status)
            if public_url and public_url.strip():
                clean_url = public_url.strip().rstrip("/")
                target = clean_url if clean_url.endswith("/health") else f"{clean_url}/health"
                req_pub = urllib.request.Request(target, headers={"User-Agent": "KoyebKeepAlive/2.0"})
                with urllib.request.urlopen(req_pub, timeout=12) as pub_resp:
                    pass
                logger.info(f"Koyeb 24/7 Keep-Alive Ping successful to {target}.")
            else:
                logger.info("Local keepalive ping successful. 💡 Tip: Set KOYEB_PUBLIC_URL in Koyeb settings to keep it awake 24/7.")
        except Exception as e:
            logger.debug(f"Keep-Alive notice: {e}")
