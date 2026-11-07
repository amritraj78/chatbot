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
import json
import urllib.request
from flask import Flask, jsonify, request, Response
from nexichat.core.webapp_html import WEBAPP_HTML

logger = logging.getLogger(__name__)

app = Flask("VIP_Reaction_HealthServer")

# Suppress flask development server banner spam
logging.getLogger("werkzeug").setLevel(logging.WARNING)


@app.route("/")
@app.route("/webapp")
def webapp():
    """Serve modern interactive Telegram Mini App."""
    return Response(WEBAPP_HTML, mimetype="text/html; charset=utf-8")


@app.route("/api/info")
def info():
    return jsonify({
        "service": "VIP Reaction & AI Chatbot",
        "status": "online",
        "author": "Amrit Raj (@Villanns)",
        "telegram": "https://t.me/amrit_feel",
    })


@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    """Live AI Chat endpoint for the Telegram WebApp."""
    if request.method == "OPTIONS":
        resp = jsonify({"status": "ok"})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return resp

    data = request.get_json(silent=True) or {}
    msg = data.get("message", "").strip()
    user_name = data.get("user_name") or "Friend"
    user_id = data.get("user_id")

    if not msg:
        resp = jsonify({"error": "Empty message"})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp, 400

    try:
        from nexichat.modules.helpers.ai import generate_conversational_response
        import concurrent.futures

        def _get_reply():
            new_loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(new_loop)
                return new_loop.run_until_complete(
                    generate_conversational_response(msg, user_name=user_name, user_id=user_id)
                )
            finally:
                new_loop.close()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_get_reply)
            reply = future.result(timeout=12)

        resp = jsonify({"reply": reply})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp
    except Exception as e:
        logger.error(f"Mini App /api/chat error: {e}")
        resp = jsonify({"reply": "Hii! Main thoda padhai mein busy thi, aap batao kaise ho? 😊🌸"})
        resp.headers["Access-Control-Allow-Origin"] = "*"
        return resp


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": os.environ.get("HOSTNAME", "localhost")
    })


def configure_telegram_menu_button(bot_token: str, public_url: str, text: str = "🌸 Anshika AI"):
    """Configures the Telegram Chat Menu Button to open the Web App."""
    if not bot_token or not public_url:
        return
    try:
        clean_url = public_url.rstrip("/") + "/webapp"
        api_url = f"https://api.telegram.org/bot{bot_token}/setChatMenuButton"
        payload = {
            "menu_button": {
                "type": "web_app",
                "text": text,
                "web_app": {
                    "url": clean_url
                }
            }
        }
        req = urllib.request.Request(
            api_url,
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            data=json.dumps(payload).encode()
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            logger.info(f"Telegram Menu Button configured ({text} -> {clean_url}): {r.read().decode()}")
    except Exception as e:
        logger.debug(f"Failed to set Telegram menu button: {e}")


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

    # Automatically set Telegram Menu Button to open Anshika Mini App
    bot_token = os.environ.get("BOT_TOKEN")
    if bot_token and public_url:
        configure_telegram_menu_button(bot_token, public_url, text="🌸 Anshika AI")

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
