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
  Ye file Koyeb Cloud Server par bot ki RAM (Memory) aur Disk (Storage) par 24/7
  nazar rakhti hai (Sentinel Monitor).

Koyeb Free Tier me kya hota hai?
  Koyeb free tier 512MB RAM aur limited ephemeral disk deta hai. Agar memory leak
  ya temp files jama ho jayein, toh server band ho sakta hai. Isliye ye module:
  1. Har 10 minute me check karta hai.
  2. Jaise jaise memory ya storage 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90%
     par pahunchti hai, ye turant Owner (@Villanns) ko Telegram alert bhejta hai.
  3. 90% par aate hi automatic temp cache files (.mp3, .jpg) delete kar deta hai
     aur Python garbage collector (gc.collect()) run karke RAM release karta hai.
  4. Owner command: /storage ya /mem se live status dekh sakte hain.
================================================================================
"""

import os
import gc
import shutil
import time
import asyncio
import logging
from typing import Dict, Tuple, Set
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import config
from config import OWNER_ID
from nexichat import nexichat, SUDOERS

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# Step-by-step milestones to notify owner
MILESTONES = [10, 20, 30, 40, 50, 60, 70, 80, 90, 95]
_reported_ram_milestones: Set[int] = set()
_reported_disk_milestones: Set[int] = set()
_last_clean_time = 0
_last_auto_clean_report_time = 0


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

    # Pure standard library fallback: Read Linux /proc/meminfo directly
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
    except Exception as e:
        logger.debug(f"/proc/meminfo RAM check notice: {e}")

    return {"total_mb": 0.0, "used_mb": 0.0, "free_mb": 0.0, "percent": 0.0}


def clean_cache(max_age_seconds: int = 600) -> Tuple[int, float]:
    """
    Remove temporary cache files (.mp3 voice notes, .jpg images).
    If max_age_seconds <= 0, deletes all files in cache.
    Returns (files_deleted_count, megabytes_freed).
    """
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
    except Exception as e:
        logger.error(f"Error cleaning cache: {e}")

    # Trigger Python Garbage Collection to reclaim memory immediately
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
    """Standard inline keyboard for storage cards and milestone alerts."""
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


async def check_and_alert_storage(client: Client):
    """
    Periodic sentinel check:
    1. Tracks 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90% milestones.
    2. Sends real-time milestone alerts with [Clean Cache Now] & [Refresh] buttons.
    3. Auto-cleans cache when owner is unavailable at >= 85% and notifies owner with details.
    4. Guarantees learned memory is never lost (safely saved in Telegram & MongoDB).
    """
    global _reported_ram_milestones, _reported_disk_milestones, _last_clean_time

    now = time.time()
    if (now - _last_clean_time) > 1800:
        clean_cache(max_age_seconds=1200)
        _last_clean_time = now

    disk = get_disk_stats()
    ram = get_ram_stats()
    cache_files, cache_mb = get_cache_size()

    status_icon = "🟢 Healthy"
    if disk["percent"] >= 90 or ram["percent"] >= 90:
        status_icon = "🔴 Critical (>=90%)"
    elif disk["percent"] >= 70 or ram["percent"] >= 70:
        status_icon = "🟡 Warning (>=70%)"

    keyboard = get_sentinel_keyboard()

    # 1. Check RAM milestones (10% to 90%)
    current_ram_p = int(ram["percent"])
    for m in MILESTONES:
        if current_ram_p >= m and m not in _reported_ram_milestones:
            _reported_ram_milestones.add(m)
            alert_msg = (
                f"📊 **[KOYEB MEMORY MILESTONE : {m}%]** 📊\n"
                f"────────────────────────────\n"
                f"🔔 **RAM Usage has reached {m}%!**\n\n"
                f"• **RAM Usage:** `{ram['used_mb']} MB` / `{ram['total_mb']} MB` ({ram['percent']}%)\n"
                f"• **Disk Used:** `{disk['used_gb']} GB` / `{disk['total_gb']} GB` ({disk['percent']}%)\n"
                f"• **Disk Free:** `{disk['free_gb']} GB`\n"
                f"• **Cache Size:** `{cache_files} files` ({cache_mb} MB)\n"
                f"• **Status:** {status_icon}\n"
                f"────────────────────────────\n\n"
                f"💡 **Clean Suggestion:** Click below to flush temporary cache files (.mp3, .jpg) & release RAM without affecting any learned memory!\n\n"
                f"🛡️ **Safety Guarantee:** All learned Q&A & chats are 100% permanently stored in Telegram Cloud (>1000GB) & MongoDB."
            )
            try:
                await client.send_message(int(OWNER_ID), alert_msg, reply_markup=keyboard)
            except Exception as e:
                logger.debug(f"Failed to send RAM milestone alert: {e}")

    _reported_ram_milestones = {m for m in _reported_ram_milestones if current_ram_p >= (m - 4)}

    # 2. Check Disk milestones (10% to 90%)
    current_disk_p = int(disk["percent"])
    for m in MILESTONES:
        if current_disk_p >= m and m not in _reported_disk_milestones:
            _reported_disk_milestones.add(m)
            alert_msg = (
                f"💾 **[KOYEB STORAGE MILESTONE : {m}%]** 💾\n"
                f"────────────────────────────\n"
                f"🔔 **Disk Storage has reached {m}%!**\n\n"
                f"• **Disk Used:** `{disk['used_gb']} GB` / `{disk['total_gb']} GB` ({disk['percent']}%)\n"
                f"• **Disk Free:** `{disk['free_gb']} GB`\n"
                f"• **RAM Usage:** `{ram['used_mb']} MB` / `{ram['total_mb']} MB` ({ram['percent']}%)\n"
                f"• **Cache Size:** `{cache_files} files` ({cache_mb} MB)\n"
                f"• **Status:** {status_icon}\n"
                f"────────────────────────────\n\n"
                f"💡 **Clean Suggestion:** Temporary media cache can be cleared now to protect Koyeb free tier disk.\n\n"
                f"🛡️ **Safety Guarantee:** Your database on Telegram Cloud (>1000GB) & MongoDB is completely safe and unaffected!"
            )
            try:
                await client.send_message(int(OWNER_ID), alert_msg, reply_markup=keyboard)
            except Exception as e:
                logger.debug(f"Failed to send Disk milestone alert: {e}")

    _reported_disk_milestones = {m for m in _reported_disk_milestones if current_disk_p >= (m - 4)}

    # 3. Critical threshold check: Auto-clean when resource exceeds threshold
    global _last_auto_clean_report_time
    crit_threshold = float(getattr(config, "STORAGE_THRESHOLD", 90))
    if disk["percent"] >= crit_threshold or ram["percent"] >= crit_threshold:
        deleted, freed = clean_cache(max_age_seconds=0)
        gc.collect()
        if deleted > 0 or freed > 0:
            logger.info(f"High Resource Sentinel (>{crit_threshold}%): Auto-cleaned {deleted} files ({freed} MB).")
            # Debounce alert: At most once per 2 hours to prevent alert spamming
            if (now - _last_auto_clean_report_time) >= 7200:
                _last_auto_clean_report_time = now
                auto_report = (
                    f"🤖 **[KOYEB AUTO-CLEAN EXECUTED]** 🤖\n"
                    f"────────────────────────────\n"
                    f"⚠️ **High usage detected ({max(disk['percent'], ram['percent'])}%)!**\n"
                    f"Since owner action was pending, Sentinel automatically cleaned caches to protect your instance:\n\n"
                    f"• **Files Cleaned:** `{deleted} temp cache files`\n"
                    f"• **Space Freed:** `{freed} MB`\n"
                    f"• **RAM Action:** `gc.collect() executed`\n"
                    f"• **Learned Data:** `100% Safe in Telegram DB` ☁️\n"
                    f"────────────────────────────\n\n"
                    f"💡 System is running smoothly without lag or risk of crash! 🚀"
                )
                try:
                    await client.send_message(int(OWNER_ID), auto_report, reply_markup=keyboard)
                except Exception as e:
                    logger.debug(f"Failed to send auto-clean notification: {e}")


async def sentinel_monitor_loop(client: Client):
    """Background task monitoring storage and server health every 10 minutes."""
    logger.info("Storage & RAM Sentinel Monitor active with 10%-90% milestone tracking.")
    while True:
        try:
            await asyncio.sleep(600)  # Check every 10 minutes
            await check_and_alert_storage(client)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Sentinel monitor loop notice: {e}")
            await asyncio.sleep(60)


@nexichat.on_message(filters.command(["storage", "disk", "mem", "memory"]) & (SUDOERS | filters.user(int(OWNER_ID))))
async def storage_command(client: Client, message: Message):
    """Display real-time server disk, RAM, and cache diagnostics card."""
    gc.collect()
    disk = get_disk_stats()
    ram = get_ram_stats()
    cache_files, cache_mb = get_cache_size()

    status_icon = "🔴 Critical" if (disk["percent"] >= 90 or ram["percent"] >= 90) else ("🟡 Warning" if (disk["percent"] >= 70 or ram["percent"] >= 70) else "🟢 Optimal")

    text = f"""**
