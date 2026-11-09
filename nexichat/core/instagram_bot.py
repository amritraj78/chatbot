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
  Ye module Instagram AI Userbot ko manage karta hai!
  
Kaise kaam karta hai?
  1. Login & Session Caching:
     - User ke credentials se login karta hai aur session settings ko 
       `cache/ig_session.json` me safely cache kar leta hai.
     - Agli baar restart hone par cached session reuse hota hai, jisse bar bar
       Instagram login / 2FA checkpoint trigger na ho.
  2. Safety Delays & Anti-Ban Rate Limiter:
     - Har 15-20 seconds ke interval par unread DMs poll karta hai.
     - Reply bhejne se pehle 2-4 seconds ka natural human delay rakhta hai.
     - Instagram checkpoint / challenge ya rate-limit hone par clear logs deta hai.
  3. AI Brain Integration:
     - Naye incoming text message ko seedha Anshika AI (`generate_conversational_response`)
       se connect karta hai aur sweet & friendly reply bhejta hai.
================================================================================
"""

import os
import json
import time
import uuid
import random
import asyncio
import logging
from typing import Optional, Dict, Any, Set

try:
    from nexichat.modules.helpers.ai import generate_conversational_response
except ImportError:
    generate_conversational_response = None

import config

LOGGER = logging.getLogger("nexichat.instagram")




try:
    from instagram_private_api import (
        Client,
        ClientCompatPatch,
        ClientError,
        ClientLoginError,
        ClientLoginRequiredError,
        ClientCookieExpiredError,
        ClientCheckpointRequiredError,
        ClientChallengeRequiredError,
        ClientThrottledError,
        ClientSentryBlockError,
    )
    INSTAGRAM_LIBRARY_AVAILABLE = True
except ImportError:
    INSTAGRAM_LIBRARY_AVAILABLE = False
    Client = object
    ClientError = Exception
    ClientLoginError = Exception
    ClientLoginRequiredError = Exception
    ClientCookieExpiredError = Exception
    ClientCheckpointRequiredError = Exception
    ClientChallengeRequiredError = Exception
    ClientThrottledError = Exception
    ClientSentryBlockError = Exception


SESSION_FILE_PATH = os.path.join("cache", "ig_session.json")


class InstagramChatbotClient(Client):
    """
    Subclassed Instagram Private API Client providing direct messaging,
    thread fetching, and session serialization helpers.
    """

    def send_direct_text(
        self,
        text: str,
        thread_id: Optional[str] = None,
        recipient_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sends a direct text message to a specific thread or user ID
        via Instagram's internal mobile broadcast endpoint.
        """
        client_context = str(uuid.uuid4())
        params = {
            "client_context": client_context,
            "action": "send_item",
            "text": str(text),
            "_uuid": getattr(self, "uuid", str(uuid.uuid4())),
        }
        if thread_id:
            params["thread_ids"] = f"[{thread_id}]"
        elif recipient_user_id:
            params["recipient_users"] = f"[[{recipient_user_id}]]"
        else:
            raise ValueError("Either thread_id or recipient_user_id must be provided")

        return self._call_api("direct_v2/threads/broadcast/text/", params=params)

    def get_inbox_threads(self, cursor: Optional[str] = None) -> Dict[str, Any]:
        """
        Fetches direct message inbox threads from Instagram.
        """
        query = {"cursor": cursor} if cursor else None
        return self._call_api("direct_v2/inbox/", query=query)

    def get_thread_detail(
        self, thread_id: str, cursor: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetches detailed messages from a specific conversation thread.
        """
        query = {"cursor": cursor} if cursor else None
        return self._call_api(f"direct_v2/threads/{thread_id}/", query=query)


class InstagramUserbot:
    """
    Controller that coordinates Instagram authentication, session caching,
    and background DM polling with AI auto-reply.
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        poll_interval: int = 15,
        session_file: str = SESSION_FILE_PATH,
    ):
        self.username = username or getattr(config, "INSTAGRAM_USERNAME", None)
        self.password = password or getattr(config, "INSTAGRAM_PASSWORD", None)
        self.poll_interval = poll_interval or getattr(config, "INSTAGRAM_POLL_INTERVAL", 15)
        self.session_file = session_file
        self.client: Optional[InstagramChatbotClient] = None
        self.is_running = False
        self.seen_message_ids: Set[str] = set()
        self._worker_task: Optional[asyncio.Task] = None

    def _ensure_cache_dir(self) -> None:
        directory = os.path.dirname(self.session_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def save_session_callback(self, client: InstagramChatbotClient) -> None:
        """
        Callback invoked when a fresh login succeeds. Saves session settings.
        """
        try:
            self._ensure_cache_dir()
            settings = client.settings
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2)
            LOGGER.info(f"💾 [Instagram] Session successfully cached to '{self.session_file}'.")
        except Exception as ex:
            LOGGER.warning(f"⚠️ [Instagram] Could not save session settings: {ex}")

    def load_cached_settings(self) -> Optional[Dict[str, Any]]:
        """
        Loads cached session settings from disk if available.
        """
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "cookie" in data:
                        return data
            except Exception as ex:
                LOGGER.warning(f"⚠️ [Instagram] Failed to read session cache: {ex}")
        return None

    def login(self) -> bool:
        """
        Authenticates with Instagram. Uses cached session first,
        falling back to fresh credentials if expired.
        """
        if not INSTAGRAM_LIBRARY_AVAILABLE:
            LOGGER.error("❌ [Instagram] instagram_private_api library is not installed.")
            return False

        if not self.username or not self.password:
            LOGGER.warning("⚠️ [Instagram] Username or password not configured in .env.")
            return False

        cached_settings = self.load_cached_settings()
        if cached_settings:
            try:
                LOGGER.info("🔑 [Instagram] Attempting login with cached session settings...")
                self.client = InstagramChatbotClient(
                    self.username,
                    self.password,
                    settings=cached_settings,
                )
                LOGGER.info(f"✅ [Instagram] Reconnected successfully using cached session for @{self.username}!")
                return True
            except (ClientCookieExpiredError, ClientLoginRequiredError) as ex:
                LOGGER.info(f"ℹ️ [Instagram] Cached session expired ({ex}). Proceeding with fresh login...")
            except Exception as ex:
                LOGGER.warning(f"⚠️ [Instagram] Cached session login failed: {ex}. Retrying with fresh login...")

        try:
            LOGGER.info(f"🔐 [Instagram] Logging in to Instagram as @{self.username}...")
            self.client = InstagramChatbotClient(
                self.username,
                self.password,
                on_login=self.save_session_callback,
            )
            # In case on_login was not called by constructor, save explicitly:
            self.save_session_callback(self.client)
            LOGGER.info(f"✅ [Instagram] Logged in successfully as @{self.username}!")
            return True

        except (ClientCheckpointRequiredError, ClientChallengeRequiredError) as cp_err:
            LOGGER.error(
                "🚨 [Instagram CHECKPOINT REQUIRED]\n"
                f"Instagram flagged this login from your IP: {cp_err}\n"
                "👉 ACTION REQUIRED: Please open your Instagram mobile app or email/SMS "
                "and approve 'This was me' or provide the verification code."
            )
            return False
        except ClientLoginError as login_err:
            LOGGER.error(f"❌ [Instagram Login Failed] Incorrect username or password: {login_err}")
            return False
        except (ClientThrottledError, ClientSentryBlockError) as block_err:
            LOGGER.error(f"⚠️ [Instagram Blocked] Rate limit or temporary block by Instagram: {block_err}")
            return False
        except Exception as general_err:
            LOGGER.error(f"❌ [Instagram Login Error] Unexpected error during authentication: {general_err}")
            return False

    async def _seed_existing_messages(self) -> None:
        """
        Pre-seeds seen message IDs from the existing inbox on startup
        so historical messages are not repeatedly replied to.
        """
        if not self.client:
            return
        try:
            inbox_data = await asyncio.to_thread(self.client.get_inbox_threads)
            threads = inbox_data.get("inbox", {}).get("threads", [])
            for thread in threads:
                for item in thread.get("items", []):
                    item_id = str(item.get("item_id", ""))
                    if item_id:
                        self.seen_message_ids.add(item_id)
            LOGGER.info(
                f"📥 [Instagram] Seeded {len(self.seen_message_ids)} existing inbox messages. "
                "Only new incoming messages will receive AI replies."
            )
        except Exception as ex:
            LOGGER.warning(f"⚠️ [Instagram] Inbox pre-seeding notice: {ex}")

    async def worker_loop(self) -> None:
        """
        Background loop polling for unread Direct Messages and sending AI replies.
        """
        LOGGER.info(f"🚀 [Instagram] Auto-reply userbot started for @{self.username} (Poll: {self.poll_interval}s).")

        await self._seed_existing_messages()

        while self.is_running:
            try:
                # Add human jitter to the poll interval in production mode
                if self.poll_interval < 5:
                    sleep_time = max(0.01, float(self.poll_interval))
                else:
                    jitter = random.uniform(-2.0, 2.0)
                    sleep_time = max(5.0, self.poll_interval + jitter)
                await asyncio.sleep(sleep_time)


                if not self.is_running or not self.client:
                    break

                inbox = await asyncio.to_thread(self.client.get_inbox_threads)
                threads = inbox.get("inbox", {}).get("threads", [])

                my_id = str(getattr(self.client, "authenticated_user_id", ""))

                for thread in threads:
                    thread_id = str(thread.get("thread_id", ""))
                    items = thread.get("items", [])
                    if not items:
                        continue

                    latest_item = items[0]
                    item_id = str(latest_item.get("item_id", ""))
                    if not item_id or item_id in self.seen_message_ids:
                        continue

                    # Record message as seen
                    self.seen_message_ids.add(item_id)
                    if len(self.seen_message_ids) > 3000:
                        # Keep memory bounded
                        self.seen_message_ids = set(list(self.seen_message_ids)[-1500:])

                    sender_id = str(latest_item.get("user_id", ""))
                    if sender_id and sender_id == my_id:
                        # Ignore messages sent by ourselves
                        continue

                    item_type = latest_item.get("item_type", "")
                    user_text = latest_item.get("text", "")
                    if item_type != "text" or not user_text:
                        # Only text messages are answered for now
                        continue

                    # Determine sender name for friendly persona addressing
                    sender_name = "Friend"
                    for u in thread.get("users", []):
                        if str(u.get("pk", "")) == sender_id:
                            sender_name = u.get("full_name") or u.get("username") or "Friend"
                            break

                    LOGGER.info(f"📩 [Instagram DM] New message from {sender_name}: '{user_text}'")

                    # Generate AI response via Anshika sweet girl brain
                    reply_text = None
                    if generate_conversational_response is not None:
                        try:
                            reply_text = await generate_conversational_response(
                                user_text=user_text,
                                user_name=sender_name,
                                user_id=int(sender_id) if sender_id.isdigit() else None,
                            )
                        except Exception as ai_err:
                            LOGGER.warning(f"⚠️ [Instagram] AI response error: {ai_err}")

                    if not reply_text:
                        reply_text = "Hii! Kaise ho aap? 😊"


                    # Natural human delay before sending reply
                    typing_delay = 0.01 if self.poll_interval < 5 else random.uniform(2.0, 4.0)
                    await asyncio.sleep(typing_delay)


                    # Send reply back to thread
                    try:
                        await asyncio.to_thread(
                            self.client.send_direct_text,
                            text=reply_text,
                            thread_id=thread_id,
                        )
                        LOGGER.info(f"💌 [Instagram DM] Replied to {sender_name}: '{reply_text}'")
                    except Exception as send_err:
                        LOGGER.error(f"❌ [Instagram DM Send Error] Failed to reply in thread {thread_id}: {send_err}")

            except (ClientThrottledError, ClientSentryBlockError) as throttle_err:
                LOGGER.warning(f"⚠️ [Instagram Throttled] Backing off for 60s: {throttle_err}")
                await asyncio.sleep(60.0)
            except (asyncio.CancelledError, KeyboardInterrupt):
                break
            except Exception as loop_err:
                LOGGER.warning(f"⚠️ [Instagram Worker Notice] {loop_err}")
                await asyncio.sleep(10.0)

        LOGGER.info("🛑 [Instagram] Auto-reply userbot worker stopped.")

    async def start(self) -> bool:
        """
        Starts the Instagram Userbot background worker.
        """
        if self.is_running:
            return True

        login_success = await asyncio.to_thread(self.login)
        if not login_success:
            return False

        self.is_running = True
        self._worker_task = asyncio.create_task(self.worker_loop())
        return True

    async def stop(self) -> None:
        """
        Stops the Instagram Userbot gracefully.
        """
        self.is_running = False
        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        LOGGER.info("✅ [Instagram] Userbot safely terminated.")


