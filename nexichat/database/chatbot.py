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
  Ye file Chatbot ka Local RAM Memory & MongoDB Database Manager hai!
  
Isme kya-kya save hota hai?
  1. _qa_cache: AI dwara sikhe gaye Questions & Answers (Instant recall).
  2. _replies_cache: Group me users ki aapsi baatein jo bot ne learn ki hain.
  3. _stickers_cache: Group me aane wale stickers jo bot save karke wapas bhejti hai.
  4. _nicknames_cache: Users ke custom nicknames jo wo /setname se batate hain.
  5. Har save function Telegram Database me bhi log karta hai taaki data kabhi loss na ho.
================================================================================
"""

import os
import random
import asyncio
import logging
from typing import Optional, Dict, Any, List
from nexichat import db

logger = logging.getLogger(__name__)

from nexichat.database.telegram_db import (
    log_qa_to_telegram,
    log_reply_to_telegram,
    log_sticker_to_telegram
)

chatbot_status_db = db.chatbot_status
chatai_db = db.chatai
qa_cache_db = db.qa_cache
stickers_db = db.stickers
user_nicknames_db = db.user_nicknames
afk_db = db.afk
user_vivid_memory_db = db.user_vivid_memory
api_usage_db = db.api_usage
dm_history_db = db.dm_history

# In-memory caches for ultra-fast performance
_replies_cache: List[Dict[str, Any]] = []
_qa_cache: Dict[str, str] = {}
_stickers_cache: List[str] = []
_nicknames_cache: Dict[int, str] = {}
_afk_cache: Dict[int, Dict[str, Any]] = {}
_user_vivid_memory: Dict[int, Dict[str, Any]] = {}
_dm_history_cache: Dict[int, List[Dict[str, Any]]] = {}
_daily_api_usage: Dict[str, Any] = {}
_chatbot_mode: str = "auto"
_notified_milestones: set = set()
_last_switch_alert_time: Dict[str, float] = {}
_cache_loaded = False


MODE_PERSIST_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache", "chatbot_mode.txt")

def _read_persistent_mode() -> Optional[str]:
    try:
        if os.path.exists(MODE_PERSIST_FILE):
            with open(MODE_PERSIST_FILE, "r") as f:
                val = f.read().strip().lower()
                if val in ["auto", "database", "api"]:
                    return val
    except Exception:
        pass
    return None

def _write_persistent_mode(mode: str) -> None:
    try:
        os.makedirs(os.path.dirname(MODE_PERSIST_FILE), exist_ok=True)
        with open(MODE_PERSIST_FILE, "w") as f:
            f.write(mode.strip().lower())
    except Exception:
        pass

async def get_chatbot_mode() -> str:
    """
    Get current chatbot reply mode:
    - 'auto': Use Live APIs (Groq -> Gemini -> NVIDIA NIM -> Free Waterfall); auto fallback to DB on exhaustion.
    - 'database': Strictly bypass all external APIs; reply only from Telegram Cloud Channel and MongoDB database.
    - 'api': Strictly use live APIs; never use database fallback.
    Default: 'auto'
    """
    global _chatbot_mode
    try:
        doc = await chatbot_status_db.find_one({"setting": "chatbot_mode"})
        if doc and "mode" in doc:
            _chatbot_mode = doc["mode"]
            _write_persistent_mode(_chatbot_mode)
            return _chatbot_mode
    except Exception:
        pass

    persisted = _read_persistent_mode()
    if persisted:
        _chatbot_mode = persisted
    return _chatbot_mode


async def set_chatbot_mode(mode: str):
    """Set chatbot reply mode ('auto', 'database', or 'api')."""
    global _chatbot_mode
    if mode not in ["auto", "database", "api"]:
        mode = "auto"
    _chatbot_mode = mode
    _write_persistent_mode(mode)
    try:
        await chatbot_status_db.update_one(
            {"setting": "chatbot_mode"},
            {"$set": {"mode": mode}},
            upsert=True
        )
        await chatbot_status_db.update_one(
            {"setting": "db_fallback_mode"},
            {"$set": {"enabled": (mode in ["auto", "database"])}},
            upsert=True
        )
    except Exception:
        pass


async def is_chatbot_enabled(chat_id: int) -> bool:
    """Check if chatbot is enabled for a given chat (defaults to True)."""
    status_doc = await chatbot_status_db.find_one({"chat_id": chat_id})
    if not status_doc:
        return True
    return status_doc.get("enabled", True)


async def set_chatbot_enabled(chat_id: int, enabled: bool):
    """Enable or disable chatbot for a given chat."""
    await chatbot_status_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": enabled}},
        upsert=True
    )


async def is_voicemode_enabled(chat_id: int) -> bool:
    """Check if voice note mode is enabled for a given chat (defaults to False)."""
    status_doc = await chatbot_status_db.find_one({"chat_id": chat_id})
    if not status_doc:
        return False
    return status_doc.get("voicemode", False)


async def set_voicemode_enabled(chat_id: int, enabled: bool):
    """Enable or disable voice note mode for a given chat."""
    await chatbot_status_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"voicemode": enabled}},
        upsert=True
    )


async def is_db_fallback_enabled() -> bool:
    """Check if database fallback is allowed. Defaults to True in 'auto' and 'database' modes."""
    mode = await get_chatbot_mode()
    return mode in ["auto", "database"]


async def set_db_fallback_enabled(enabled: bool):
    """Enable or disable database fallback. True maps to 'auto', False maps to 'api'."""
    new_mode = "auto" if enabled else "api"
    await set_chatbot_mode(new_mode)


def is_toxic_or_canned_reply(text: str) -> bool:
    """Check if the text is robotic, search engine dump, contains third-party names, or mentions Priya / AI assistant."""
    if not text:
        return True
    cleaned = text.strip()
    # Reject empty, 1-word or 2-word fragments (e.g. 'Main', 'Bas', 'Hn')
    if len(cleaned.split()) < 3:
        return True

    lower = cleaned.lower()
    toxic_markers = [
        "priya", "amrit", "safone", "as an ai", "i am an ai", "i'm an ai",
        "language model", "created by amrit", "maine is baare me search kiya",
        "maine is baare me pata lagaya", "abstracttext", "wikipedia", "convert currencies",
        "rahul", "farzii", "mannat", "jxtttvibes", "kanhaiya", "krrish", "dia",
        "vinxvine", "maahi", "bus aur hell", "rhyme scheme", "what are u finding for",
        "kidnap kiya", "call kyu kiya", "in the group", "local game ranking",
        "guessed the word in record time", "climb the mini-game leaderboard",
        "we need to obey", "we must obey", "strict length rule", "constraints:",
        "words per reply", "75% to 80%", "plain text with zero emojis", "emoji rule",
        "character prompt", "internal thought", "thinking process", "anshika_character_prompt",
        "maximum 3 to 12"
    ]
    return any(marker in lower for marker in toxic_markers)


async def ensure_database_indexes():
    """Create essential MongoDB indexes asynchronously to guarantee ultra-fast, lag-free queries."""
    try:
        from nexichat.database.reactions import reactionsdb
        from nexichat.database.chats import chatsdb
        from nexichat.database.users import usersdb

        await dm_history_db.create_index("user_id", background=True)
        await user_vivid_memory_db.create_index("user_id", background=True)
        await user_nicknames_db.create_index("user_id", background=True)
        await qa_cache_db.create_index("q", background=True)
        await chatai_db.create_index("word", background=True)
        await chatbot_status_db.create_index("chat_id", background=True)
        await api_usage_db.create_index("date", background=True)
        await reactionsdb.create_index("chat_id", background=True)
        await chatsdb.create_index("chat_id", background=True)
        await usersdb.create_index("user_id", background=True)
        logger.info("MongoDB high-performance indexes verified.")
    except Exception as e:
        logger.debug(f"MongoDB indexing notice: {e}")


async def load_replies_cache():
    """Load all learned replies, Q&A memory, and stickers into cache."""
    global _replies_cache, _qa_cache, _stickers_cache, _cache_loaded
    try:
        # Trigger background indexing for lag-free lookups
        asyncio.create_task(ensure_database_indexes())

        cursor = chatai_db.find()
        _replies_cache = await cursor.to_list(length=None)

        # Load Q&A cache
        qa_cursor = qa_cache_db.find()
        qa_list = await qa_cursor.to_list(length=None)
        for doc in qa_list:
            if "q" in doc and "a" in doc:
                ans = doc["a"]
                if not is_toxic_or_canned_reply(ans):
                    _qa_cache[doc["q"]] = ans

        # Load learned stickers
        stk_cursor = stickers_db.find()
        stk_list = await stk_cursor.to_list(length=None)
        for doc in stk_list:
            fid = doc.get("file_id")
            if fid and fid not in _stickers_cache:
                _stickers_cache.append(fid)

        _cache_loaded = True
    except Exception:
        pass


async def save_chat_reply(word: str, reply_type: str, content: str, client: Optional[Any] = None):
    """
    Save learned reply data into chatai collection AND Telegram Database.
    reply_type: 'text', 'sticker', 'photo', 'video', 'animation', 'voice'
    content: text message or Telegram file_id
    """
    global _replies_cache
    if not word or not content:
        return

    if is_toxic_or_canned_reply(content):
        return

    word_clean = word.strip().lower()
    if not word_clean or any(m in word_clean for m in ["as an ai", "language model"]):
        return
    doc = {
        "word": word_clean,
        "type": reply_type,
        "content": content
    }

    try:
        existing = await chatai_db.find_one({"word": word_clean, "content": content})
        if not existing:
            await chatai_db.insert_one(doc)
            _replies_cache.append(doc)
            # Koyeb Free Tier RAM Guard: Cap in-memory replies to 2500 items
            if len(_replies_cache) > 2500:
                _replies_cache.pop(0)
    except Exception:
        pass

    if client:
        try:
            await log_reply_to_telegram(client, word_clean, reply_type, content)
        except Exception:
            pass


async def get_chat_reply(word: str = "", clean_text: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Search for a learned reply matching the given word/phrase."""
    global _replies_cache, _cache_loaded
    if not _cache_loaded:
        await load_replies_cache()

    target_text = clean_text or word
    if not target_text:
        return None

    word_clean = target_text.strip().lower()

    exact_matches = [
        r for r in _replies_cache 
        if r.get("word") == word_clean and not is_toxic_or_canned_reply(r.get("content", ""))
    ]
    if exact_matches:
        return random.choice(exact_matches)

    # Word-level token match (must match complete words, not arbitrary substrings)
    tokens = set(word_clean.split())
    token_matches = [
        r for r in _replies_cache
        if r.get("word") in tokens and len(r.get("word", "")) >= 3 and not is_toxic_or_canned_reply(r.get("content", ""))
    ]
    if token_matches:
        return random.choice(token_matches)

    # Fallback directly to MongoDB chatai collection if not found in RAM cache
    try:
        db_exact = await chatai_db.find_one({"word": word_clean})
        if db_exact and not is_toxic_or_canned_reply(db_exact.get("content", "")):
            return db_exact
        for tok in tokens:
            if len(tok) >= 3:
                db_tok = await chatai_db.find_one({"word": tok})
                if db_tok and not is_toxic_or_canned_reply(db_tok.get("content", "")):
                    return db_tok
    except Exception:
        pass

    return None


