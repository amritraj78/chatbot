import time
import logging
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions

from config import OWNER_ID, SUPPORT_GRP
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
                f"\n\n📊 **VIP AI API USAGE**\n"
                f"────────────────────────────\n"
                f"✦ **Groq AI:** `{st['groq_calls']}`/`{st['groq_quota']}` ({st['groq_used_pct']}% used | {st['groq_left_pct']}% left)\n"
                f"✦ **Gemini AI:** `{st['gemini_calls']}`/`{st['gemini_quota']}` ({st['gemini_used_pct']}% used | {st['gemini_left_pct']}% left)\n"
                f"✦ **Total Queries:** `{st['total_calls']}` | **DB Fallback:** `{st['db_fallback_calls']}`\n"
                f"────────────────────────────"
            )
        except Exception:
            pass

    await message.reply_text(
        f"""{(await cli.get_me()).mention} Reaction Bot Stats:

➻ **Chats:** {chats}
➻ **Users:** {users}{api_info}"""
    )


@Client.on_message(filters.command("id"))
async def getid(client: Client, message: Message):
    chat = message.chat
    your_id = message.from_user.id if message.from_user else 0
    message_id = message.id
    reply = message.reply_to_message

    text = f"**[Message ID:]({message.link})** `{message_id}`\n"
    text += f"**[Your ID:](tg://user?id={your_id})** `{your_id}`\n"

    if not getattr(message, "command", None):
        message.command = (getattr(message, "text", "") or "").split()

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"**[User ID:](tg://user?id={user_id})** `{user_id}`\n"
        except Exception:
            return await message.reply_text("This user doesn't exist.", quote=True)

    chat_username = getattr(chat, "username", None)
    if chat_username:
        text += f"**[Chat ID:](https://t.me/{chat_username})** `{chat.id}`\n\n"
    else:
        text += f"**Chat ID:** `{chat.id}`\n\n"

    if (
        not getattr(reply, "empty", True)
        and not message.forward_from_chat
        and not reply.sender_chat
    ):
        text += f"**[Replied Message ID:]({reply.link})** `{reply.id}`\n"
        text += f"**[Replied User ID:](tg://user?id={reply.from_user.id})** `{reply.from_user.id}`\n\n"

    if reply and reply.forward_from:
        text += f"The forwarded user, {reply.forward_from.first_name}, has an ID of `{reply.forward_from.id}`\n\n"

    if reply and reply.forward_from_chat:
        text += f"The forwarded channel, {reply.forward_from_chat.title}, has an ID of `{reply.forward_from_chat.id}`\n\n"

    if reply and reply.sender_chat:
        text += f"ID of the replied chat/channel is `{reply.sender_chat.id}`"

    await message.reply_text(
        text,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        parse_mode=ParseMode.DEFAULT,
    )


@Client.on_message(filters.command(["profile", "me", "myinfo"]))
async def user_profile(client: Client, message: Message):
    user = message.from_user
    if not user:
        return
    
    uptime = get_readable_time(time.time() - _boot_)
    is_owner = (user.id == int(OWNER_ID))
    role = "👑 Owner / Boss" if is_owner else "💎 VIP Member"
    
    nickname = await get_user_nickname(user.id)
    nick_str = f"• **Nickname:** `{nickname}`\n" if nickname else ""
    
    text = f"""╭────────────────────────────╮
│    👑 USER VIP PROFILE 👑  │
╰────────────────────────────╯
🌸 **Hello {user.mention}!**
Here is your official VIP profile card.

╭────────────────────────────╮
│ • **Name:** {user.first_name}
│ • **User ID:** `{user.id}`
│ • **Username:** @{user.username if user.username else 'None'}
│ {nick_str}• **Status:** {role}
│ • **DC ID:** `{user.dc_id or 'Unknown'}`
│ • **Bot Uptime:** `{uptime}`
╰────────────────────────────╯
📡 **Powered by:** [Amrit Feel](https://t.me/{SUPPORT_GRP}) 💞"""
    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📷 Instagram", url="https://instagram.com/ex_amrit"),
            InlineKeyboardButton("👻 Snapchat", url="https://snapchat.com/add/ex_amrit"),
        ],
        [
            InlineKeyboardButton("👑 Creator", url="https://t.me/Villanns"),
            InlineKeyboardButton("⦿ Close ⦿", callback_data="CLOSE"),
        ]
    ])
    await message.reply_text(text, reply_markup=btn, link_preview_options=LinkPreviewOptions(is_disabled=True))
