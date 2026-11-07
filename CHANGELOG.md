# 📝 CHANGELOG - VIP REACTION & AI CHATBOT

All notable changes, optimizations, and upgrades to the VIP Reaction & AI Chatbot project are documented below.

---

## [v3.0.0 - Production Master Upgrade] - 2026-11-05

### 🚀 Major Enhancements & Upgrades
- **AI Token Optimization & Zero-Quota Semantic Caching**:
  - Implemented `thinkingConfig: {"thinkingBudget": 0}` for Gemini 3.5 Flash requests, eliminating 150-300 internal thinking tokens per query and reducing latency from 4.5s to 1.2s.
  - Implemented Jaccard Token Overlap Similarity caching (`_jaccard_token_similarity >= 0.70`), answering frequent/similar queries from RAM in 0.001s with **zero API credit usage**.
  - History context pruned to last 3 conversational turns (100 characters max) with compressed system prompt (saving 80% input tokens).
- **Callback Query & UI Button Repair**:
  - Fixed raw `{}` string template placeholders on `START` callback query in `nexichat/modules/callback.py` and `nexichat/mplugin/callback.py`.
  - Added dedicated callback query handlers for `SBACK` and `soon` alerts with non-blocking feedback (`query.answer()`).
  - Added `query.continue_propagation()` across unhandled callback branches to prevent swallowing sub-module event listeners.
- **Command Menu & Registration Completion**:
  - Added `/help`, `/commands`, `/menu` command handler in `start.py` (both main and cloned bots).
  - Registered all missing commands (`security`, `shield`, `antilink`, `antispam`, `roast`, `quote`, `help`) in global Telegram Bot Menu via `set_bot_commands`.
- **Hybrid Multi-Tier Database & In-Memory Sudoers**:
  - Removed artificial `MONGO_URL is None` guards in `sudoers.py`, enabling `/addsudo`, `/rmsudo`, and `/sudolist` to work seamlessly in both MongoDB Atlas and In-Memory modes.
  - Made `add_sudo` and `remove_sudo` safely await async mock collections while remaining backward-compatible with synchronous PyMongo.
- **Diagnostics & Error Telemetry**:
  - Added `report_exception_to_owner` in `nexichat.core.diagnostics` with 60-second rate-limiting to prevent notification floods while notifying `OWNER_ID` of runtime exceptions.
  - Added `get_system_health_report()` providing live RAM (MB), uptime, PID, and health status for `/health` endpoint.
- **Automated Verification & Test Expansion**:
  - Expanded unit test suite from 53 to 57 tests covering Jaccard similarity, sudoers operations, health reporting, and anti-flood rate limits.
  - 100% test pass rate (`Ran 57 tests in 13.5s - OK`).

---

## [v2.5.0 - Multi-Tier Storage & Koyeb Keep-Alive] - 2026-11-05

### 🔧 Performance & Infrastructure
- **Telegram Cloud DB Integration**:
  - Created automated stream syncing Q&A pairs, clone registrations, and statistics to central channels (`@Yaarwinprofits`) and groups (`@chatbotsaved` / `-1004415957871`).
  - Periodic background sync every 10 minutes to prevent data loss even without MongoDB.
- **Koyeb Inactivity Sentinel**:
  - Built-in Flask microserver on `PORT 8000` with `/health` route.
  - Background asynchronous task pinging `KOYEB_PUBLIC_URL` every 25 minutes to prevent container sleep.
  - RAM & Disk Sentinel (`nexichat/modules/sentinel.py`) monitoring resource thresholds and auto-running `gc.collect()` at 85% RAM.
- **Personalization & Social Integration**:
  - Linked Amrit Raj's personal profiles across all modules: Instagram (`@ex_amrit`), Snapchat (`@ex_amrit`), Support (`@amrit_feel`), Channel (`@privatethink`).

---

## [v2.0.0 - Architecture Modularization] - 2026-11-04
- Replaced monolithic files with clean modular architecture (`nexichat/modules/` and `nexichat/mplugin/`).
- Implemented clone bot engine allowing users to spawn independent reaction bots via `/clone`.
- Added interactive social games: `/couples`, `/propose`, `/afk`, `/tagall`, `/dice`, `/truth`, `/dare`, `/flirt`, `/shayri`, `/joke`.