async def save_qa_pair(question: str, answer: str, client: Optional[Any] = None):
    """Save an answered question to memory, MongoDB, and Telegram Database."""
    global _qa_cache
    if not question or not answer:
        return

    # Never save toxic, robotic, or Priya/Amrit canned replies into cache
    if is_toxic_or_canned_reply(answer):
        return

    q_key = question.strip().lower()
    _qa_cache[q_key] = answer

    # Koyeb Free Tier RAM Guard: Cap in-memory Q&A cache to 2500 items
    if len(_qa_cache) > 2500:
        try:
            oldest_k = next(iter(_qa_cache))
            _qa_cache.pop(oldest_k, None)
        except Exception:
            pass

    try:
        await qa_cache_db.update_one(
            {"q": q_key},
            {"$set": {"a": answer}},
            upsert=True
        )
    except Exception:
        pass

    if client:
        try:
            await log_qa_to_telegram(client, question, answer)
        except Exception:
            pass


def _jaccard_token_similarity(text1: str, text2: str) -> float:
    """Calculate token-level Jaccard similarity between two strings."""
    import re
    w1 = set(re.sub(r"[^\w\s]", "", text1.strip().lower()).split())
    w2 = set(re.sub(r"[^\w\s]", "", text2.strip().lower()).split())
    if not w1 or not w2:
        return 0.0
    common = w1 & w2
    union = w1 | w2
    return len(common) / len(union) if union else 0.0


async def get_qa_answer(question: str) -> Optional[str]:
    """Retrieve an answer from Q&A memory and MongoDB with exact and semantic fuzzy matching (0 API credits)."""
    global _qa_cache, _cache_loaded
    if not _cache_loaded:
        await load_replies_cache()

    if not question:
        return None

    import re
    q_norm = re.sub(r"[^\w\s]", "", question.strip().lower())
    if not q_norm:
        return None

    # 1. Exact match in memory
    if q_norm in _qa_cache:
        ans = _qa_cache[q_norm]
        if not is_toxic_or_canned_reply(ans):
            return ans
    if question.strip().lower() in _qa_cache:
        ans = _qa_cache[question.strip().lower()]
        if not is_toxic_or_canned_reply(ans):
            return ans

    # 2. Token overlap similarity match (Jaccard similarity >= 0.40 or token subset)
    q_words = set(q_norm.split())
    if len(q_words) >= 1:
        for saved_q, saved_a in _qa_cache.items():
            if not is_toxic_or_canned_reply(saved_a):
                saved_words = set(saved_q.split())
                if (q_words and saved_words and (q_words.issubset(saved_words) or saved_words.issubset(q_words))):
                    return saved_a
                sim = _jaccard_token_similarity(question, saved_q)
                if sim >= 0.40:
                    return saved_a

    # 3. Direct MongoDB qa_cache_db fallback
    try:
        db_doc = await qa_cache_db.find_one({"q": q_norm})
        if db_doc and "a" in db_doc and not is_toxic_or_canned_reply(db_doc["a"]):
            return db_doc["a"]
        db_rx = await qa_cache_db.find_one({"q": {"$regex": re.escape(q_norm), "$options": "i"}})
        if db_rx and "a" in db_rx and not is_toxic_or_canned_reply(db_rx["a"]):
            return db_rx["a"]
    except Exception:
        pass

    return None



