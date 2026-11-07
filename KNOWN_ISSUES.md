# 📋 VIP REACTION & AI CHATBOT - KNOWN ISSUES & TROUBLESHOOTING GUIDE

> **Copyright (c) 2026 Amrit Raj (@Villanns)**  
> **Support Group:** [@amrit_feel](https://t.me/amrit_feel) | **Updates:** [@privatethink](https://t.me/privatethink)  
> **Instagram:** [@ex_amrit](https://instagram.com/ex_amrit) | **Snapchat:** [@ex_amrit](https://snapchat.com/add/ex_amrit)

---

## 1. Koyeb Free-Tier Instance Sleeping & Resource Limits

### Issue: Koyeb Free Instances Sleep After Inactivity
- **Root Cause:** Koyeb Free/Hobby tier containers scale to zero or idle sleep if no external HTTP traffic arrives on the declared port.
- **Implemented Mitigation:**
  1. A Flask micro-server listens on `PORT` (default `8000`) with endpoint `/health`.
  2. `nexichat.core.keepalive` runs a non-blocking background task that pings the declared `KOYEB_PUBLIC_URL` every 25 minutes.
  3. Pre-flight diagnostics automatically detect and bind to free fallback ports if port 8000 is occupied.
- **Best Practice & Limitation:** If Koyeb updates free tier policies to hard-pause containers after a monthly compute credit cutoff, automated self-pings cannot override Koyeb's billing platform. To guarantee 100% 24/7 uninterrupted uptime, upgrade to Koyeb Standard ($5/mo) or pair with an external monitor like UptimeRobot or Cron-Job.org hitting `https://<your-app>.koyeb.app/health`.

### Issue: 512MB RAM Container OOM (Out Of Memory) Crashes
- **Root Cause:** Running multiple cloned bots concurrently while holding thousands of Q&A pairs and in-memory chat histories in Python can push RAM above 512MB.
- **Implemented Mitigation:**
  1. Python GC thresholds tuned aggressively (`gc.set_threshold(700, 10, 10)`).
  2. LRU limits enforced across all in-memory collections:
     - `_qa_cache` capped to 2,500 entries.
     - `_replies_cache` capped to 1,500 entries.
     - `_stickers_cache` capped to 500 entries.
     - User conversational history capped to last 3 turns (100 chars each).
  3. `sentinel_monitor_loop` automatically triggers `gc.collect()` and purges ephemeral temp audio/image files if memory reaches 85%.

---

## 2. Telegram MTProto & Pyrogram Concurrency

### Issue: `sqlite3.OperationalError: database is locked` on Fast Restarts
- **Root Cause:** When Pyrogram crashes or is abruptly killed (`kill -9`), SQLite session files (`nexichat.session`) may remain locked by lingering file descriptors.
- **Implemented Mitigation:**
  1. `anony_boot()` in `nexichat/__main__.py` implements a graceful `finally:` block catching `asyncio.CancelledError` and `KeyboardInterrupt`, explicitly calling `await nexichat.stop()` to release database locks.
  2. `start` script cleanly cleans dangling `.session-journal` files before booting.
- **Prevention Strategy:** Always allow the bot to shut down gracefully using `SIGINT` (Ctrl+C) or `SIGTERM` rather than hard kills.

### Issue: `FloodWait` (Telegram API Rate Limiting)
- **Root Cause:** Triggering mass broadcast (`/gcast`), tag-all (`/tagall`), or rapid reactions across hundreds of groups too quickly triggers Telegram anti-flood limits (ranging from 10 seconds to several hours).
- **Implemented Mitigation:**
  1. `/tagall` pauses 2.5 seconds between each batch of 5 mentions.
  2. `/gcast` catches `FloodWait` exceptions and dynamically sleeps for `e.value` seconds without crashing.
  3. Auto-reactions use internal throttling to prevent duplicate reactions to the same message.

---

## 3. Gemini 3.5 AI Token Consumption & Thinking Latency

### Issue: High API Latency (4-6s) and Premature Quota Exhaustion
- **Root Cause:** Google's `gemini-3.5-flash` model defaults to internal multi-step "thinking" processes, consuming 150-300 hidden tokens per query and introducing 4+ seconds of latency.
- **Implemented Mitigation:**
  1. API payload explicitly specifies `"thinkingConfig": {"thinkingBudget": 0}`, cutting latency to 1.2s and saving 100% of thinking tokens.
  2. `maxOutputTokens` is capped at 250 for crisp, loving Priya responses.
  3. Token Overlap Jaccard Similarity Cache (`_jaccard_token_similarity >= 0.70`) serves frequent user questions from RAM in 0.001s with **0 API quota consumed**.

---

## 4. Database Disconnections & Offline Mode

### Issue: MongoDB Atlas IP Whitelist (`pymongo.errors.ServerSelectionTimeoutError`)
- **Root Cause:** MongoDB Atlas clusters block connections by default unless the hosting server's IP is whitelisted (`0.0.0.0/0`). Koyeb dynamic IPs change on every redeploy.
- **Implemented Mitigation:**
  1. `nexichat/__init__.py` catches connection timeouts and auto-switches to the built-in `InMemoryDatabase` with zero downtime.
  2. All learned Q&A, clones, and statistics are continuously backed up to the Telegram Cloud Database channel (`@Yaarwinprofits`) and group (`@chatbotsaved`).
  3. On startup, `sync_database_from_telegram()` automatically hydrates the in-memory database with previous records.

---

## 5. Summary of Diagnostic Tools

| Tool / Command | File / Component | Purpose |
| :--- | :--- | :--- |
| `bash manage.sh test` | `tests/test_features.py` | 57 automated unit tests covering all modules |
| `bash manage.sh check` | `nexichat/core/diagnostics.py` | Validates environment, port availability & tokens |
| `/storage` | `nexichat/modules/sentinel.py` | Real-time RAM, CPU, and disk usage report |
| `/ping` | `nexichat/modules/ping.py` | Telegram MTProto ping and gateway latency |
| `/exportdb` | `nexichat/modules/exportdb.py` | Complete JSON database export for backup |
| `/health` | `nexichat/core/keepalive.py` | JSON HTTP health check endpoint for Koyeb |
