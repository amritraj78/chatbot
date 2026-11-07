# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT - TELEGRAM WEB APP (MINI APP)
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
# ---------------------------------------------------------------------------------

WEBAPP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Anshika AI • Mini App</title>
  <!-- Telegram WebApp JS SDK -->
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      --bg-color: #0b0f19;
      --card-bg: rgba(23, 32, 51, 0.75);
      --card-border: rgba(244, 114, 182, 0.18);
      --text-color: #f3f4f6;
      --text-muted: #9ca3af;
      --primary-color: #ec4899;
      --primary-gradient: linear-gradient(135deg, #f43f5e 0%, #ec4899 50%, #8b5cf6 100%);
      --bubble-anshika: rgba(30, 41, 59, 0.9);
      --bubble-user: linear-gradient(135deg, #ec4899, #8b5cf6);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      -webkit-tap-highlight-color: transparent;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    body {
      background-color: var(--bg-color);
      color: var(--text-color);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      overflow-x: hidden;
      background-image: 
        radial-gradient(circle at 10% 10%, rgba(236, 72, 153, 0.12) 0%, transparent 40%),
        radial-gradient(circle at 90% 90%, rgba(139, 92, 246, 0.12) 0%, transparent 40%);
    }

    .app-container {
      max-width: 520px;
      margin: 0 auto;
      width: 100%;
      display: flex;
      flex-direction: column;
      height: 100vh;
      position: relative;
    }

    /* Header Profile Card */
    .profile-card {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--card-border);
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      flex-shrink: 0;
    }

    .profile-header {
      display: flex;
      align-items: center;
      gap: 14px;
    }

    .avatar-wrapper {
      position: relative;
      width: 58px;
      height: 58px;
      flex-shrink: 0;
    }

    .avatar {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      background: var(--primary-gradient);
      padding: 2.5px;
      box-shadow: 0 4px 14px rgba(236, 72, 153, 0.35);
    }

    .avatar img {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      object-fit: cover;
      background: #1e293b;
    }

    .online-badge {
      position: absolute;
      bottom: 2px;
      right: 2px;
      width: 13px;
      height: 13px;
      background: #10b981;
      border: 2px solid var(--bg-color);
      border-radius: 50%;
      animation: pulse 2s infinite;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.7; transform: scale(1.15); }
    }

    .profile-info {
      flex: 1;
    }

    .profile-name-row {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .profile-name {
      font-size: 19px;
      font-weight: 700;
      letter-spacing: -0.3px;
    }

    .flower-badge {
      font-size: 16px;
    }

    .profile-tagline {
      font-size: 12.5px;
      color: var(--text-muted);
      margin-top: 2px;
    }

    .profile-status {
      display: inline-flex;
      align-items: center;
      gap: 5px;
      font-size: 11px;
      font-weight: 600;
      color: #10b981;
      background: rgba(16, 185, 129, 0.12);
      padding: 2px 8px;
      border-radius: 12px;
      margin-top: 4px;
    }

    .chips-row {
      display: flex;
      gap: 6px;
      overflow-x: auto;
      padding-bottom: 2px;
      scrollbar-width: none;
    }
    .chips-row::-webkit-scrollbar { display: none; }

    .chip {
      font-size: 11px;
      font-weight: 500;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(255, 255, 255, 0.08);
      color: var(--text-muted);
      padding: 3px 9px;
      border-radius: 10px;
      white-space: nowrap;
    }

    /* Chat Area */
    .chat-container {
      flex: 1;
      overflow-y: auto;
      padding: 16px 14px;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .chat-container::-webkit-scrollbar { width: 4px; }
    .chat-container::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }

    .msg-row {
      display: flex;
      align-items: flex-end;
      gap: 8px;
      max-width: 86%;
      animation: fadeIn 0.25s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .msg-row.anshika {
      align-self: flex-start;
    }

    .msg-row.user {
      align-self: flex-end;
      flex-direction: row-reverse;
    }

    .msg-avatar {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: var(--primary-gradient);
      padding: 1.5px;
      flex-shrink: 0;
      margin-bottom: 2px;
    }

    .msg-avatar img {
      width: 100%;
      height: 100%;
      border-radius: 50%;
      object-fit: cover;
    }

    .msg-bubble {
      padding: 10px 14px;
      border-radius: 18px;
      font-size: 14px;
      line-height: 1.45;
      word-break: break-word;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }

    .msg-row.anshika .msg-bubble {
      background: var(--bubble-anshika);
      color: var(--text-color);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-bottom-left-radius: 4px;
    }

    .msg-row.user .msg-bubble {
      background: var(--bubble-user);
      color: #ffffff;
      border-bottom-right-radius: 4px;
    }

    .msg-time {
      font-size: 10px;
      color: rgba(255, 255, 255, 0.55);
      margin-top: 4px;
      text-align: right;
    }

    /* Typing Indicator */
    .typing-indicator {
      display: none;
      align-self: flex-start;
      background: var(--bubble-anshika);
      padding: 10px 16px;
      border-radius: 18px;
      border-bottom-left-radius: 4px;
      border: 1px solid rgba(255, 255, 255, 0.08);
      gap: 4px;
      align-items: center;
      margin-left: 36px;
    }

    .typing-indicator.active {
      display: flex;
    }

    .typing-dot {
      width: 6px;
      height: 6px;
      background: var(--primary-color);
      border-radius: 50%;
      animation: typingBounce 1.4s infinite ease-in-out both;
    }

    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }

    @keyframes typingBounce {
      0%, 80%, 100% { transform: scale(0); opacity: 0.4; }
      40% { transform: scale(1); opacity: 1; }
    }

    /* Quick Suggestions */
    .suggestions-container {
      padding: 0 14px 10px 14px;
      display: flex;
      gap: 7px;
      overflow-x: auto;
      scrollbar-width: none;
      flex-shrink: 0;
    }
    .suggestions-container::-webkit-scrollbar { display: none; }

    .sugg-pill {
      background: rgba(236, 72, 153, 0.12);
      border: 1px solid rgba(236, 72, 153, 0.3);
      color: #fbcfe8;
      font-size: 12px;
      padding: 6px 12px;
      border-radius: 14px;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.2s ease;
    }

    .sugg-pill:active {
      transform: scale(0.95);
      background: rgba(236, 72, 153, 0.25);
    }

    /* Input Bar */
    .input-bar {
      padding: 10px 14px 14px 14px;
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border-top: 1px solid var(--card-border);
      display: flex;
      align-items: center;
      gap: 8px;
      flex-shrink: 0;
    }

    .chat-input {
      flex: 1;
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 22px;
      padding: 11px 16px;
      color: #ffffff;
      font-size: 14px;
      outline: none;
      transition: border 0.2s ease;
    }

    .chat-input:focus {
      border-color: var(--primary-color);
    }

    .send-btn {
      width: 42px;
      height: 42px;
      border-radius: 50%;
      background: var(--primary-gradient);
      border: none;
      color: white;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 4px 12px rgba(236, 72, 153, 0.4);
      transition: transform 0.15s ease;
      flex-shrink: 0;
    }

    .send-btn:active {
      transform: scale(0.92);
    }

    .send-btn svg {
      width: 18px;
      height: 18px;
      fill: currentColor;
      margin-left: 2px;
    }

    /* Bottom Quick Action Bar */
    .quick-actions {
      display: flex;
      justify-content: space-around;
      padding: 8px 12px;
      background: rgba(11, 15, 25, 0.95);
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      font-size: 11px;
    }

    .qa-btn {
      color: var(--text-muted);
      text-decoration: none;
      display: flex;
      align-items: center;
      gap: 4px;
      padding: 4px 8px;
      border-radius: 8px;
      transition: color 0.2s;
    }

    .qa-btn:hover, .qa-btn:active {
      color: #f472b6;
    }
  </style>
</head>
<body>
  <div class="app-container">
    <!-- Profile Card Header -->
    <div class="profile-card">
      <div class="profile-header">
        <div class="avatar-wrapper">
          <div class="avatar">
            <img src="https://telegra.ph/file/0c9a59b207dfec2b0716b.jpg" alt="Anshika" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Anshika&backgroundColor=ec4899';">
          </div>
          <div class="online-badge" title="Active"></div>
        </div>
        <div class="profile-info">
          <div class="profile-name-row">
            <h1 class="profile-name">Anshika</h1>
            <span class="flower-badge">🌸</span>
          </div>
          <div class="profile-tagline">17yo Student • Chamoli, Uttarakhand</div>
          <div class="profile-status">● Active & Ready to Chat</div>
        </div>
      </div>
      <div class="chips-row">
        <span class="chip">🏔️ Chamoli (UK)</span>
        <span class="chip">📚 Class 12</span>
        <span class="chip">💬 Natural Hinglish</span>
        <span class="chip">🌸 Friendly & Witty</span>
      </div>
    </div>

    <!-- Live Chat Messages -->
    <div class="chat-container" id="chatContainer">
      <div class="msg-row anshika">
        <div class="msg-avatar">
          <img src="https://telegra.ph/file/0c9a59b207dfec2b0716b.jpg" alt="Anshika" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Anshika&backgroundColor=ec4899';">
        </div>
        <div class="msg-bubble">
          Hii! Main Anshika hoon! Chamoli se... Padhai se thoda break liya tha. Aap batao kaise ho? 😊🌸
          <div class="msg-time" id="initTime">Just now</div>
        </div>
      </div>

      <div class="typing-indicator" id="typingIndicator">
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
      </div>
    </div>

    <!-- Quick Suggestion Chips -->
    <div class="suggestions-container">
      <div class="sugg-pill" onclick="sendSuggestion('Kaise ho aap? 😊')">Kaise ho? 😊</div>
      <div class="sugg-pill" onclick="sendSuggestion('Kahan se ho aap? 🏔️')">Kahan se ho? 🏔️</div>
      <div class="sugg-pill" onclick="sendSuggestion('Ek pyari si shayari sunao 🌸')">Shayari sunao 🌸</div>
      <div class="sugg-pill" onclick="sendSuggestion('Ek funny joke sunao 😂')">Joke sunao 😂</div>
      <div class="sugg-pill" onclick="sendSuggestion('Class 12 ki padhai kaisi chal rahi? 📚')">Padhai kaisi chal rahi? 📚</div>
    </div>

    <!-- Input Bar -->
    <div class="input-bar">
      <input type="text" id="chatInput" class="chat-input" placeholder="Type a message for Anshika..." autocomplete="off">
      <button class="send-btn" id="sendBtn" onclick="sendMessage()">
        <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
      </button>
    </div>

    <!-- Quick Actions Footer -->
    <div class="quick-actions">
      <a href="https://t.me/amrit_feel" target="_blank" class="qa-btn">💬 Support Group</a>
      <a href="https://t.me/privatethink" target="_blank" class="qa-btn">📢 Updates Channel</a>
      <a href="https://t.me/Villanns" target="_blank" class="qa-btn">👑 Creator</a>
      <a href="https://t.me/anishikabot?startgroup=true" target="_blank" class="qa-btn">➕ Add Bot</a>
    </div>
  </div>

  <script>
    // Initialize Telegram WebApp
    const tg = window.Telegram?.WebApp;
    let userName = "Friend";
    let userId = null;

    if (tg) {
      try {
        tg.ready();
        tg.expand();
        if (tg.enableClosingConfirmation) tg.enableClosingConfirmation();
        if (tg.initDataUnsafe?.user) {
          userName = tg.initDataUnsafe.user.first_name || "Friend";
          userId = tg.initDataUnsafe.user.id || null;
        }
      } catch (e) {
        console.log("Telegram SDK init note:", e);
      }
    }

    const chatContainer = document.getElementById('chatContainer');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const typingIndicator = document.getElementById('typingIndicator');

    function getCurrentTime() {
      const now = new Date();
      return now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    document.getElementById('initTime').textContent = getCurrentTime();

    function scrollToBottom() {
      setTimeout(() => {
        chatContainer.scrollTop = chatContainer.scrollHeight;
      }, 50);
    }

    function appendMessage(text, sender) {
      const row = document.createElement('div');
      row.className = `msg-row ${sender}`;

      if (sender === 'anshika') {
        row.innerHTML = `
          <div class="msg-avatar">
            <img src="https://telegra.ph/file/0c9a59b207dfec2b0716b.jpg" alt="Anshika" onerror="this.src='https://api.dicebear.com/7.x/bottts/svg?seed=Anshika&backgroundColor=ec4899';">
          </div>
          <div class="msg-bubble">
            ${escapeHtml(text)}
            <div class="msg-time">${getCurrentTime()}</div>
          </div>
        `;
      } else {
        row.innerHTML = `
          <div class="msg-bubble">
            ${escapeHtml(text)}
            <div class="msg-time">${getCurrentTime()}</div>
          </div>
        `;
      }

      chatContainer.insertBefore(row, typingIndicator);
      scrollToBottom();
    }

    function escapeHtml(string) {
      const div = document.createElement('div');
      div.innerText = string;
      return div.innerHTML;
    }

    function sendSuggestion(text) {
      if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred('light');
      chatInput.value = text;
      sendMessage();
    }

    async function sendMessage() {
      const text = chatInput.value.trim();
      if (!text) return;

      if (tg?.HapticFeedback) tg.HapticFeedback.impactOccurred('light');

      appendMessage(text, 'user');
      chatInput.value = '';
      chatInput.focus();

      typingIndicator.classList.add('active');
      scrollToBottom();

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: text,
            user_name: userName,
            user_id: userId
          })
        });

        const data = await response.json();
        typingIndicator.classList.remove('active');

        if (data && data.reply) {
          appendMessage(data.reply, 'anshika');
          if (tg?.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
        } else {
          appendMessage("Main ekdum mast hoon yrr! Tum sunao?", 'anshika');
        }
      } catch (err) {
        typingIndicator.classList.remove('active');
        appendMessage("Arey lagta hai connection slow hai thoda! Fir se bolo na?", 'anshika');
      }
    }

    chatInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        sendMessage();
      }
    });
  </script>
</body>
</html>
"""