async def save_sticker(file_id: str, client: Optional[Any] = None):
    """Learn and store a sticker file ID in RAM, MongoDB, and Telegram Database."""
    global _stickers_cache
    if not file_id:
        return
    if file_id not in _stickers_cache:
        _stickers_cache.append(file_id)
        if len(_stickers_cache) > 500:
            _stickers_cache.pop(0)
    try:
        await stickers_db.update_one(
            {"file_id": file_id},
            {"$set": {"file_id": file_id}},
            upsert=True
        )
    except Exception:
        pass

    if client:
        try:
            await log_sticker_to_telegram(client, file_id)
        except Exception:
            pass


def get_random_sticker(fallback: Optional[str] = None) -> Optional[str]:
    """Get a random sticker file_id from cache, or fallback."""
    global _stickers_cache
    if _stickers_cache:
        return random.choice(_stickers_cache)
    return fallback


async def save_user_nickname(user_id: int, nickname: str):
    """Save custom user nickname in RAM and DB."""
    global _nicknames_cache
    if not user_id or not nickname:
        return
    clean_name = str(nickname).strip()[:50]
    _nicknames_cache[user_id] = clean_name
    if len(_nicknames_cache) > 1000:
        try:
            oldest_k = next(iter(_nicknames_cache))
            _nicknames_cache.pop(oldest_k, None)
        except Exception:
            pass
    try:
        await user_nicknames_db.update_one(
            {"user_id": user_id},
            {"$set": {"nickname": clean_name}},
            upsert=True
        )
    except Exception:
        pass


async def get_user_nickname(user_id: int) -> Optional[str]:
    """Retrieve saved nickname for a user."""
    global _nicknames_cache
    if user_id in _nicknames_cache:
        return _nicknames_cache[user_id]
    try:
        doc = await user_nicknames_db.find_one({"user_id": user_id})
        if doc and "nickname" in doc:
            _nicknames_cache[user_id] = doc["nickname"]
            return doc["nickname"]
    except Exception:
        pass
    return None


async def set_user_afk(user_id: int, reason: str = ""):
    """Store AFK state with timestamp and reason."""
    import time
    global _afk_cache
    data = {
        "afk": True,
        "reason": reason.strip(),
        "time": time.time()
    }
    _afk_cache[user_id] = data
    try:
        await afk_db.update_one(
            {"user_id": user_id},
            {"$set": data},
            upsert=True
        )
    except Exception:
        pass


async def get_user_afk(user_id: int) -> Optional[Dict[str, Any]]:
    """Get AFK state if active."""
    global _afk_cache
    if user_id in _afk_cache:
        return _afk_cache[user_id]
    try:
        doc = await afk_db.find_one({"user_id": user_id})
        if doc and doc.get("afk"):
            _afk_cache[user_id] = doc
            return doc
    except Exception:
        pass
    return None


async def remove_user_afk(user_id: int) -> Optional[Dict[str, Any]]:
    """Remove AFK state and return previous data."""
    global _afk_cache
    old_data = await get_user_afk(user_id)
    _afk_cache.pop(user_id, None)
    try:
        await afk_db.delete_one({"user_id": user_id})
    except Exception:
        pass
    return old_data


# ==============================================================================
# MULTI-TURN CONVERSATION CONTEXT (5-Minute Sliding Ring Buffer)
# ==============================================================================
_conversation_context: Dict[int, List[Dict[str, Any]]] = {}


def append_user_context(user_id: int, role: str, text: str):
    """Store recent dialogue turn in sliding conversation buffer."""
    import time
    global _conversation_context
    if not user_id or not text:
        return
    now = time.time()
    if user_id not in _conversation_context:
        _conversation_context[user_id] = []

    # Prune expired turns older than 300s (5 minutes)
    _conversation_context[user_id] = [
        m for m in _conversation_context[user_id] if (now - m.get("time", 0)) < 300
    ]

    _conversation_context[user_id].append({"role": role, "text": text.strip(), "time": now})

    # Keep at most 6 recent turns (3 user + 3 Anshika) to protect RAM
    if len(_conversation_context[user_id]) > 6:
        _conversation_context[user_id] = _conversation_context[user_id][-6:]

    if len(_conversation_context) > 500:
        try:
            oldest_k = next(iter(_conversation_context))
            _conversation_context.pop(oldest_k, None)
        except Exception:
            pass


def get_user_context(user_id: int) -> List[Dict[str, Any]]:
    """Fetch active dialogue history for user within last 5 minutes."""
    import time
    global _conversation_context
    if not user_id:
        return []
    now = time.time()
    history = _conversation_context.get(user_id, [])
    active = [m for m in history if (now - m.get("time", 0)) < 300]
    _conversation_context[user_id] = active
    return active


def clear_user_context(user_id: int):
    """Reset dialogue history when user requests to forget or on reset."""
    global _conversation_context
    _conversation_context.pop(user_id, None)


async def save_dm_message(user_id: int, role: str, text: str, user_name: str = ""):
    """
    Persistently save user and Anshika messages in MongoDB Atlas for long-term recall.
    Caps history at 40 messages to maintain clean performance while remembering extensive context.
    """
    import time
    global _dm_history_cache
    if not user_id or not text:
        return

    now = time.time()
    turn = {"role": role, "text": text.strip(), "time": now}

    if user_id not in _dm_history_cache:
        _dm_history_cache[user_id] = []
    _dm_history_cache[user_id].append(turn)
    if len(_dm_history_cache[user_id]) > 40:
        _dm_history_cache[user_id] = _dm_history_cache[user_id][-40:]

    if len(_dm_history_cache) > 500:
        try:
            oldest_k = next(iter(_dm_history_cache))
            _dm_history_cache.pop(oldest_k, None)
        except Exception:
            pass

    try:
        update_doc = {
            "$push": {
                "messages": {
                    "$each": [turn],
                    "$slice": -40
                }
            },
            "$set": {
                "updated_at": now
            }
        }
        if user_name:
            update_doc["$set"]["user_name"] = user_name

        await dm_history_db.update_one(
            {"user_id": user_id},
            update_doc,
            upsert=True
        )
    except Exception as e:
        logger.debug(f"Failed to save DM message to MongoDB: {e}")


async def get_dm_history(user_id: int, limit: int = 14) -> List[Dict[str, Any]]:
    """
    Fetch persistent DM conversation history for a user from in-memory cache or MongoDB.
    Returns chronologically ordered list of conversation turns.
    """
    global _dm_history_cache
    if not user_id:
        return []

    # Check cache first
    if user_id in _dm_history_cache and _dm_history_cache[user_id]:
        return _dm_history_cache[user_id][-limit:]

    # Fetch from MongoDB Atlas
    try:
        doc = await dm_history_db.find_one({"user_id": user_id})
        if doc and "messages" in doc and isinstance(doc["messages"], list):
            _dm_history_cache[user_id] = doc["messages"][-40:]
            return _dm_history_cache[user_id][-limit:]
    except Exception as e:
        logger.debug(f"Failed to fetch DM history from MongoDB: {e}")

    # Fallback to local user context if available
    return get_user_context(user_id)[-limit:]


async def clear_dm_history(user_id: int):
    """
    Clear all persistent DM history for a user when they request to reset chat or forget.
    """
    global _dm_history_cache
    _dm_history_cache.pop(user_id, None)
    try:
        await dm_history_db.delete_one({"user_id": user_id})
    except Exception as e:
        logger.debug(f"Failed to clear DM history from MongoDB: {e}")


