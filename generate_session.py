#!/usr/bin/env python3
# ---------------------------------------------------------------------------------
#  VIP REACTION & AI CHATBOT - PYROGRAM V2 STRING SESSION GENERATOR
#  Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.
#  Support Group : https://t.me/amrit_feel
#  Updates Channel: https://t.me/privatethink
# ---------------------------------------------------------------------------------
"""
Interactive CLI Script to generate a secure Pyrogram v2 (64-bit) String Session
for VIP Reaction Bot ID Clone feature.
"""

import asyncio
import sys

# Official credentials or custom from environment
DEFAULT_API_ID = 6435225
DEFAULT_API_HASH = "4e984ea35f854762dcde906dce426c2d"

BANNER = r"""
╔═══════════════════════════════════════════════════════════════════════════╗
║            VIP REACTION BOT - PYROGRAM V2 SESSION GENERATOR               ║
║              Copyright (c) 2026 Amrit Raj (@Villanns). All Rights Reserved.║
╠═══════════════════════════════════════════════════════════════════════════╣
║  • Framework  : Pyrogram v2 (64-Bit Clean Session)                        ║
║  • Target     : VIP Reaction & AI Chatbot ID Clone Engine                 ║
║  • Security   : 100% In-Memory (No Session File Saved on Disk)           ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""


async def generate_session():
    print(BANNER)
    print("ℹ️  This script generates a genuine Pyrogram v2 String Session.")
    print("   The session string will also be sent directly to your Telegram 'Saved Messages'!\n")

    try:
        from pyrogram import Client
    except ImportError:
        print("❌ Pyrogram is not installed! Run: pip install pyrogram")
        sys.exit(1)

    api_id_in = input(f"Enter API_ID [Press Enter for default: {DEFAULT_API_ID}]: ").strip()
    api_id = int(api_id_in) if api_id_in else DEFAULT_API_ID

    api_hash_in = input(f"Enter API_HASH [Press Enter for default]: ").strip()
    api_hash = api_hash_in if api_hash_in else DEFAULT_API_HASH

    print("\n⏳ Initializing in-memory Pyrogram client...")
    print("📲 You will be asked for your phone number (+countrycode number) and OTP code.")
    print("🔒 If you have 2-Step Verification (Two-Factor Password), enter it when prompted.\n")

    client = Client(
        name=":memory:",
        api_id=api_id,
        api_hash=api_hash,
        in_memory=True
    )

    async with client:
        session_str = await client.export_session_string()
        me = await client.get_me()

        user_tag = f"@{me.username}" if me.username else me.first_name
        saved_msg = (
            f"✦ **VIP REACTION BOT - PYROGRAM V2 SESSION** ✦\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Account:** {me.first_name} ({user_tag})\n"
            f"🆔 **User ID:** `{me.id}`\n"
            f"🔑 **Pyrogram v2 String Session:**\n`{session_str}`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ **SECURITY WARNING:**\n"
            f"Never share this session string with anyone!\n\n"
            f"🚀 **How to activate ID Clone:**\n"
            f"Send this command to your VIP Reaction Bot:\n"
            f"`/idclone {session_str}`"
        )

        try:
            await client.send_message("me", saved_msg)
            sent_to_saved = True
        except Exception:
            sent_to_saved = False

        print("\n" + "═" * 70)
        print("🎉 SUCCESS! Pyrogram v2 String Session generated successfully!")
        print(f"👤 Account : {me.first_name} (ID: {me.id} | {user_tag})")
        if sent_to_saved:
            print("📬 Delivery: Sent directly to your Telegram 'Saved Messages'!")
        print("═" * 70)
        print(f"\n🔑 YOUR PYROGRAM V2 STRING SESSION:\n\n{session_str}\n")
        print("═" * 70)
        print("💡 Next Step:")
        print(f"   Copy the session above and send to your bot:")
        print(f"   /idclone {session_str}")
        print("═" * 70 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(generate_session())
    except (KeyboardInterrupt, SystemExit):
        print("\n🛑 Session generation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error during session generation: {e}")
