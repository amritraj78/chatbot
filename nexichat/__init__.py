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
  Ye pooray package (nexichat) ka entry initialization file hai.
  Isme:
  1. Telegram Client (Pyrogram), Logging engine, aur Event loops initialize hote hain.
  2. MongoDB connection setup hota hai; agar MongoDB offline ya missing ho, toh
     fallback In-Memory database activate karta hai taki bot bina crash huye chale.
  3. Sudoers and Clone storage setup hote hain.
================================================================================
"""

import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

import logging
import time
import config

try:
    from Abg import patch
except ImportError:
    pass
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
try:
    import uvloop
    uvloop.install()
except Exception:
    pass

try:
    _loop = asyncio.get_event_loop()
    if _loop.is_closed():
        raise RuntimeError("loop closed")
except RuntimeError:
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)

import gc
from logging.handlers import RotatingFileHandler

# Aggressive garbage collection tuning for 512MB RAM Koyeb container
gc.set_threshold(700, 10, 10)
gc.enable()

SUDOERS = filters.user()
CLONE_OWNERS = {}

# Rotating file handler caps logs to 5MB (max 10MB total on disk forever)
logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=5 * 1024 * 1024, backupCount=2, encoding="utf-8"),
        logging.StreamHandler()
    ],
    level=logging.INFO,
)

logging.getLogger("pyrogram").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)
boot = time.time()

class AwaitableDict(dict):
    def __await__(self):
        async def _coro():
            return self
        return _coro().__await__()

class AwaitableNone:
    def __await__(self):
        async def _coro():
            return None
        return _coro().__await__()
    def __bool__(self):
        return False

class AwaitableResult:
    def __init__(self, val=True):
        self.val = val
    def __await__(self):
        async def _coro():
            return self.val
        return _coro().__await__()

class InMemoryCursor:
    def __init__(self, data):
        self._data = list(data)
    def __aiter__(self):
        self._iter = iter(self._data)
        return self
    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration
    async def to_list(self, length=None):
        return list(self._data)
    def __iter__(self):
        return iter(self._data)

class InMemoryCollection:
    def __init__(self):
        self._data = []

    def _matches(self, doc, filt):
        for k, v in filt.items():
            if isinstance(v, dict):
                val = doc.get(k, 0)
                if "$gt" in v and not (val > v["$gt"]):
                    return False
                if "$lt" in v and not (val < v["$lt"]):
                    return False
            elif doc.get(k) != v:
                return False
        return True

    def find_one(self, filt=None):
        filt = filt or {}
        for d in self._data:
            if self._matches(d, filt):
                return AwaitableDict(d)
        return AwaitableNone()

    def find(self, filt=None):
        filt = filt or {}
        matched = [d for d in self._data if self._matches(d, filt)]
        return InMemoryCursor(matched)

    async def insert_one(self, doc):
        self._data.append(dict(doc))
        return AwaitableResult(True)

    async def update_one(self, filt, update, upsert=False):
        set_vals = update.get("$set", {})
        found = False
        for d in self._data:
            if self._matches(d, filt):
                d.update(set_vals)
                found = True
                break
        if not found and upsert:
            new_doc = dict(filt)
            new_doc.update(set_vals)
            self._data.append(new_doc)
        return AwaitableResult(True)

    async def delete_one(self, filt):
        for i, d in enumerate(self._data):
            if self._matches(d, filt):
                self._data.pop(i)
                break
        return AwaitableResult(True)

    async def delete_many(self, filt=None):
        filt = filt or {}
        if not filt:
            self._data.clear()
        else:
            self._data = [d for d in self._data if not self._matches(d, filt)]
        return AwaitableResult(True)

class InMemoryDatabase:
    def __init__(self):
        self._cols = {}

    def __getattr__(self, name):
        if name not in self._cols:
            self._cols[name] = InMemoryCollection()
        return self._cols[name]

    def __getitem__(self, name):
        return getattr(self, name)

import os
import sys

if config.MONGO_URL and "unittest" not in sys.modules and not os.getenv("TESTING"):
    try:
        try:
            import dns.resolver
            if not os.path.exists("/etc/resolv.conf"):
                r = dns.resolver.Resolver(configure=False)
                r.nameservers = ["8.8.8.8", "1.1.1.1"]
                dns.resolver.default_resolver = r
                dns.resolver.reset_default_resolver = lambda: None
                dns.resolver.get_default_resolver = lambda: r
        except Exception:
            pass

        from pymongo import MongoClient
        from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
        _mongo_async = MongoCli(config.MONGO_URL)
        db = _mongo_async.Anonymous
        mongo = MongoClient(config.MONGO_URL)
        mongodb = mongo.VIP
        LOGGER.info("Connected to MongoDB Atlas.")
    except Exception as e:
        LOGGER.warning(f"MongoDB connection failed: {e}. Falling back to in-memory store.")
        db = InMemoryDatabase()
        mongodb = InMemoryDatabase()
        mongo = mongodb
else:
    LOGGER.info("No MONGO_URL provided. Running with In-Memory database.")
    db = InMemoryDatabase()
    mongodb = InMemoryDatabase()
    mongo = mongodb

OWNER = config.OWNER_ID
_boot_ = time.time()

def sudo():
    global SUDOERS
    OWNER = config.OWNER_ID
    SUDOERS.add(OWNER)
    try:
        sudoersdb = mongodb.sudoers
        res = sudoersdb.find_one({"sudo": "sudo"})
        sudoers = res.get("sudoers", []) if isinstance(res, dict) else []
        if OWNER not in sudoers:
            sudoers.append(OWNER)
            upd = sudoersdb.update_one(
                {"sudo": "sudo"},
                {"$set": {"sudoers": sudoers}},
                upsert=True,
            )
            # If async coroutine is returned by in-memory mock, schedule or ignore in sync init
            if asyncio.iscoroutine(upd):
                try:
                    asyncio.get_event_loop().create_task(upd)
                except Exception:
                    pass
        for x in sudoers:
            SUDOERS.add(x)
        print(f"Sudoers Loaded ({len(SUDOERS)} members).")
    except Exception as e:
        print(f"Sudoers loaded (Owner only: {e})")

cloneownerdb = db.clone_owners

async def load_clone_owners():
    try:
        async for entry in cloneownerdb.find():
            bot_id = entry["bot_id"]
            user_id = entry["user_id"]
            CLONE_OWNERS[bot_id] = user_id
    except Exception as e:
        LOGGER.warning(f"Failed to load clone owners: {e}")

async def save_clonebot_owner(bot_id, user_id):
    await cloneownerdb.update_one(
        {"bot_id": bot_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )
async def get_clone_owner(bot_id):
    data = await cloneownerdb.find_one({"bot_id": bot_id})
    if data:
        return data["user_id"]
    return None

async def delete_clone_owner(bot_id):
    await cloneownerdb.delete_one({"bot_id": bot_id})
    CLONE_OWNERS.pop(bot_id, None)

async def save_idclonebot_owner(clone_id, user_id):
    await cloneownerdb.update_one(
        {"clone_id": clone_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

async def get_idclone_owner(clone_id):
    data = await cloneownerdb.find_one({"clone_id": clone_id})
    if data:
        return data["user_id"]
    return None

    
class nexichat(Client):
    def __init__(self):
        try:
            _loop = asyncio.get_event_loop()
            if _loop.is_closed():
                raise RuntimeError("loop closed")
        except RuntimeError:
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
        super().__init__(
            name="nexichat",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.DEFAULT,
            workers=8,
            sleep_threshold=60,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention
        
    async def stop(self):
        await super().stop()

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time
    
sudo()
nexichat = nexichat()