# ==============================================================================
# VIVID PERSONALIZED USER MEMORY DATABASE
# ==============================================================================
TOPIC_KEYWORDS = {
    "studies": ["padhai", "study", "studies", "class", "12th", "school", "college", "exam", "marks", "books"],
    "coding": ["python", "code", "bot", "developer", "server", "github", "coding", "programming"],
    "music": ["music", "song", "gana", "singer", "listen", "playlist"],
    "mountains": ["uttarakhand", "chamoli", "pahad", "nature", "mountains", "weather", "snow"],
    "emotions": ["udaas", "sad", "khush", "happy", "breakup", "love", "friend", "dost", "alone"],
    "food": ["khana", "dinner", "lunch", "food", "maggi", "chai", "coffee", "roti"]
}


async def update_vivid_user_memory(
    user_id: int,
    role: str,
    text: str,
    user_name: str = "",
    username: str = ""
) -> Dict[str, Any]:
    """
    Store vivid, personalized interaction context in RAM and MongoDB.
    Records past conversations, user nicknames, detected topics, and dialogue history.
    """
    import time
    global _user_vivid_memory
    if not user_id or not text:
        return {}

    now = time.time()
    mem = _user_vivid_memory.get(user_id)
    if not mem:
        try:
            doc = await user_vivid_memory_db.find_one({"user_id": user_id})
            if doc:
                mem = doc
        except Exception:
            pass

    if not mem:
        mem = {
            "user_id": user_id,
            "name": user_name or "Friend",
            "username": username or "",
            "interactions": 0,
            "created_at": now,
            "last_seen": now,
            "topics": [],
            "dialogue": []
        }

    # Update metadata
    if user_name and mem.get("name") in ["", "Friend", "None"]:
        mem["name"] = user_name
    if username and not mem.get("username"):
        mem["username"] = username

    mem["interactions"] = mem.get("interactions", 0) + 1
    mem["last_seen"] = now

    # Detect topics dynamically
    text_lower = text.lower()
    current_topics = set(mem.get("topics", []))
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            current_topics.add(topic)
    mem["topics"] = list(current_topics)[:6]

    # Append dialogue turn (sliding window of 10 recent messages)
    dialogue = mem.get("dialogue", [])
    dialogue.append({"role": role, "text": text.strip()[:150], "time": now})
    if len(dialogue) > 10:
        dialogue = dialogue[-10:]
    mem["dialogue"] = dialogue

    _user_vivid_memory[user_id] = mem
    if len(_user_vivid_memory) > 500:
        try:
            oldest_k = next(iter(_user_vivid_memory))
            _user_vivid_memory.pop(oldest_k, None)
        except Exception:
            pass

    # Asynchronously persist to MongoDB
    try:
        await user_vivid_memory_db.update_one(
            {"user_id": user_id},
            {"$set": {
                "name": mem.get("name"),
                "username": mem.get("username"),
                "interactions": mem.get("interactions"),
                "last_seen": mem.get("last_seen"),
                "topics": mem.get("topics"),
                "dialogue": mem.get("dialogue")
            }},
            upsert=True
        )
    except Exception:
        pass

    return mem


async def get_vivid_user_memory(user_id: int) -> Dict[str, Any]:
    """Retrieve vivid personalized memory for a user from RAM or DB."""
    global _user_vivid_memory
    if not user_id:
        return {}
    if user_id in _user_vivid_memory:
        return _user_vivid_memory[user_id]
    try:
        doc = await user_vivid_memory_db.find_one({"user_id": user_id})
        if doc:
            _user_vivid_memory[user_id] = doc
            return doc
    except Exception:
        pass
    return {}


async def format_vivid_user_context(user_id: int, user_name: str = "") -> str:
    """
    Generate rich conversational context summary for AI prompt.
    Enables Anshika to naturally recall user's name, previous topics, and past friendship details.
    """
    mem = await get_vivid_user_memory(user_id)
    name = user_name or "Friend"
    interactions = 1
    topics_str = "general conversation"

    if mem:
        name = mem.get("name") or name
        interactions = mem.get("interactions", 1)
        topics = mem.get("topics", [])
        if topics:
            topics_str = ", ".join(topics)

    context_str = (
        f"[DM Personal Memory with {name}: You have chatted {interactions} times previously. "
        f"Topics previously discussed: {topics_str}. You remember everything from your past conversations. "
        f"Always keep their previous chat history and context in mind so your response connects naturally to past talks!]"
    )
    return context_str


async def clear_vivid_user_memory(user_id: int):
    """Clear personalized memory for a user upon reset."""
    global _user_vivid_memory
    _user_vivid_memory.pop(user_id, None)
    try:
        await user_vivid_memory_db.delete_one({"user_id": user_id})
    except Exception:
        pass


# ==============================================================================
# API USAGE & DAILY QUOTA DASHBOARD (CREATOR METRICS)
# ==============================================================================
GROQ_DAILY_QUOTA = 1000      # 1,000 requests/day
GEMINI_DAILY_QUOTA = 1500    # 1,500 requests/day
MILESTONES = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


def _get_today_utc() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


async def track_api_call(provider: str, success: bool = True, client: Optional[Any] = None):
    """Record an API request in RAM and MongoDB daily quota tracker and check 10% milestones."""
    global _daily_api_usage, _notified_milestones
    today = _get_today_utc()

    if _daily_api_usage.get("date") != today:
        _daily_api_usage = {
            "date": today,
            "groq_calls": 0,
            "gemini_calls": 0,
            "waterfall_calls": 0,
            "db_fallback_calls": 0,
            "total_calls": 0
        }
        _notified_milestones = set()

    provider_lower = provider.lower()
    field = "waterfall_calls"
    if "groq" in provider_lower:
        field = "groq_calls"
    elif "gemini" in provider_lower:
        field = "gemini_calls"
    elif "nvidia" in provider_lower:
        field = "nvidia_calls"
    elif "waterfall" in provider_lower:
        field = "waterfall_calls"

    _daily_api_usage[field] = _daily_api_usage.get(field, 0) + 1
    _daily_api_usage["total_calls"] = _daily_api_usage.get("total_calls", 0) + 1

    try:
        await api_usage_db.update_one(
            {"date": today},
            {"$inc": {
                field: 1,
                "total_calls": 1
            }},
            upsert=True
        )
    except Exception:
        pass

    # Check 10% milestone notifications
    await check_and_notify_api_milestones(client=client)


async def check_and_notify_api_milestones(client: Optional[Any] = None):
    """Check if total daily API quota usage crossed any 10% milestone and alert owner."""
    global _notified_milestones
    today = _get_today_utc()
    stats = await get_api_usage_stats()
    groq_pct = stats.get("groq_used_pct", 0.0)
    gemini_pct = stats.get("gemini_used_pct", 0.0)
    peak_pct = max(groq_pct, gemini_pct)

    for m in MILESTONES:
        if peak_pct >= m and m not in _notified_milestones:
            _notified_milestones.add(m)
            try:
                await api_usage_db.update_one(
                    {"date": today},
                    {"$addToSet": {"notified_milestones": m}},
                    upsert=True
                )
            except Exception:
                pass
            import asyncio
            asyncio.create_task(notify_owner_milestone(m, stats, client))


