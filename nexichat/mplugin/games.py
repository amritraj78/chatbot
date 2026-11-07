# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT (Cloned Bot Plugin)
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
#  Licensed under Proprietary Terms. Unauthorized copying is strictly prohibited.
# ---------------------------------------------------------------------------------
"""
================================================================================
  FILE EXPLANATION & HINTS (Cloned Plugin Games)
================================================================================
Is file ka kya kaam hai?
  Ye file Cloned Bots ke liye Games & Fun Commands (/truth, /dare, /flirt, /roast,
  /toss, /roll, /quote) provide karti hai.
================================================================================
"""

import random
import asyncio
import logging
import hashlib
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import ChatAction, ChatType
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logger = logging.getLogger(__name__)

TRUTHS = [
    "Aapka sabse bada secret kya hai jo aapne aaj tak kisi ko nahi bataya? 🤫",
    "Agar aapko kisi ek person ke sath poori zindagi bitani ho, toh wo kaun hoga? 💖",
    "Aapne life me sabse badi galti kya ki hai jiska aapko aaj bhi afsos hai? 🥺",
    "Aapka sabse ajeeb sapna (weirdest dream) kya raha hai? 🙈",
    "Kya aapne kabhi kisi par crush kiya hai jise aap bata nahi paye? Kaun tha wo? 🥰",
    "Agar aapko invisible hone ki power mil jaye, toh aap sabse pehle kya karoge? 👻",
    "Aapne aakhiri baar jhooth kab aur kyu bola tha? 🤥",
    "Aapke phone me sabse embarrassing photo kaun si hai? 📸",
]

DARES = [
    "Group me kisi bhi ek member ko tag karke bolo: 'Main tumhare bina nahi jee sakta!' 🙈",
    "Apne status par likho: 'I am getting married tomorrow!' aur 5 minute baad delete karna! 🤣",
    "Group ke owner ko ek sweet shayari likhkar bhejo! 🌺",
    "Apni voice me ek gaana gaa kar group me voice note bhejo! 🎤",
    "Apni gallery ki 5th photo bina dekhe group me share karo! 📸",
    "Group me kisi ko propose karo pure filmi style me! 💍",
    "Agli 3 baatein sirf shuddh Hindi me bolna hoga! 📜",
]

FLIRTS = [
    "Aapki smile itni pyari hai na, ki Google bhi fail ho jaye aap jaisa dhoondhne me! 🥰🌸",
    "Kya aapka naam Wi-Fi hai? Kyunki jaise hi aap paas aate ho, connection strong ho jata hai! 📶💖",
    "Aapko dekh kar lagta hai ki khuda ne badi fursat me banaya hai aapko! ✨🙈",
    "Doctors kehte hain dil 1 minute me 72 baar dhadakta hai, par mera dil aapko dekh kar double speed me chalta hai! 💓",
    "Aapke aage toh chaand bhi feeka lagta hai ji! 🌙💖",
]

ROASTS = [
    "Aapka dimaag itna fresh hai ji, kyunki aapne lagta hai use hi nahi kiya kabhi! 😂",
    "Agar overthinking ek sport hota, toh aapko Olympic me Gold Medal mil chuka hota! 🥇🤣",
    "Aapki baatein sunke lagta hai ki Google ko bhi ek baar refresh karne ki zaroorat pad jayegi! 🤐",
    "Aap single nahi ho ji, aap toh reserved ho... aane wale saalon ke shock ke liye! 🙈😂",
    "Aap itne unique ho na, ki aap jaisa doosra mil jaye toh duniya handle nahi kar payegi! 😜",
]

QUOTES = [
    "🌟 *\"Koshish karne walon ki kabhi haar nahi hoti!\"* - Harivansh Rai Bachchan",
    "✨ *\"Zindagi lambi nahi, badi honi chahiye babumoshai!\"* - Anand",
    "🚀 *\"Sapne wo nahi jo hum sote huye dekhte hain, sapne wo hain jo humein sone nahi dete!\"* - Dr. A.P.J. Abdul Kalam",
    "🌸 *\"Har din ek naya mauka hai apni kahani ko behtar banane ka!\"*",
]


