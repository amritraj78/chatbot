import time
import logging
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

from config import OWNER_ID, SUPPORT_GRP, INSTAGRAM, SNAPCHAT, OWNER_USERNAME
from nexichat import _boot_, get_readable_time, SUDOERS
from nexichat.database.chats import get_served_chats
from nexichat.database.users import get_served_users
from nexichat.database.chatbot import get_user_nickname

logger = logging.getLogger(__name__)


@Client.on_message(filters.command("stats"))
async def stats(cli: Client, message: Message):
    bot_id = (await cli.get_me()).id
    users = len(await get_served_users(bot_id))
    chats = len(await get_served_chats(bot_id))
    
    api_info = ""
    user_id = message.from_user.id if message.from_user else 0
    if user_id in SUDOERS or user_id == int(OWNER_ID):
        try:
            from nexichat.database.chatbot import get_api_usage_stats
            st = await get_api_usage_stats()
            api_info = (
                f"\n\n📊 **ᴠɪᴘ ᴀɪ ᴀᴘɪ ᴜsᴀɢᴇ**\n"
                f"• **ɢʀᴏǫ ᴀɪ:** `{st['groq_calls']}`/`{st['groq_quota']}` ({st['groq_used_pct']}% ᴜsᴇᴅ | {st['groq_left_pct']}% ʟᴇғᴛ)\n"
                f"• **ɢᴇᴍɪɴɪ ᴀɪ:** `{st['gemini_calls']}`/`{st['gemini_quota']}` ({st['gemini_used_pct']}% ᴜsᴇᴅ | {st['gemini_left_pct']}% ʟᴇғᴛ)\n"
                f"• **ᴛᴏᴛᴀʟ ǫᴜᴇʀɪᴇs:** `{st['total_calls']}` | **ᴅʙ ғᴀʟʟʙᴀᴄᴋ:** `{st['db_fallback_calls']}`"
            )
        except Exception:
            pass

    bot_obj = await cli.get_me()
    await message.reply_text(
        f"📊 **{bot_obj.first_name or 'VIP REACTION'} sᴛᴀᴛs**\n\n"
        f"• **ᴄʜᴀᴛs:** `{chats}`\n"
        f"• **ᴜsᴇʀs:** `{users}`{api_info}"
    )


@Client.on_message(filters.command("id"))
async def getid(client: Client, message: Message):
    chat = message.chat
    your_id = message.from_user.id if message.from_user else 0
    message_id = message.id
    reply = message.reply_to_message

    text = f"**[ᴍᴇssᴀɢᴇ ɪᴅ:]({message.link})** `{message_id}`\n"
    text += f"**[ʏᴏᴜʀ ɪᴅ:](tg://user?id={your_id})** `{your_id}`\n"

    if not getattr(message, "command", None):
        message.command = (getattr(message, "text", "") or "").split()

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"**[ᴜsᴇʀ ɪᴅ:](tg://user?id={user_id})** `{user_id}`\n"
        except Exception:
            return await message.reply_text("ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ.", quote=True)

    chat_username = getattr(chat, "username", None)
    if chat_username:
        text += f"**[ᴄʜᴀᴛ ɪᴅ:](https://t.me/{chat_username})** `{chat.id}`\n\n"
    else:
        text += f"**ᴄʜᴀᴛ ɪᴅ :** `{chat.id}`\n\n"

    if (
        not getattr(reply, "empty", True)
        and not message.forward_from_chat
        and not reply.sender_chat
        and reply.from_user
    ):
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ:]({reply.link})** `{reply.id}`\n"
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ:](tg://user?id={reply.from_user.id})** `{reply.from_user.id}`\n\n"

    if reply and reply.forward_from:
        text += f"ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴜsᴇʀ, {reply.forward_from.first_name}, ʜᴀs ᴀɴ ɪᴅ ᴏғ `{reply.forward_from.id}`\n\n"

    if reply and reply.forward_from_chat:
        text += f"ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, {reply.forward_from_chat.title}, ʜᴀs ᴀɴ ɪᴅ ᴏғ `{reply.forward_from_chat.id}`\n\n"

    if reply and reply.sender_chat:
        text += f"ɪᴅ ᴏғ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ, ɪs `{reply.sender_chat.id}`"

    await message.reply_text(
        text,
        disable_web_page_preview=True,
    )


@Client.on_message(filters.command(["profile", "me", "myinfo"]))
async def user_profile(client: Client, message: Message):
    user = message.from_user
    if not user:
        return
    
    uptime = get_readable_time(time.time() - _boot_)
    is_owner = (user.id == int(OWNER_ID))
    role = "👑 ᴏᴡɴᴇʀ / ʙᴏss" if is_owner else "💎 ᴠɪᴘ ᴍᴇᴍʙᴇʀ"
    
    nickname = await get_user_nickname(user.id)
    nick_str = f"• **ɴɪᴄᴋɴᴀᴍᴇ:** `{nickname}`\n" if nickname else ""
    
    text = f"""👑 **ᴜsᴇʀ ᴠɪᴘ ᴘʀᴏғɪʟᴇ**
ᴠ2.0

🌸 **ʜᴇʏ {user.mention}!**
ʏᴏᴜʀ ᴏғғɪᴄɪᴀʟ ᴠɪᴘ ᴘʀᴏғɪʟᴇ ᴄᴀʀᴅ:

• **ɴᴀᴍᴇ:** {user.first_name}
• **ᴜsᴇʀ ɪᴅ:** `{user.id}`
• **ᴜsᴇʀɴᴀᴍᴇ:** @{user.username if user.username else 'None'}
{nick_str}• **sᴛᴀᴛᴜs:** {role}
• **ᴅᴄ ɪᴅ:** `{user.dc_id or 'Unknown'}`
• **ʙᴏᴛ ᴜᴘᴛɪᴍᴇ:** `{uptime}`

👑 **ᴄʀᴇᴀᴛᴏʀ:** [ᴀᴍʀɪᴛ ʀᴀᴊ](https://t.me/Villanns) 💖"""
    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📷 ɪɴsᴛᴀɢʀᴀᴍ", url=f"https://instagram.com/{INSTAGRAM}"),
            InlineKeyboardButton("👻 sɴᴀᴘᴄʜᴀᴛ", url=f"https://snapchat.com/add/{SNAPCHAT}"),
        ],
        [
            InlineKeyboardButton("👑 ᴄʀᴇᴀᴛᴏʀ", url=f"https://t.me/{OWNER_USERNAME}"),
            InlineKeyboardButton("⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE"),
        ]
    ])
    await message.reply_text(text, reply_markup=btn, disable_web_page_preview=True)