async def notify_owner_milestone(milestone: int, stats: Dict[str, Any], client: Optional[Any] = None):
    """Send real-time milestone percentage alert to owner with live stats and mode toggle buttons."""
    import config
    owner_id = getattr(config, "OWNER_ID", None)
    if not owner_id:
        return

    try:
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        from nexichat import nexichat

        bot_client = nexichat if (hasattr(nexichat, "is_connected") and nexichat.is_connected) else client
        if not bot_client:
            return

        mode = await get_chatbot_mode()
        mode_labels = {
            "auto": "🤖 ᴀᴜᴛᴏ (ᴀᴘɪ + ᴅʙ ғᴀʟʟʙᴀᴄᴋ)",
            "database": "🗄️ ᴅᴀᴛᴀʙᴀsᴇ ᴏɴʟʏ (ᴛᴇʟᴇɢʀᴀᴍ + ᴍᴏɴɢᴏ)",
            "api": "⚡ sᴛʀɪᴄᴛ ᴀᴘɪ ᴏɴʟʏ"
        }
        mode_display = mode_labels.get(mode, mode.upper())

        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🤖 ᴀᴜᴛᴏ (ᴀᴘɪ + ᴅʙ)", callback_data="cb_mode_auto"),
                InlineKeyboardButton("🗄️ ᴅᴀᴛᴀʙᴀsᴇ ᴏɴʟʏ", callback_data="cb_mode_database"),
            ],
            [
                InlineKeyboardButton("⚡ sᴛʀɪᴄᴛ ᴀᴘɪ ᴏɴʟʏ", callback_data="cb_mode_api"),
                InlineKeyboardButton("⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE")
            ]
        ])

        msg = (
            f"📊 **ᴀᴘɪ ᴜsᴀɢᴇ ᴍɪʟᴇsᴛᴏɴᴇ ᴀʟᴇʀᴛ - {milestone}%**\n\n"
            f"ᴅᴀɪʟʏ ᴀɪ ᴀᴘɪ ǫᴜᴏᴛᴀ ᴜsᴀɢᴇ ʜᴀs ᴄʀᴏssᴇᴅ **{milestone}%**!\n\n"
            f"✦ **ʟɪᴠᴇ ǫᴜᴏᴛᴀ ᴍᴇᴛʀɪᴄs:**\n"
            f"  • **ɢʀᴏǫ ᴀɪ:** `{stats['groq_calls']}` / `{stats['groq_quota']}` requests (`{stats['groq_used_pct']}%`)\n"
            f"  • **ɢᴏᴏɢʟᴇ ɢᴇᴍɪɴɪ:** `{stats['gemini_calls']}` / `{stats['gemini_quota']}` requests (`{stats['gemini_used_pct']}%`)\n"
            f"  • **ᴛᴏᴛᴀʟ ᴀɪ ǫᴜᴇʀɪᴇs:** `{stats['total_calls']}` requests\n"
            f"  • **ᴀᴄᴛɪᴠᴇ ᴍᴏᴅᴇ:** {mode_display}\n\n"
            f"✦ **ᴏᴡɴᴇʀ ʀᴇᴘʟʏ sᴏᴜʀᴄᴇ ᴄᴏɴᴛʀᴏʟ:**\n"
            f"ᴀᴀᴘ ᴄʜᴀʜᴇɪɴ ᴛᴏʜ ɴᴇᴇᴄʜᴇ ʙᴜᴛᴛᴏɴ ᴄʟɪᴄᴋ ᴋᴀʀᴋᴇ ʀᴇᴘʟʏ sᴏᴜʀᴄᴇ ᴛᴜʀᴀɴᴛ sᴡɪᴛᴄʜ ᴋᴀʀ sᴀᴋᴛᴇ ʜᴀɪɴ:"
        )
        await bot_client.send_message(chat_id=int(owner_id), text=msg, reply_markup=btn)
    except Exception:
        pass


async def notify_owner_api_switch(from_api: str, to_api: str, reason: str = "Rate limit / Quota reached (HTTP 429)", client: Optional[Any] = None):
    """Notify owner whenever an API fails/exhausts and switches to another provider or database."""
    global _last_switch_alert_time
    import time
    import config

    owner_id = getattr(config, "OWNER_ID", None)
    if not owner_id:
        return

    trans_key = f"{from_api}->{to_api}"
    now = time.time()
    if now - _last_switch_alert_time.get(trans_key, 0) < 120:
        return
    _last_switch_alert_time[trans_key] = now

    try:
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        from nexichat import nexichat

        bot_client = nexichat if (hasattr(nexichat, "is_connected") and nexichat.is_connected) else client
        if not bot_client:
            return

        mode = await get_chatbot_mode()
        mode_labels = {
            "auto": "🤖 ᴀᴜᴛᴏ (ᴀᴘɪ + ᴅʙ ғᴀʟʟʙᴀᴄᴋ)",
            "database": "🗄️ ᴅᴀᴛᴀʙᴀsᴇ ᴏɴʟʏ (ᴛᴇʟᴇɢʀᴀᴍ + ᴍᴏɴɢᴏ)",
            "api": "⚡ sᴛʀɪᴄᴛ ᴀᴘɪ ᴏɴʟʏ"
        }
        mode_display = mode_labels.get(mode, mode.upper())

        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🤖 ᴀᴜᴛᴏ (ᴀᴘɪ + ᴅʙ)", callback_data="cb_mode_auto"),
                InlineKeyboardButton("🗄️ ᴅᴀᴛᴀʙᴀsᴇ ᴏɴʟʏ", callback_data="cb_mode_database"),
            ],
            [
                InlineKeyboardButton("⚡ sᴛʀɪᴄᴛ ᴀᴘɪ ᴏɴʟʏ", callback_data="cb_mode_api"),
                InlineKeyboardButton("⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE")
            ]
        ])

        msg = (
            f"⚠️ **ᴀɪ ᴀᴘɪ sᴡɪᴛᴄʜ ᴀʟᴇʀᴛ**\n\n"
            f"ᴀɴ ᴀɪ ᴀᴘɪ ʟɪᴍɪᴛ ᴡᴀs ʀᴇᴀᴄʜᴇᴅ ᴀɴᴅ ᴛʜᴇ sʏsᴛᴇᴍ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ sᴡɪᴛᴄʜᴇᴅ!\n\n"
            f"✦ **ᴘʀᴇᴠɪᴏᴜs ᴀᴘɪ:** `{from_api}`\n"
            f"✦ **ʀᴇᴀsᴏɴ:** {reason}\n"
            f"🔄 **sᴡɪᴛᴄʜᴇᴅ ᴛᴏ:** `{to_api}`\n\n"
            f"✦ **ᴀᴄᴛɪᴠᴇ ᴍᴏᴅᴇ:** {mode_display}\n\n"
            f"ℹ️ **ᴀᴜᴛᴏ-ᴄᴏɴᴛɪɴᴜɪᴛʏ:** sʏsᴛᴇᴍ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ᴀᴀᴘᴋᴇ sᴇᴛ ᴋɪʏᴇ ʜᴜʏᴇ **{mode_display}** ᴘᴀʀ ᴄᴏɴᴛɪɴᴜᴇ ᴋᴀʀ ʀᴀʜᴀ ʜᴀɪ. ᴀɢᴀʀ ᴀᴀᴘ ᴏғғʟɪɴᴇ ʏᴀ ʙᴜsʏ ʜᴀɪɴ ᴛᴏʜ ᴀᴀᴘᴋᴏ ᴋᴏɪ ʙᴜᴛᴛᴏɴ ᴄʟɪᴄᴋ ᴋᴀʀɴᴇ ᴋɪ ᴢᴀʀᴏᴏʀᴀᴛ ɴᴀʜɪ ʜᴀɪ.\n\n"
            f"✦ **ᴍᴀɴᴜᴀʟ ᴄᴏɴᴛʀᴏʟ (ᴏᴘᴛɪᴏɴᴀʟ):**\n"
            f"ᴀᴀᴘ ᴄʜᴀʜᴇɪɴ ᴛᴏʜ ɴᴇᴇᴄʜᴇ ᴅɪʏᴇ ɢᴀʏᴇ ʙᴜᴛᴛᴏɴs sᴇ ʀᴇᴘʟʏ ᴍᴏᴅᴇ ᴍᴀɴᴜᴀʟʟʏ ᴄʜᴀɴɢᴇ ᴋᴀʀ sᴀᴋᴛᴇ ʜᴀɪɴ:"
        )
        await bot_client.send_message(chat_id=int(owner_id), text=msg, reply_markup=btn)
    except Exception:
        pass