# Global instance
_instagram_userbot_instance: Optional[InstagramUserbot] = None


async def start_instagram_bot() -> Optional[InstagramUserbot]:
    """
    Entry point to launch the Instagram bot if enabled in config.
    """
    global _instagram_userbot_instance

    is_enabled = getattr(config, "INSTAGRAM_BOT_ENABLED", False)
    if not is_enabled:
        LOGGER.info("ℹ️ [Instagram] Userbot is disabled (INSTAGRAM_BOT_ENABLED=False).")
        return None

    username = getattr(config, "INSTAGRAM_USERNAME", None)
    password = getattr(config, "INSTAGRAM_PASSWORD", None)

    if not username or not password:
        LOGGER.warning("⚠️ [Instagram] Userbot enabled but INSTAGRAM_USERNAME or INSTAGRAM_PASSWORD is missing.")
        return None

    bot = InstagramUserbot(username=username, password=password)
    started = await bot.start()
    if started:
        _instagram_userbot_instance = bot
        return bot
    return None


async def stop_instagram_bot() -> None:
    """
    Entry point to stop the Instagram bot gracefully on shutdown.
    """
    global _instagram_userbot_instance
    if _instagram_userbot_instance:
        await _instagram_userbot_instance.stop()
        _instagram_userbot_instance = None
