from pyrogram import Client
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import OWNER_ID
from nexichat import SUDOERS
from nexichat.database.chatbot import (
    set_chatbot_enabled,
    is_chatbot_enabled,
    set_db_fallback_enabled,
    is_db_fallback_enabled,
    set_chatbot_mode,
    get_chatbot_mode,
    format_mode_dashboard,
    format_api_usage_dashboard,
)
from nexichat.mplugin.helpers import (
    ABOUT_BTN,
    ABOUT_READ,
    ADMIN_READ,
    CHATBOT_BACK,
    CHATBOT_READ,
    AI_CHATBOT_READ,
    DEV_OP,
    HELP_BTN,
    HELP_READ,
    HELP_GAMES_READ,
    HELP_GROUP_READ,
    TOOLS_DATA_READ,
)


async def _safe_edit(query: CallbackQuery, text: str, reply_markup: InlineKeyboardMarkup = None):
    """Safely edits the message using disable_web_page_preview and avoids unhandled errors."""
    try:
        await query.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )
    except Exception as e:
        if "MESSAGE_NOT_MODIFIED" in str(e).upper():
            return
        try:
            await query.message.reply_text(
                text=text,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
        except Exception:
            pass


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data
    try:
        await query.answer()
    except Exception:
        pass

    if data == "HELP":
        await _safe_edit(query, text=HELP_READ, reply_markup=InlineKeyboardMarkup(HELP_BTN))
    elif data == "CLOSE":
        try:
            await query.message.delete()
        except Exception:
            pass
    elif data in ["BACK", "SBACK"]:
        first_name = query.from_user.first_name if query.from_user else "Friend"
        back_text = (
            f"🌸 **ᴀɴsʜɪᴋᴀ ᴀɪ ᴄʜᴀᴛʙᴏᴛ**\n"
            f"ᴠ2.0\n\n"
            f"ʜᴇʏ {first_name} 👋\n\n"
            f"ɪ ᴀᴍ ᴀɴsʜɪᴋᴀ, ᴀ ʜɪɢʜ-ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ ᴀɪ ᴄʜᴀᴛʙᴏᴛ ᴅᴇsɪɢɴᴇᴅ ᴛᴏ ᴄʜᴀᴛ, ʀᴇᴀᴄᴛ ᴀɴᴅ ᴇɴᴛᴇʀᴛᴀɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘs:\n\n"
            f"• 🌸 **sᴡᴇᴇᴛ ɪɴᴅɪᴀɴ ɢɪʀʟ ᴄʜᴀᴛ** (ᴛᴇxᴛ, sᴛɪᴄᴋᴇʀs, ᴍᴇᴅɪᴀ)\n"
            f"• ⚡ **ᴀᴜᴛᴏ-ʀᴇᴀᴄᴛɪᴏɴs** (ɢʀᴏᴜᴘs & ᴄʜᴀɴɴᴇʟs)\n"
            f"• 🧠 **ᴘᴇʀsɪsᴛᴇɴᴛ ᴅᴍ ᴍᴇᴍᴏʀʏ ʀᴇᴄᴀʟʟ**\n"
            f"• 🎮 **ғᴜɴ ɢᴀᴍᴇs, ʟᴏᴠᴇ ᴛᴇsᴛs & sʜᴀʏᴀʀɪs**\n"
            f"• 👑 **ᴄʀᴇᴀᴛᴏʀ:** [ᴀᴍʀɪᴛ ʀᴀᴊ](https://t.me/Villanns)\n\n"
            f"ᴊᴜsᴛ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ɢʀᴀɴᴛ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs!"
        )
        await _safe_edit(query, text=back_text, reply_markup=InlineKeyboardMarkup(DEV_OP))
    elif data == "ABOUT":
        await _safe_edit(query, text=ABOUT_READ, reply_markup=InlineKeyboardMarkup(ABOUT_BTN))
    elif data == "ADMINS":
        await _safe_edit(query, text=ADMIN_READ, reply_markup=InlineKeyboardMarkup(CHATBOT_BACK))
    elif data == "HELP_GAMES":
        await _safe_edit(query, text=HELP_GAMES_READ, reply_markup=InlineKeyboardMarkup(CHATBOT_BACK))
    elif data == "HELP_GROUP":
        await _safe_edit(query, text=HELP_GROUP_READ, reply_markup=InlineKeyboardMarkup(CHATBOT_BACK))
    elif data == "TOOLS_DATA":
        await _safe_edit(query, text=TOOLS_DATA_READ, reply_markup=InlineKeyboardMarkup(CHATBOT_BACK))
    elif data == "BACK_HELP" or data == "CHATBOT_BACK":
        await _safe_edit(query, text=HELP_READ, reply_markup=InlineKeyboardMarkup(HELP_BTN))
    elif data == "CHATBOT_CMD":
        await _safe_edit(query, text=CHATBOT_READ, reply_markup=InlineKeyboardMarkup(CHATBOT_BACK))
    elif data == "AI_CHATBOT_CMD":
        await _safe_edit(query, text=AI_CHATBOT_READ, reply_markup=InlineKeyboardMarkup(CHATBOT_BACK))
    elif data in ["cb_enable_chatbot", "cb_disable_chatbot"]:
        chat_id = query.message.chat.id
        if query.message.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            try:
                member = await client.get_chat_member(chat_id, query.from_user.id)
                if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] and query.from_user.id not in SUDOERS and query.from_user.id != int(OWNER_ID):
                    return await query.answer("❌ Only admins can toggle chatbot settings!", show_alert=True)
            except Exception:
                return await query.answer("❌ Admin verification failed.", show_alert=True)

        is_en = (data == "cb_enable_chatbot")
        await set_chatbot_enabled(chat_id, is_en)
        await query.answer("Chatbot enabled! 🌸" if is_en else "Chatbot disabled! 😴", show_alert=False)

        status_icon = "🟢 **ᴇɴᴀʙʟᴇᴅ**" if is_en else "🔴 **ᴅɪsᴀʙʟᴇᴅ**"
        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🟢 ᴇɴᴀʙʟᴇ", callback_data="cb_enable_chatbot"),
                InlineKeyboardButton("🔴 ᴅɪsᴀʙʟᴇ", callback_data="cb_disable_chatbot"),
            ],
            [
                InlineKeyboardButton("⦿ ᴄʟᴏsᴇ ⦿", callback_data="CLOSE")
            ]
        ])
        text = (
            f"🤖 **ᴀɪ ᴄʜᴀᴛʙᴏᴛ sᴇᴛᴛɪɴɢs**\n\n"
            f"✦ **ᴄʜᴀᴛ:** {query.message.chat.title or query.message.chat.first_name or 'This Chat'}\n"
            f"✦ **sᴛᴀᴛᴜs:** {status_icon}\n"
            f"✦ **ᴘᴇʀsᴏɴᴀ:** sᴡᴇᴇᴛ ɪɴᴅɪᴀɴ ɢɪʀʟ (ᴀɴsʜɪᴋᴀ) 🌸\n\n"
            f"ᴡʜᴇɴ ᴇɴᴀʙʟᴇᴅ, ɪ ᴡɪʟʟ ʀᴇᴘʟʏ ᴛᴏ ᴍᴇssᴀɢᴇs, ǫᴜᴇsᴛɪᴏɴs, sᴛɪᴄᴋᴇʀs ᴀɴᴅ ᴍᴇᴅɪᴀ!\n\n"
            f"**ǫᴜɪᴄᴋ ᴄᴏᴍᴍᴀɴᴅs:**\n"
            f"• `/chatbot on` - ᴛᴜʀɴ ᴄʜᴀᴛʙᴏᴛ ᴏɴ\n"
            f"• `/chatbot off` - ᴛᴜʀɴ ᴄʜᴀᴛʙᴏᴛ ᴏғғ\n"
            f"• `/ask <query>` - ᴀsᴋ ᴀɴʏ ᴀɪ ǫᴜᴇsᴛɪᴏɴ\n"
            f"• `/love <name1> <name2>` - ʟᴏᴠᴇ ᴄᴀʟᴄᴜʟᴀᴛᴏʀ\n"
            f"• `/shayri` - ᴘᴏᴇᴛɪᴄ sʜᴀʏᴀʀɪs\n"
            f"• `/joke` - ғᴜɴɴʏ ᴊᴏᴋᴇs"
        )
        try:
            await query.message.edit_text(text, reply_markup=btn)
        except Exception:
            pass

    elif data in ["cb_mode_auto", "cb_mode_database", "cb_mode_api"]:
        user_id = query.from_user.id
        if user_id not in SUDOERS and user_id != int(OWNER_ID):
            return await query.answer("❌ Only Creator/Sudoers can change reply mode!", show_alert=True)

        mode_map = {
            "cb_mode_auto": "auto",
            "cb_mode_database": "database",
            "cb_mode_api": "api"
        }
        target_mode = mode_map[data]
        await set_chatbot_mode(target_mode)
        await query.answer(f"✅ Switched to {target_mode.upper()} mode!", show_alert=True)

        text, btn = await format_mode_dashboard()
        try:
            await query.message.edit_text(text, reply_markup=btn)
        except Exception:
            pass

    elif data in ["cb_dbmode_enable", "cb_dbmode_disable"]:
        user_id = query.from_user.id
        if user_id not in SUDOERS and user_id != int(OWNER_ID):
            return await query.answer("❌ Only Creator/Sudoers can change this!", show_alert=True)

        is_en = (data == "cb_dbmode_enable")
        await set_chatbot_mode("auto" if is_en else "api")
        await query.answer("✅ Database fallback mode ENABLED!" if is_en else "🛑 Strict API-only mode ENABLED!", show_alert=True)

        text, btn = await format_mode_dashboard()
        try:
            await query.message.edit_text(text, reply_markup=btn)
        except Exception:
            pass

    elif data == "cb_refresh_api_usage":
        user_id = query.from_user.id
        if user_id not in SUDOERS and user_id != int(OWNER_ID):
            return await query.answer("❌ Only Creator/Sudoers can view this dashboard!", show_alert=True)
        dashboard_text = await format_api_usage_dashboard()
        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Refresh Dashboard", callback_data="cb_refresh_api_usage"),
                InlineKeyboardButton("⦿ Close ⦿", callback_data="CLOSE")
            ]
        ])
        try:
            await query.message.edit_text(dashboard_text, reply_markup=btn)
            await query.answer("✅ API Quota Dashboard refreshed!", show_alert=False)
        except Exception:
            await query.answer("✅ Dashboard is up to date!")

    elif data == "soon":
        await query.answer("🚀 This feature is coming soon in the next update! Stay tuned! 🌸", show_alert=True)
    else:
        query.continue_propagation()
