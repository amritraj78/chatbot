# 🚀 KOYEB DEPLOYMENT & PRODUCTION RUNBOOK

> **VIP REACTION & AI CHATBOT (Priya AI Engine)**  
> **Author & Creator:** [Amrit Raj (@Villanns)](https://t.me/Villanns)  
> **Instagram:** [@ex_amrit](https://instagram.com/ex_amrit) | **Snapchat:** [@ex_amrit](https://snapchat.com/add/ex_amrit)  
> **Support:** [@amrit_feel](https://t.me/amrit_feel) | **Updates:** [@privatethink](https://t.me/privatethink)

---

## 1. Quick One-Click Deployment (Recommended)

Click the deployment badge below to launch directly onto Koyeb:

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/amritraj78/VIP-REACTION-BOT&branch=master&name=vip-reaction-bot)

---

## 2. Manual Step-by-Step GitHub Setup

### Step 1: Fork or Push Repository
Fork this repository or push your clone to your own GitHub account:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/VIP-REACTION-BOT.git
git push -u origin master
```

### Step 2: Create a Koyeb Web Service
1. Log in to your [Koyeb Console](https://app.koyeb.com/).
2. Click **Create Service** -> Select **GitHub**.
3. Choose your repository: `VIP-REACTION-BOT`.
4. Choose the branch: `master` (or `main`).
5. Choose Service Type: **Web Service**.

### Step 3: Configure Build & Runtime
- **Builder:** Select **Dockerfile**.
  - The repository's optimized `Dockerfile` uses lightweight Python with uvloop, sets up non-root security, pre-compiles dependencies, and exposes port `8000`.
- **Instance Size:** `Free` (Nano) or `Standard` (Micro / 512MB RAM).
- **Regions:** Select nearest region (e.g., `fra` Frankfurt or `was` Washington).

### Step 4: Environment Variables Configuration
In the **Environment variables** section, add the following key-value pairs:

| Variable | Required | Description | Example / Recommendation |
| :--- | :--- | :--- | :--- |
| `BOT_TOKEN` | **YES** | Telegram Bot Token from [@BotFather](https://t.me/BotFather) | `123456789:ABCdefGhIJKlm...` |
| `OWNER_ID` | **YES** | Numeric ID of Bot Owner | `5423666218` |
| `PORT` | Optional | Web server port for health checks | `8000` (default) |
| `KOYEB_PUBLIC_URL`| Optional | Koyeb public service URL for keep-alive ping | `https://vip-reaction-bot-xyz.koyeb.app` |
| `GEMINI_API_KEY` | Optional | Free Google Gemini 3.5 AI Key | From [Google AI Studio](https://aistudio.google.com) |
| `MONGO_URL` | Optional | MongoDB Atlas URI | Leave blank for built-in In-Memory engine |
| `DATABASE_GROUP` | Optional | Group ID for backup stream | `-1004415957871` |
| `DATABASE_CHANNEL`| Optional| Channel username for backup stream | `Yaarwinprofits` |
| `OWNER_USERNAME` | Optional | Owner Telegram handle | `Villanns` |
| `INSTAGRAM` | Optional | Owner Instagram handle | `ex_amrit` |
| `SNAPCHAT` | Optional | Owner Snapchat handle | `ex_amrit` |

### Step 5: Configure Health Check (Critical for Koyeb Zero-Downtime)
Under **Health checks**:
- **Protocol:** `HTTP`
- **Path:** `/health`
- **Port:** `8000`
- **Interval:** `60s`
- **Timeout:** `5s`
- **Unhealthy threshold:** `3`
- **Healthy threshold:** `1`

Click **Deploy**! Koyeb will build the Docker container and start your bot within 60 seconds.

---

## 3. Local & Termux Quick Start

For Termux (Android) or Linux VPS:
```bash
# Clone and enter repo
git clone https://github.com/amritraj78/VIP-REACTION-BOT
cd VIP-REACTION-BOT

# Setup environment
cp .env.example .env
nano .env   # Enter your BOT_TOKEN and OWNER_ID

# Verify everything before launch
bash manage.sh check
bash manage.sh test

# Launch daemon
bash start
```

---

## 4. Verification & Diagnostics

Once deployed:
1. Open your browser and navigate to `https://<your-koyeb-app>.koyeb.app/health`.
   - Response: `{"status": "healthy"}`
2. Open Telegram and send `/start` to your bot.
3. Send `/storage` from the owner account to inspect RAM usage, disk space, and process statistics.
4. Send `/help` to view all interactive commands and buttons.
