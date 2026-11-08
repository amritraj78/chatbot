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
  Ye file standard text ko aesthetic Small Caps font me convert karti hai
  jaisa Telegram bots ke menus, commands aur buttons me use hota hai.
  Example: "COPYRIGHT" -> "ᴄᴏᴘʏʀɪɢʜᴛ"
================================================================================
"""

import re

SMALL_CAPS_MAP = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ',
    'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
    'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ',
    'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ', 'z': 'ᴢ',
    'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ғ', 'G': 'ɢ',
    'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ',
    'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ', 'U': 'ᴜ',
    'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ',
}


def to_small_caps(text: str) -> str:
    """
    Converts plain text to aesthetic Small Capitals font.
    Preserves markdown symbols, links, emojis, and code formatting.
    """
    if not text:
        return text

    # Split lines and transform text while preserving markdown tags and commands
    result_chars = []
    i = 0
    n = len(text)

    while i < n:
        # Check if URL starting (http:// or https://)
        if text[i:i+7] == "http://" or text[i:i+8] == "https://":
            url_match = re.match(r"https?://[^\s\)]+", text[i:])
            if url_match:
                url_str = url_match.group(0)
                result_chars.append(url_str)
                i += len(url_str)
                continue

        # Check if bot command or mention (/command or @username)
        if text[i] in ['/', '@'] and i + 1 < n and text[i+1].isalnum():
            cmd_match = re.match(r"[/@][a-zA-Z0-9_]+", text[i:])
            if cmd_match:
                cmd_str = cmd_match.group(0)
                result_chars.append(cmd_str)
                i += len(cmd_str)
                continue

        # Check if code block `code`
        if text[i] == '`':
            code_match = re.match(r"`[^`]+`", text[i:])
            if code_match:
                code_str = code_match.group(0)
                result_chars.append(code_str)
                i += len(code_str)
                continue

        c = text[i]
        result_chars.append(SMALL_CAPS_MAP.get(c, c))
        i += 1

    return "".join(result_chars)