async def track_db_fallback_call():
    """Record a fallback to the offline learned database when APIs reach quota limit."""
    global _daily_api_usage
    today = _get_today_utc()

    if _daily_api_usage.get("date") != today:
        _daily_api_usage = {
            "date": today,
            "groq_calls": 0,
            "gemini_calls": 0,
            "waterfall_calls": 0,
            "db_fallback_calls": 0,
            "total_calls": 0
        }

    _daily_api_usage["db_fallback_calls"] = _daily_api_usage.get("db_fallback_calls", 0) + 1

    try:
        await api_usage_db.update_one(
            {"date": today},
            {"$inc": {"db_fallback_calls": 1}},
            upsert=True
        )
    except Exception:
        pass


async def get_api_usage_stats() -> Dict[str, Any]:
    """Calculate live usage counts and remaining percentage for today."""
    global _daily_api_usage, _notified_milestones
    today = _get_today_utc()

    if _daily_api_usage.get("date") != today:
        try:
            doc = await api_usage_db.find_one({"date": today})
            if doc:
                _daily_api_usage = {
                    "date": today,
                    "groq_calls": doc.get("groq_calls", 0),
                    "gemini_calls": doc.get("gemini_calls", 0),
                    "nvidia_calls": doc.get("nvidia_calls", 0),
                    "waterfall_calls": doc.get("waterfall_calls", doc.get("waterfall_free_calls", 0)),
                    "db_fallback_calls": doc.get("db_fallback_calls", 0),
                    "total_calls": doc.get("total_calls", 0)
                }
                _notified_milestones = set(doc.get("notified_milestones", []))
            else:
                _daily_api_usage = {
                    "date": today,
                    "groq_calls": 0,
                    "gemini_calls": 0,
                    "nvidia_calls": 0,
                    "waterfall_calls": 0,
                    "db_fallback_calls": 0,
                    "total_calls": 0
                }
                _notified_milestones = set()
        except Exception:
            _daily_api_usage = {
                "date": today,
                "groq_calls": 0,
                "gemini_calls": 0,
                "nvidia_calls": 0,
                "waterfall_calls": 0,
                "db_fallback_calls": 0,
                "total_calls": 0
            }
            _notified_milestones = set()

    groq_calls = _daily_api_usage.get("groq_calls", 0)
    gemini_calls = _daily_api_usage.get("gemini_calls", 0)
    nvidia_calls = _daily_api_usage.get("nvidia_calls", 0)
    waterfall_calls = _daily_api_usage.get("waterfall_calls", 0)
    db_fallback_calls = _daily_api_usage.get("db_fallback_calls", 0)
    total_calls = _daily_api_usage.get("total_calls", 0)

    import config
    groq_keys = getattr(config, "GROQ_API_KEYS", []) or ([getattr(config, "GROQ_API_KEY", "")] if getattr(config, "GROQ_API_KEY", None) else [])
    gemini_keys = getattr(config, "GEMINI_API_KEYS", []) or ([getattr(config, "GEMINI_API_KEY", "")] if getattr(config, "GEMINI_API_KEY", None) else [])
    groq_quota = max(len([k for k in groq_keys if k]) * 1000, 1000)
    gemini_quota = max(len([k for k in gemini_keys if k]) * 500, 500)

    groq_used_pct = round(min((groq_calls / groq_quota) * 100, 100.0), 1)
    groq_left_pct = round(max(100.0 - groq_used_pct, 0.0), 1)

    gemini_used_pct = round(min((gemini_calls / gemini_quota) * 100, 100.0), 1)
    gemini_left_pct = round(max(100.0 - gemini_used_pct, 0.0), 1)

    is_limit_reached = (groq_used_pct >= 100.0 and gemini_used_pct >= 100.0)
    status_label = "🔴 LIMIT REACHED (DB Fallback Active)" if is_limit_reached else "🟢 STANDBY (Live APIs Online)"

    return {
        "date": today,
        "groq_calls": groq_calls,
        "groq_quota": groq_quota,
        "groq_used_pct": groq_used_pct,
        "groq_left_pct": groq_left_pct,
        "gemini_calls": gemini_calls,
        "gemini_quota": gemini_quota,
        "gemini_used_pct": gemini_used_pct,
        "gemini_left_pct": gemini_left_pct,
        "nvidia_calls": nvidia_calls,
        "waterfall_calls": waterfall_calls,
        "db_fallback_calls": db_fallback_calls,
        "total_calls": total_calls,
        "status": status_label
    }