💾 Server Health & Storage 💾
────────────────────────────
🌸 **Server Health & Storage Monitor**
*Continuous 10% - 90% milestone reporting active!*

────────────────────────────
• **Disk Total:** `{disk['total_gb']} GB`
• **Disk Used:** `{disk['used_gb']} GB` ({disk['percent']}%)
• **Disk Free:** `{disk['free_gb']} GB`
• **RAM Usage:** `{ram['used_mb']} MB` / `{ram['total_mb']} MB` ({ram['percent']}%)
• **Cache Dir:** `{cache_files} files` ({cache_mb} MB)
• **Status:** {status_icon}
• **Auto-Alert:** Every 10% Step Milestone
• **Database:** Telegram Cloud (>1000GB) ☁️
────────────────────────────
📡 **Hosted on:** Koyeb Free Tier Cloud ☁️
👑 **Owner:** [Amrit Raj](https://t.me/Villanns) 💖**
"""
    await message.reply_text(text, reply_markup=get_sentinel_keyboard())


@nexichat.on_callback_query(filters.regex(r"^sentinel_"))
async def sentinel_callback_handler(client: Client, query: CallbackQuery):
    """Handle cache cleaning, refresh, and clean info guide."""
    user_id = query.from_user.id
    if user_id != int(OWNER_ID) and user_id not in SUDOERS:
        return await query.answer("Only the bot owner or sudoers can perform this action.", show_alert=True)

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
*Continuous 10% - 90% milestone reporting active!*

────────────────────────────
• **Disk Total:** `{disk['total_gb']} GB`
• **Disk Used:** `{disk['used_gb']} GB` ({disk['percent']}%)
• **Disk Free:** `{disk['free_gb']} GB`
• **RAM Usage:** `{ram['used_mb']} MB` / `{ram['total_mb']} MB` ({ram['percent']}%)
• **Cache Dir:** `{cache_files} files` ({cache_mb} MB)
• **Status:** {status_icon}
• **Auto-Alert:** Every 10% Step Milestone
• **Database:** Telegram Cloud (>1000GB) ☁️
────────────────────────────
{action_line}📡 **Hosted on:** Koyeb Free Tier Cloud ☁️
👑 **Owner:** [Amrit Raj](https://t.me/Villanns) 💖**
"""
    try:
        await query.message.edit_text(text, reply_markup=get_sentinel_keyboard())
    except Exception:
        pass