@Client.on_message(filters.command(["truth"]))
async def truth_command(client: Client, message: Message):
    """Get a random truth question."""
    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass
    truth = random.choice(TRUTHS)
    await message.reply_text(
        f"╭━━━━━━━〔 🤫 **TRUTH CHALLENGE** 〕━━━━━━━╮\n\n"
        f"  ✦ **sᴀᴡᴀʟ :** {truth}\n\n"
        f"  *Sach sach batana padega haan ji! Jhooth nahi chalega!* 🙈\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )


@Client.on_message(filters.command(["dare"]))
async def dare_command(client: Client, message: Message):
    """Get a random dare challenge."""
    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass
    dare = random.choice(DARES)
    await message.reply_text(
        f"╭━━━━━━━〔 🎯 **DARE CHALLENGE** 〕━━━━━━━╮\n\n"
        f"  ✦ **ᴄʜᴀʟʟᴇɴɢᴇ :** {dare}\n\n"
        f"  *Darr ke bhaagna mana hai! Himmat hai toh pura karo!* 🔥\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )


@Client.on_message(filters.command(["flirt"]))
async def flirt_command(client: Client, message: Message):
    """Get a sweet flirt line."""
    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass
    flirt = random.choice(FLIRTS)
    await message.reply_text(
        f"╭━━━━━━━〔 💖 **SWEET FLIRT** 〕━━━━━━━╮\n\n"
        f"  {flirt}\n\n"
        f"  *Hehe sharmana mat haan ji!* 🙈🌸\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )


@Client.on_message(filters.command(["roast"]))
async def roast_command(client: Client, message: Message):
    """Get a playful, friendly roast."""
    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass
    target = message.reply_to_message.from_user.first_name if (message.reply_to_message and message.reply_to_message.from_user) else (message.from_user.first_name if message.from_user else "Dost")
    roast = random.choice(ROASTS)
    await message.reply_text(
        f"╭━━━━━━━〔 🔥 **FRIENDLY ROAST** 〕━━━━━━━╮\n\n"
        f"  Arey {target}! 😂\n"
        f"  {roast}\n\n"
        f"  *Dil par mat lena ji, sirf mazak tha!* 😜✨\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )


@Client.on_message(filters.command(["toss", "coin"]))
async def toss_command(client: Client, message: Message):
    """Flip a coin (Heads or Tails)."""
    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass
    msg = await message.reply_text("🪙 **sɪᴋᴋᴀ ʜᴀᴡᴀ ᴍᴇɪɴ ʜᴀɪ...** 🌪️")
    await asyncio.sleep(0.8)
    outcome = random.choice(["HEADS (चित)", "TAILS (पट)"])
    await msg.edit_text(f"🪙 **Toss Result:** `{outcome}`! 🎉")


@Client.on_message(filters.command(["roll", "dice", "dart", "basket", "football", "slot", "bowling"], prefixes=["/", "!", ".", ""]) | filters.dice)
async def interactive_dice_match(client: Client, message: Message):
    """
    Interactive Dice & Sports Minigame for Clone Bots:
    - Supports /dice, /roll, /dart, /basket, /football, /slot, /bowling
    - Supports direct Telegram animated emoji (🎲, 🎯, 🏀, ⚽, 🎰, 🎳)
    - Bot rolls back and plays against the user!
    """
    chat_id = message.chat.id
    user_name = message.from_user.first_name if message.from_user else "Dost"
    
    emoji = "🎲"
    if message.dice:
        emoji = message.dice.emoji or "🎲"
    elif message.command:
        cmd = message.command[0].lower()
        if "dart" in cmd:
            emoji = "🎯"
        elif "basket" in cmd:
            emoji = "🏀"
        elif "foot" in cmd:
            emoji = "⚽"
        elif "slot" in cmd:
            emoji = "🎰"
        elif "bowl" in cmd:
            emoji = "🎳"
        else:
            emoji = "🎲"

    try:
        user_val = message.dice.value if message.dice else None
        
        if user_val is None:
            user_dice_msg = await message.reply_dice(emoji=emoji)
            await asyncio.sleep(2.0)
            user_val = user_dice_msg.dice.value if user_dice_msg.dice else random.randint(1, 6)
        
        await asyncio.sleep(0.8)
        status = await message.reply_text(f"🌸 **Meri baari! Dekhte hain mera kya aata hai...** {emoji}✨")
        await asyncio.sleep(1.0)
        
        bot_dice_msg = await client.send_dice(chat_id, emoji=emoji)
        await asyncio.sleep(2.2)
        bot_val = bot_dice_msg.dice.value if bot_dice_msg.dice else random.randint(1, 6)
        
        if user_val > bot_val:
            verdict = f"🎉 **Waah {user_name}! Aap jeet gaye!** 💖\nMera luck thoda kharab tha aaj, hehe! 🙈"
        elif bot_val > user_val:
            verdict = f"👑 **Yayyy! Main jeet gayi {user_name}!** 💃✨\nEk aur match khelein? Try again! 🌸"
        else:
            verdict = f"🤝 **Arre waah! Hum dono ka tie ho gaya!** 🌟\nRab ne bana di jodi, score barabar! 🥰"

        await status.edit_text(
            f"╭━━━━━━━〔 {emoji} **MATCH RESULT** 〕━━━━━━━╮\n\n"
            f"  👤 **{user_name} :** `{user_val}` {emoji}\n"
            f"  🌸 **Anshika :** `{bot_val}` {emoji}\n\n"
            f"  {verdict}\n\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
    except Exception as e:
        logger.debug(f"Dice match fallback: {e}")
        u_score = random.randint(1, 6)
        b_score = random.randint(1, 6)
        outcome = "Aap jeet gaye! 🎉" if u_score > b_score else ("Main jeet gayi! 🙈" if b_score > u_score else "Tie ho gaya! 🤝")
        await message.reply_text(
            f"🎲 **Dice Rolled!**\n\n"
            f"• **Aapka :** `{u_score}`\n"
            f"• **Mera :** `{b_score}`\n\n"
            f"{outcome} ✨"
        )


@Client.on_message(filters.command(["quote", "motivation"]))
async def quote_command(client: Client, message: Message):
    """Get an inspirational quote."""
    quote = random.choice(QUOTES)
    await message.reply_text(
        f"╭━━━━━━━〔 🌟 **DAILY MOTIVATION** 〕━━━━━━━╮\n\n"
        f"  {quote}\n\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )


@Client.on_message(filters.command(["couples", "couple"]))
async def couple_command(client: Client, message: Message):
    """Find the couple of the day in group chats (seeded by today's date)."""
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await message.reply_text("❌ **Ye command sirf groups mein kaam karta hai ji!** 🌸")

    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass

    today_str = datetime.now().strftime("%Y-%m-%d")
    chat_id = message.chat.id

    members = []
    try:
        async for member in client.get_chat_members(chat_id, limit=60):
            if member.user and not member.user.is_bot and not member.user.is_deleted:
                members.append(member.user)
    except Exception:
        pass

    if len(members) < 2:
        return await message.reply_text("🌸 Group mein couple banane ke liye kam se kam 2 active members hone chahiye ji! 🥰")

    seed_val = int(hashlib.md5(f"{chat_id}_{today_str}".encode()).hexdigest(), 16)
    rng = random.Random(seed_val)
    selected = rng.sample(members, 2)
    user1, user2 = selected[0], selected[1]
    compat = rng.randint(75, 99)

    verdicts = [
        "Rab ne bana di jodi! 💍✨ Nazar na lage kisi ki!",
        "Ekdum Perfect Match! Jaldi shaadi ka card bhej dena! 🥰💒",
        "In dono ka connection ekdum 5G speed me hai! 📶💖",
        "Dono ek doosre ke liye hi bane hain! Aise hi khush raho! 🌺🌹",
        "Kamaal ki understanding hai dono ke beech! 🌟💕",
    ]
    verdict = rng.choice(verdicts)

    status = await message.reply_text("🔮 **ᴅʜᴏᴏɴᴅʜ ʀᴀʜɪ ʜᴏᴏɴ ᴀᴀᴊ ᴋɪ ᴊᴏᴅɪ...** ✨")
    await asyncio.sleep(0.8)

    text = (
        f"╭━━━━━━━〔 💍 **COUPLE OF THE DAY** 〕━━━━━━━╮\n\n"
        f"  ✦ **ᴅᴀᴛᴇ :** `{today_str}`\n"
        f"  ✦ **ʟᴜᴄᴋʏ ᴄᴏᴜᴘʟᴇ :**\n"
        f"    {user1.mention} 💕 + {user2.mention} 💕\n\n"
        f"  ✦ **ᴄᴏᴍᴘᴀᴛɪʙɪʟɪᴛʏ :** **{compat}%** 🔥\n"
        f"  ✦ **ᴀɴsʜɪᴋᴀ's ᴠᴇʀᴅɪᴄᴛ :**\n"
        f"    _{verdict}_\n\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    try:
        await status.edit_text(text)
    except Exception:
        await message.reply_text(text)


@Client.on_message(filters.command(["propose", "proposal"]))
async def propose_command(client: Client, message: Message):
    """Propose to a user in group with Accept/Reject inline buttons."""
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await message.reply_text("❌ **Ye command sirf groups mein kaam karta hai ji!** 🌸")

    proposer = message.from_user
    if not proposer:
        return

    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        target_username = message.command[1].replace("@", "")
        try:
            target = await client.get_users(target_username)
        except Exception:
            pass

    if not target:
        return await message.reply_text(
            "💍 **Usage:** Reply to someone's message with `/propose` or `/propose @username`\n\n"
            "**Example:** `/propose @username`"
        )

    if target.id == proposer.id:
        return await message.reply_text("Arey khud ko propose kaise karoge ji? Kisi aur ko propose karo na! 🙈😂")

    if target.is_bot:
        if target.id == client.me.id:
            return await message.reply_text(
                f"Aww {proposer.mention}! 🙈 Main toh bohot sharma gayi! "
                "Par main toh sabki pyari dost Anshika hoon ji! Chalo hum hamesha ke liye best friends ban jaate hain! 💖✨"
            )
        return await message.reply_text("Bot ko propose mat karo ji, wo reply nahi karega! 🤖😂")

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💍 Accept", callback_data=f"prop_acc_{proposer.id}_{target.id}"),
            InlineKeyboardButton("💔 Reject", callback_data=f"prop_rej_{proposer.id}_{target.id}"),
        ]
    ])

    proposals = [
        "Dil se chaha hai aapko jaan se zyada, will you be mine forever? 💕💍",
        "Aapki ek smile pe dil fida ho gaya! Kya aap meri life partner banoge? 🌹✨",
        "Meri har khushi aapke sath judi hai, will you hold my hand through life? 💖",
    ]
    chosen_line = random.choice(proposals)

    text = (
        f"╭━━━━━━━〔 💍 **LOVE PROPOSAL** 〕━━━━━━━╮\n\n"
        f"  ✦ **ғʀᴏᴍ :** {proposer.mention}\n"
        f"  ✦ **ᴛᴏ :** {target.mention}\n\n"
        f"  💬 *\"{proposer.first_name} says: {chosen_line}\"*\n\n"
        f"  🌸 *Anshika: Awww kitna romantic moment hai! {target.first_name}, jaldi reply do na!* 🥰\n\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    await message.reply_text(text, reply_markup=buttons)


@Client.on_callback_query(filters.regex(r"^prop_(acc|rej)_(\d+)_(\d+)$"))
async def propose_callback_handler(client: Client, query: CallbackQuery):
    """Handle accept/reject button clicks for proposals."""
    data_parts = query.data.split("_")
    action = data_parts[1]
    proposer_id = int(data_parts[2])
    target_id = int(data_parts[3])

    if query.from_user.id != target_id:
        return await query.answer("❌ Arey ye proposal aapke liye nahi hai ji! Beech mein mat aao! 🙈", show_alert=True)

    try:
        proposer = await client.get_users(proposer_id)
        proposer_mention = proposer.mention
    except Exception:
        proposer_mention = f"[User](tg://user?id={proposer_id})"

    target_mention = query.from_user.mention

    if action == "acc":
        text = (
            f"╭━━━━━━━〔 🎉 **PROPOSAL ACCEPTED!** 〕━━━━━━━╮\n\n"
            f"  ✦ **ʜᴀᴘᴘʏ ᴄᴏᴜᴘʟᴇ :**\n"
            f"    {proposer_mention} 💕 💍 💕 {target_mention}\n\n"
            f"  🎉 **SHE/HE SAID YES!** 🥳\n"
            f"  {target_mention} ne {proposer_mention} ka proposal ACCEPT kar liya hai!\n\n"
            f"  🌸 *Anshika: Mubarak ho dono ko! Ekdum Rab ne bana di jodi! Dher saara pyaar aur duayein!* 🌹✨\n\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        await query.message.edit_text(text)
    else:
        text = (
            f"╭━━━━━━━〔 💔 **PROPOSAL REJECTED** 〕━━━━━━━╮\n\n"
            f"  ✦ **ᴜɴғᴏʀᴛᴜɴᴀᴛᴇʟʏ :**\n"
            f"    {target_mention} ne {proposer_mention} ka proposal REJECT kar diya... 🥺\n\n"
            f"  🥀 *Anshika: Ouch! Dil ke armaan aansuon me beh gaye... Koi baat nahi {proposer_mention}, aap bohot achhe ho! Himmat rakho!* 🌸\n\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        await query.message.edit_text(text)