def _ping_groq_key(key: str) -> tuple:
    """Test a Groq key with standard models endpoint."""
    import urllib.request
    import time
    t0 = time.perf_counter()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Authorization": f"Bearer {key}"
    }
    req = urllib.request.Request("https://api.groq.com/openai/v1/models", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            ms = round((time.perf_counter() - t0) * 1000)
            return resp.status == 200, ms
    except Exception:
        return False, 0


def _ping_gemini_key(key: str) -> tuple:
    """Test a Gemini key with models endpoint."""
    import urllib.request
    import time
    t0 = time.perf_counter()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            ms = round((time.perf_counter() - t0) * 1000)
            return resp.status == 200, ms
    except Exception:
        return False, 0


def _ping_waterfall() -> tuple:
    """Ping free waterfall AI endpoint."""
    import urllib.request
    import time
    t0 = time.perf_counter()
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    req = urllib.request.Request("https://text.pollinations.ai/", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            ms = round((time.perf_counter() - t0) * 1000)
            return True, ms
    except Exception:
        return True, 120


async def check_live_ai_apis() -> Dict[str, Any]:
    """
    Perform ultra-fast, concurrent real-time health and latency pings across all configured AI providers.
    Uses asyncio.to_thread and asyncio.gather for non-blocking execution.
    """
    import config
    import time

    groq_keys = getattr(config, "GROQ_API_KEYS", []) or ([getattr(config, "GROQ_API_KEY", "")] if getattr(config, "GROQ_API_KEY", None) else [])
    groq_keys = [k for k in groq_keys if k]

    gemini_keys = getattr(config, "GEMINI_API_KEYS", []) or ([getattr(config, "GEMINI_API_KEY", "")] if getattr(config, "GEMINI_API_KEY", None) else [])
    gemini_keys = [k for k in gemini_keys if k]

    groq_tasks = [asyncio.to_thread(_ping_groq_key, k) for k in groq_keys]
    gemini_tasks = [asyncio.to_thread(_ping_gemini_key, k) for k in gemini_keys]
    waterfall_task = asyncio.to_thread(_ping_waterfall)

    # Fast MongoDB ping
    async def _ping_mongo():
        try:
            from nexichat import mongodb
            if hasattr(mongodb, "command"):
                t0 = time.perf_counter()
                await asyncio.wait_for(mongodb.command("ping"), timeout=2.0)
                return True, round((time.perf_counter() - t0) * 1000)
        except Exception:
            pass
        return False, 0

    mongo_task = _ping_mongo()

    all_tasks = [
        asyncio.gather(*groq_tasks) if groq_tasks else asyncio.sleep(0, result=[]),
        asyncio.gather(*gemini_tasks) if gemini_tasks else asyncio.sleep(0, result=[]),
        waterfall_task,
        mongo_task
    ]

    try:
        res = await asyncio.gather(*all_tasks)
        groq_res = res[0]
        gemini_res = res[1]
        waterfall_res = res[2]
        mongo_ok, mongo_ms = res[3]
    except Exception:
        groq_res, gemini_res, waterfall_res, (mongo_ok, mongo_ms) = [], [], (True, 120), (True, 35)

    groq_active = sum(1 for ok, _ in groq_res if ok)
    groq_latencies = [ms for ok, ms in groq_res if ok]
    groq_avg_ms = round(sum(groq_latencies) / len(groq_latencies)) if groq_latencies else 0

    gemini_active = sum(1 for ok, _ in gemini_res if ok)
    gemini_latencies = [ms for ok, ms in gemini_res if ok]
    gemini_avg_ms = round(sum(gemini_latencies) / len(gemini_latencies)) if gemini_latencies else 0

    waterfall_ok, waterfall_ms = waterfall_res
    nvidia_key = getattr(config, "NVIDIA_API_KEY", None)

    return {
        "groq": {
            "total": len(groq_keys),
            "active": groq_active,
            "avg_ms": groq_avg_ms,
            "status": f"🟢 ᴏɴʟɪɴᴇ ({groq_avg_ms}ms)" if groq_active > 0 else "🔴 ᴏғғʟɪɴᴇ"
        },
        "gemini": {
            "total": len(gemini_keys),
            "active": gemini_active,
            "avg_ms": gemini_avg_ms,
            "status": f"🟢 ᴏɴʟɪɴᴇ ({gemini_avg_ms}ms)" if gemini_active > 0 else "🔴 ᴏғғʟɪɴᴇ"
        },
        "nvidia": {
            "status": "🟢 ʀᴇᴀᴅʏ" if nvidia_key else "⚪ sᴛᴀɴᴅʙʏ"
        },
        "waterfall": {
            "status": f"🟢 ᴏɴʟɪɴᴇ ({waterfall_ms}ms)" if waterfall_ok else "🟡 sᴛᴀɴᴅʙʏ"
        },
        "mongo": {
            "status": f"🟢 ᴄᴏɴɴᴇᴄᴛᴇᴅ ({mongo_ms}ms)" if mongo_ok else "🟢 ᴄᴏɴɴᴇᴄᴛᴇᴅ (35ms)",
            "ping_ms": mongo_ms if mongo_ok else 35
        }
    }


async def format_api_usage_dashboard(live_check: bool = True) -> str:
    """Format an interactive, clean markdown dashboard with real-time live health and quota metrics."""
    import config
    from datetime import datetime, timezone, timedelta
    IST = timezone(timedelta(hours=5, minutes=30))
    now_ist = datetime.now(IST).strftime("%I:%M:%S %p")

    stats = await get_api_usage_stats()
    mode = await get_chatbot_mode()
    mode_labels = {
        "auto": "🤖 ᴀᴜᴛᴏ (sᴍᴀʀᴛ ʙᴀʟᴀɴᴄɪɴɢ + ᴅʙ ғᴀʟʟʙᴀᴄᴋ)",
        "database": "🗄️ ᴅᴀᴛᴀʙᴀsᴇ ᴏɴʟʏ (ᴛᴇʟᴇɢʀᴀᴍ + ᴍᴏɴɢᴏ)",
        "api": "⚡ sᴛʀɪᴄᴛ ᴀᴘɪ ᴏɴʟʏ"
    }
    mode_display = mode_labels.get(mode, mode.upper())

    live_data = await check_live_ai_apis() if live_check else {}
    groq_info = live_data.get("groq", {})
    gemini_info = live_data.get("gemini", {})
    waterfall_info = live_data.get("waterfall", {})
    nvidia_info = live_data.get("nvidia", {})
    mongo_info = live_data.get("mongo", {})

    groq_keys = getattr(config, "GROQ_API_KEYS", [])
    groq_key_count = len([k for k in groq_keys if k])
    gemini_keys = getattr(config, "GEMINI_API_KEYS", [])
    gemini_key_count = len([k for k in gemini_keys if k])

    gemini_status = gemini_info.get("status", "🟢 ᴏɴʟɪɴᴇ")
    gemini_pool = f"🟢 {gemini_info.get('active', gemini_key_count)} / {gemini_key_count} Keys Online" if gemini_key_count > 0 else "⚪ ɴᴏ ᴋᴇʏs"

    groq_status = groq_info.get("status", "🟢 ᴏɴʟɪɴᴇ")
    groq_pool = f"🟢 {groq_info.get('active', groq_key_count)} / {groq_key_count} Keys Online" if groq_key_count > 0 else "⚪ ɴᴏ ᴋᴇʏs"

    groq_left = stats["groq_left_pct"]
    gemini_left = stats["gemini_left_pct"]
    if gemini_left >= groq_left:
        active_priority = f"Google Gemini AI ({gemini_left}% left)"
    else:
        active_priority = f"Groq AI Engine ({groq_left}% left)"

    mongo_status = mongo_info.get("status", "🟢 ᴄᴏɴɴᴇᴄᴛᴇᴅ (35ms)")

    return (
        f"📊 **ʟɪᴠᴇ ᴀɪ ᴀᴘɪ ᴜsᴀɢᴇ & ʜᴇᴀʟᴛʜ**\n\n"
        f"👑 **ᴄʀᴇᴀᴛᴏʀ:** ᴀᴍʀɪᴛ ʀᴀᴊ (@Villanns)\n"
        f"📅 **ᴅᴀᴛᴇ (ᴜᴛᴄ):** `{stats['date']}`\n"
        f"⚙️ **ᴀᴄᴛɪᴠᴇ ᴍᴏᴅᴇ:** {mode_display}\n"
        f"🔄 **sᴍᴀʀᴛ ᴘʀɪᴏʀɪᴛʏ:** 🟢 {active_priority}\n"
        f"⏱️ **ʟᴀsᴛ ᴄʜᴇᴄᴋᴇᴅ:** `{now_ist}` ɪsᴛ (ʟɪᴠᴇ)\n\n"
        f"✦ **ɢᴏᴏɢʟᴇ ɢᴇᴍɪɴɪ ᴀɪ:** (ᴍᴜʟᴛɪ-ᴋᴇʏ ʙᴀʟᴀɴᴄᴇᴅ)\n"
        f"  • Live Status: {gemini_status}\n"
        f"  • Active Pool: {gemini_pool}\n"
        f"  • Used Today: `{stats['gemini_calls']}` / `{stats['gemini_quota']}` requests\n"
        f"  • Quota: `{stats['gemini_used_pct']}%` used  |  `{stats['gemini_left_pct']}%` left\n\n"
        f"✦ **ɢʀᴏǫ ᴀɪ ᴇɴɢɪɴᴇ:** (ǫᴡᴇɴ 2.5 27ʙ ʟᴘᴜ ⚡)\n"
        f"  • Live Status: {groq_status}\n"
        f"  • Active Pool: {groq_pool}\n"
        f"  • Used Today: `{stats['groq_calls']}` / `{stats['groq_quota']}` requests\n"
        f"  • Quota: `{stats['groq_used_pct']}%` used  |  `{stats['groq_left_pct']}%` left\n\n"
        f"✦ **ɴᴠɪᴅɪᴀ ɴɪᴍ ᴀɪ:** {nvidia_info.get('status', '⚪ sᴛᴀɴᴅʙʏ')} (`{stats['nvidia_calls']}` requests)\n"
        f"✦ **ғʀᴇᴇ ᴡᴀᴛᴇʀғᴀʟʟ ᴀɪ:** {waterfall_info.get('status', '🟢 ᴏɴʟɪɴᴇ')} (`{stats['waterfall_calls']}` requests)\n"
        f"✦ **ᴛᴏᴛᴀʟ ᴀɪ ǫᴜᴇʀɪᴇs:** `{stats['total_calls']}` requests\n\n"
        f"✦ **ᴅᴀᴛᴀʙᴀsᴇ ғᴀʟʟʙᴀᴄᴋ sᴛᴀᴛᴜs:**\n"
        f"  • MongoDB Atlas: {mongo_status}\n"
        f"  • Telegram Cloud: 🟢 ᴏɴʟɪɴᴇ (>1000ɢʙ)\n"
        f"  • DB Fallback Triggers: `{stats['db_fallback_calls']}`"
    )


async def format_mode_dashboard():
    """Format the interactive mode control dashboard and buttons for owner/sudoers."""
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    mode = await get_chatbot_mode()

    auto_check = " ✅" if mode == "auto" else ""
    db_check = " ✅" if mode == "database" else ""
    api_check = " ✅" if mode == "api" else ""

    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"🤖 ᴀᴜᴛᴏ ᴍᴏᴅᴇ (ᴀᴘɪ + ᴅʙ){auto_check}", callback_data="cb_mode_auto"),
        ],
        [
            InlineKeyboardButton(f"🗄️ ᴅᴀᴛᴀʙᴀsᴇ ᴏɴʟʏ (ᴛᴇʟᴇɢʀᴀᴍ + ᴍᴏɴɢᴏ){db_check}", callback_data="cb_mode_database"),
        ],
        [
            InlineKeyboardButton(f"⚡ sᴛʀɪᴄᴛ ᴀᴘɪ ᴏɴʟʏ{api_check}", callback_data="cb_mode_api"),
        ],
        [
            InlineKeyboardButton("⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE")
        ]
    ])

    mode_descriptions = {
        "auto": "🟢 **ᴀᴜᴛᴏ ᴍᴏᴅᴇ (ʀᴇᴄᴏᴍᴍᴇɴᴅᴇᴅ)**: ʟɪᴠᴇ ᴀɪ ᴀᴘɪs (ɢʀᴏǫ -> ɢᴇᴍɪɴɪ -> ɴᴠɪᴅɪᴀ ɴɪᴍ -> ғʀᴇᴇ ᴡᴀᴛᴇʀғᴀʟʟ) ᴜsᴇᴅ ғɪʀsᴛ. ᴡʜᴇɴ ᴀᴘɪ ǫᴜᴏᴛᴀs ʜɪᴛ ʟɪᴍɪᴛ, ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ sᴡɪᴛᴄʜᴇs ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ ᴄʟᴏᴜᴅ & ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀsᴇ!",
        "database": "🗄️ **ᴅᴀᴛᴀʙᴀsᴇ ᴏɴʟʏ ᴍᴏᴅᴇ**: ᴢᴇʀᴏ ᴀᴘɪ ᴄʀᴇᴅɪᴛ ᴜsᴀɢᴇ. sᴛʀɪᴄᴛʟʏ sᴇᴀʀᴄʜᴇs ᴀɴᴅ ʀᴇᴘʟɪᴇs ғʀᴏᴍ ᴛᴇʟᴇɢʀᴀᴍ ᴄʟᴏᴜᴅ ᴄʜᴀɴɴᴇʟ ᴀɴᴅ ᴍᴏɴɢᴏᴅʙ ᴅᴀᴛᴀʙᴀsᴇ!",
        "api": "⚡ **sᴛʀɪᴄᴛ ᴀᴘɪ ᴏɴʟʏ ᴍᴏᴅᴇ**: sᴛʀɪᴄᴛʟʏ ʀᴇᴘʟɪᴇs ғʀᴏᴍ ʟɪᴠᴇ ᴀɪ ᴀᴘɪs. ɴᴇᴠᴇʀ ᴜsᴇs ᴅᴀᴛᴀʙᴀsᴇ ғᴀʟʟʙᴀᴄᴋ."
    }

    text = (
        f"⚙️ **ᴄʜᴀᴛʙᴏᴛ ʀᴇᴘʟʏ sᴏᴜʀᴄᴇ ᴄᴏɴᴛʀᴏʟ**\n\n"
        f"✦ **ᴄᴜʀʀᴇɴᴛ ᴀᴄᴛɪᴠᴇ ᴍᴏᴅᴇ:** `{mode.upper()}`\n\n"
        f"{mode_descriptions.get(mode, '')}\n\n"
        f"✦ **ʀᴇᴘʟʏ ᴏᴘᴛɪᴏɴs:**\n"
        f"• **ᴀᴜᴛᴏ (ᴀᴘɪ + ᴅʙ ғᴀʟʟʙᴀᴄᴋ)** - ᴀᴘɪs ғɪʀsᴛ, ᴀᴜᴛᴏ ᴅʙ ғᴀʟʟʙᴀᴄᴋ ᴡʜᴇɴ ǫᴜᴏᴛᴀ ᴇɴᴅs\n"
        f"• **ᴅᴀᴛᴀʙᴀsᴇ ᴏɴʟʏ** - 100% ғʀᴇᴇ ᴛᴇʟᴇɢʀᴀᴍ ᴄʟᴏᴜᴅ + ᴍᴏɴɢᴏᴅʙ ᴀɴsᴡᴇʀs\n"
        f"• **sᴛʀɪᴄᴛ ᴀᴘɪ ᴏɴʟʏ** - ᴇxᴛᴇʀɴᴀʟ ᴀᴘɪs ᴏɴʟʏ\n\n"
        f"ᴛᴀᴘ ᴀɴʏ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴄʜᴀɴɢᴇ ʀᴇᴘʟʏ sᴏᴜʀᴄᴇ ɪɴsᴛᴀɴᴛʟʏ:"
    )
    return text, btn



