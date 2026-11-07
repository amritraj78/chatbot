# Contributing to VIP Reaction & AI Chatbot

Thank you for your interest in contributing to **VIP Reaction & AI Chatbot**! 🎉

This repository is maintained by **[Amrit Raj](https://t.me/Villanns)** (Instagram: [@ex_amrit](https://instagram.com/ex_amrit) | Snapchat: [@ex_amrit](https://snapchat.com/add/ex_amrit)).

---

## 📂 Architecture Overview

The codebase is organized following clean architectural separation:

- **`nexichat/core/`**: Core infrastructure modules (Pre-flight diagnostic validator, 24/7 keepalive health server on port 8000, ASCII banners).
- **`nexichat/database/`**: Central Telegram Cloud DB (`telegram_db.py`), In-memory LRU cache + MongoDB (`chatbot.py`), reaction settings (`reactions.py`), and clone stats (`clonestats.py`).
- **`nexichat/modules/`**: Main bot plugins and command handlers (`start.py`, `chatbot.py`, `reaction.py`, `games.py`, `security.py`, `sentinel.py`, `welcome.py`, etc.).
- **`nexichat/mplugin/`**: Cloned bot plugins mirroring the main features with isolated user/chat tracking.
- **`tests/`**: Unit test suite covering all architecture, diagnostic, and feature modules.

---

## 🛠️ Local Development & Testing

1. Clone your fork and enter the directory:
   ```bash
   git clone https://github.com/<your-username>/VIP-REACTION-BOT.git
   cd VIP-REACTION-BOT
   ```

2. Run pre-flight check:
   ```bash
   bash manage.sh check
   ```

3. Run the full unit test suite:
   ```bash
   bash manage.sh test
   ```

---

## 📋 Guidelines

- **PEP 8 Lowercase Filenames**: All module files must strictly follow lowercase snake_case (e.g. `broadcast.py`, `security.py`).
- **Zero Package Breakage**: Avoid introducing heavy C-dependencies that break lightweight environments like Termux or Koyeb free tier.
- **Memory Discipline**: Any in-memory cache must respect the LRU bounds (max 2,500 items) to guarantee memory stays under Koyeb's 512MB RAM limit.
- **Unit Testing**: Always run `bash manage.sh test` and ensure all tests pass before submitting a Pull Request.

---

## 💬 Community & Support

- **Telegram Support Group:** [@amrit_feel](https://t.me/amrit_feel)
- **Updates Channel:** [@privatethink](https://t.me/privatethink)
- **Developer:** [Amrit Raj (@Villanns)](https://t.me/Villanns)
