# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT (Cloned Bot Plugin)
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
#  Licensed under Proprietary Terms. Unauthorized copying is strictly prohibited.
# ---------------------------------------------------------------------------------
"""
================================================================================
  FILE EXPLANATION & HINTS (Cloned Plugin Sentinel)
================================================================================
Is file ka kya kaam hai?
  Ye file Cloned Bots ke liye Koyeb Server Memory aur Storage statistics monitor
  karti hai. Bot owner /storage ya /mem type karke server RAM aur Disk check kar
  sakte hain.
================================================================================
"""

import os
import gc
import shutil
import time
import logging
from typing import Dict, Tuple
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from config import OWNER_ID
from nexichat.mplugin.helpers import is_owner

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def get_disk_stats() -> Dict[str, float]:
    """Calculate total, used, free disk storage in GB and percentage."""
    try:
        usage = shutil.disk_usage(BASE_DIR)
        total_gb = usage.total / (1024 ** 3)
        used_gb = usage.used / (1024 ** 3)
        free_gb = usage.free / (1024 ** 3)
        percent = (usage.used / usage.total) * 100 if usage.total > 0 else 0.0
        return {
            "total_gb": round(total_gb, 2),
            "used_gb": round(used_gb, 2),
            "free_gb": round(free_gb, 2),
            "percent": round(percent, 1),
        }
    except Exception as e:
        logger.error(f"Failed to check disk usage: {e}")
        return {"total_gb": 0.0, "used_gb": 0.0, "free_gb": 0.0, "percent": 0.0}


def get_ram_stats() -> Dict[str, float]:
    """Calculate RAM usage percentage using psutil or /proc/meminfo."""
    try:
        import psutil
        mem = psutil.virtual_memory()
        if hasattr(mem, "percent") and isinstance(mem.percent, (int, float)):
            return {
                "total_mb": round(mem.total / (1024 ** 2), 1),
                "used_mb": round(mem.used / (1024 ** 2), 1),
                "free_mb": round(mem.available / (1024 ** 2), 1),
                "percent": round(float(mem.percent), 1),
            }
    except ImportError:
        pass
    except Exception:
        pass

    try:
        if os.path.exists("/proc/meminfo"):
            mem = {}
            with open("/proc/meminfo", "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        mem[parts[0].strip()] = int(parts[1].strip().split()[0])
            total_kb = mem.get("MemTotal", 1)
            avail_kb = mem.get("MemAvailable", mem.get("MemFree", 0) + mem.get("Buffers", 0) + mem.get("Cached", 0))
            used_kb = total_kb - avail_kb
            percent = (used_kb / total_kb) * 100 if total_kb > 0 else 0.0
            return {
                "total_mb": round(total_kb / 1024, 1),
                "used_mb": round(used_kb / 1024, 1),
                "free_mb": round(avail_kb / 1024, 1),
                "percent": round(float(percent), 1),
            }
    except Exception:
        pass

    return {"total_mb": 0.0, "used_mb": 0.0, "free_mb": 0.0, "percent": 0.0}


def clean_cache(max_age_seconds: int = 600) -> Tuple[int, float]:
    """Remove temporary cache files."""
    files_deleted = 0
    bytes_freed = 0
    now = time.time()
    try:
        if os.path.exists(CACHE_DIR):
            for filename in os.listdir(CACHE_DIR):
                if filename == ".gitkeep":
                    continue
                filepath = os.path.join(CACHE_DIR, filename)
                if os.path.isfile(filepath):
                    file_age = now - os.path.getmtime(filepath)
                    if max_age_seconds <= 0 or file_age >= max_age_seconds:
                        size = os.path.getsize(filepath)
                        try:
                            os.remove(filepath)
                            files_deleted += 1
                            bytes_freed += size
                        except Exception:
                            pass
    except Exception:
        pass

    gc.collect()
    mb_freed = round(bytes_freed / (1024 ** 2), 2)
    return files_deleted, mb_freed


def get_cache_size() -> Tuple[int, float]:
    """Get total number of files and total size in MB currently in cache."""
    count = 0
    total_bytes = 0
    try:
        if os.path.exists(CACHE_DIR):
            for filename in os.listdir(CACHE_DIR):
                if filename == ".gitkeep":
                    continue
                filepath = os.path.join(CACHE_DIR, filename)
                if os.path.isfile(filepath):
                    count += 1
                    total_bytes += os.path.getsize(filepath)
    except Exception:
        pass
    return count, round(total_bytes / (1024 ** 2), 2)


def get_sentinel_keyboard() -> InlineKeyboardMarkup:
    """Standard inline keyboard for storage cards."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🧹 ᴄʟᴇᴀɴ ᴄᴀᴄʜᴇ ɴᴏᴡ", callback_data="sentinel_clean_cache"),
                InlineKeyboardButton("🔄 ʀᴇғʀᴇsʜ", callback_data="sentinel_refresh"),
            ],
            [
                InlineKeyboardButton("ℹ️ ᴡʜᴀᴛ ɢᴇᴛs ᴄʟᴇᴀɴᴇᴅ & ᴡʜʏ?", callback_data="sentinel_info_clean"),
            ],
        ]
    )


@Client.on_message(filters.command(["storage", "disk", "mem", "memory"]))
async def storage_command(client: Client, message: Message):
    """Display real-time server disk, RAM, and cache diagnostics card."""
    bot_id = client.me.id
    user_id = message.from_user.id
    if not await is_owner(bot_id, user_id) and user_id != int(OWNER_ID):
        return await message.reply_text("You don't have permission to use this command.")

    gc.collect()
    disk = get_disk_stats()
    ram = get_ram_stats()
    cache_files, cache_mb = get_cache_size()

    status_icon = "🔴 Critical" if (disk["percent"] >= 90 or ram["percent"] >= 90) else ("🟡 Warning" if (disk["percent"] >= 70 or ram["percent"] >= 70) else "🟢 Optimal")

    text = f"""**
💾 Server Health & Storage 💾
────────────────────────────
🌸 **Server Health & Storage Monitor**

────────────────────────────
• **Disk Total:** `{disk['total_gb']} GB`
• **Disk Used:** `{disk['used_gb']} GB` ({disk['percent']}%)
• **Disk Free:** `{disk['free_gb']} GB`
• **RAM Usage:** `{ram['used_mb']} MB` / `{ram['total_mb']} MB` ({ram['percent']}%)
• **Cache Dir:** `{cache_files} files` ({cache_mb} MB)
• **Status:** {status_icon}
• **Database:** Telegram Cloud (>1000GB) ☁️
────────────────────────────
📡 **Hosted on:** Koyeb Free Tier Cloud ☁️
👑 **Owner:** [Amrit Raj](https://t.me/Villanns) 💖**
"""
    await message.reply_text(text, reply_markup=get_sentinel_keyboard())


@Client.on_callback_query(filters.regex(r"^sentinel_"))
async def sentinel_callback_handler(client: Client, query: CallbackQuery):
    """Handle cache cleaning, refresh, and clean info guide."""
    bot_id = client.me.id
    user_id = query.from_user.id
    if not await is_owner(bot_id, user_id) and user_id != int(OWNER_ID):
        return await query.answer("Only the bot owner can perform this action.", show_alert=True)

    action_text = ""
    if query.data == "sentinel_clean_cache":
        deleted, freed = clean_cache(max_age_seconds=0)
        gc.collect()
        action_text = f"🧹 Cleaned {deleted} cache files ({freed} MB freed)!\nPython RAM released via gc.collect().\n🛡️ All learned data safe in Telegram DB!"
        await query.answer(f"Cleaned {deleted} files ({freed} MB freed)! Memory released.", show_alert=True)
    elif query.data == "sentinel_info_clean":
        info_msg = (
            "ℹ️ [KOYEB STORAGE & CLEANING GUIDE]\n\n"
            "❓ What gets cleaned & Why?\n"
            "• cache/ directory: Temp audio (.mp3) & images (.jpg) are cleared to stop disk buildup.\n"
            "• Python RAM heap: gc.collect() frees unused objects for Koyeb 512MB RAM.\n\n"
            "🛡️ Learned Memory Safety Guarantee:\n"
            "• Aapka bot jo bhi seekhta hai, wo Telegram Channel (>1000GB) aur MongoDB me 100% safe hai.\n"
            "• Cache clean karne se seekha hua data KABHI delete nahi hota!"
        )
        return await query.answer(info_msg, show_alert=True)
    elif query.data == "sentinel_refresh":
        await query.answer("Diagnostics refreshed! 🔄")

    gc.collect()
    disk = get_disk_stats()
    ram = get_ram_stats()
    cache_files, cache_mb = get_cache_size()
    status_icon = "🔴 Critical" if (disk["percent"] >= 90 or ram["percent"] >= 90) else ("🟡 Warning" if (disk["percent"] >= 70 or ram["percent"] >= 70) else "🟢 Optimal")

    action_line = f"✨ *{action_text}*\n" if action_text else ""
    text = f"""**
💾 Server Health & Storage 💾
────────────────────────────
🌸 **Server Health & Storage Monitor**

────────────────────────────
• **Disk Total:** `{disk['total_gb']} GB`
• **Disk Used:** `{disk['used_gb']} GB` ({disk['percent']}%)
• **Disk Free:** `{disk['free_gb']} GB`
• **RAM Usage:** `{ram['used_mb']} MB` / `{ram['total_mb']} MB` ({ram['percent']}%)
• **Cache Dir:** `{cache_files} files` ({cache_mb} MB)
• **Status:** {status_icon}
• **Database:** Telegram Cloud (>1000GB) ☁️
────────────────────────────
{action_line}📡 **Hosted on:** Koyeb Free Tier Cloud ☁️
👑 **Owner:** [Amrit Raj](https://t.me/Villanns) 💖**
"""
    try:
        await query.message.edit_text(text, reply_markup=get_sentinel_keyboard())
    except Exception:
        pass
