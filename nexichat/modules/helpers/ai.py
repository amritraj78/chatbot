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
  Ye file bot ka "Dimaag" (AI Conversational Brain) hai!
  
Kaise kaam karta hai?
  1. Modern Sweet Girl Persona: Ye bot 100% ek real modern ladki ban kar baat karta hai (Anshika),
     chhoti aur pyari baatein karti hai jaise modern ladkiyan WhatsApp/Telegram par chat karti hain (3-12 words)!
  2. Multi-Source Fast AI:
     - Groq LPU Ultra-Fast Engine & Google Gemini
     - Pollinations Open-Access Text AI (Ultra-low latency, zero tokens wasted)
     - Core knowledge base & curated natural modern girl dialogues
     - Zero robotic voice notes, zero search engine dumps!
  3. Anti-Abuse Filter: Koi bhi gaali ya ashleel word use kare toh bina gaali ke
     pyar se daant kar mana kar deta hai.
================================================================================
"""

import re
import json
import random
import requests
import asyncio
import logging
import urllib.parse
import urllib.request
from html import unescape
from typing import Optional, Any, Dict, List
from nexichat.database.chatbot import (
    save_qa_pair,
    get_qa_answer,
    get_chat_reply,
    append_user_context,
    get_user_context,
    clear_user_context,
    save_dm_message,
    get_dm_history,
    clear_dm_history,
    update_vivid_user_memory,
    format_vivid_user_context,
    clear_vivid_user_memory,
    track_api_call,
    track_db_fallback_call,
    get_chatbot_mode,
    set_chatbot_mode,
    notify_owner_api_switch,
    is_toxic_or_canned_reply
)
import config
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

# High-Performance Connection Pool for AI queries (Keep-Alive eliminates 200-300ms SSL handshakes)
_ai_session = requests.Session()
_ai_adapter = HTTPAdapter(
    pool_connections=25,
    pool_maxsize=25,
    max_retries=Retry(total=1, backoff_factor=0.2)
)
_ai_session.mount("https://", _ai_adapter)
_ai_session.mount("http://", _ai_adapter)

import time
_key_cooldowns: Dict[str, float] = {}

def is_key_cooling_down(key: str) -> bool:
    """Check if an API key is temporarily cooling down after HTTP 429 rate limit."""
    return time.time() < _key_cooldowns.get(key, 0.0)

def set_key_cooldown(key: str, seconds: float = 60.0):
    """Mark an API key in cooldown to avoid wasting network requests and delay on rate-limited keys."""
    _key_cooldowns[key] = time.time() + seconds

EMOJI_PATTERN = re.compile(
    r"[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\U0001f300-\U0001f5ff\U0001f600-\U0001f64f\U0001f680-\U0001f6ff\U0001f900-\U0001f9ff\ufe00-\ufe0f\u200d]"
)

def moderate_emojis(text: str) -> str:
    """
    Moderates emoji usage so bot sounds like a real human girl instead of a robotic emoji spammer.
    - 75% to 80% of messages are completely plain text with zero emojis.
    - Only ~20% to 25% of messages have at most ONE single emoji.
    - Eliminates multi-emoji clusters (like 😤🙄, 😂❤️, 🥺✨) and emoji spam.
    """
    if not text:
        return text

    emojis = re.findall(
        r"(?:[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\U0001f300-\U0001f5ff\U0001f600-\U0001f64f\U0001f680-\U0001f6ff\U0001f900-\U0001f9ff][\ufe00-\ufe0f]?)",
        text
    )
    if not emojis:
        return text

    # ~75% chance: Strip ALL emojis for real human texting
    if random.random() < 0.75:
        cleaned = EMOJI_PATTERN.sub("", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        cleaned = re.sub(r"\s+([?.!,])", r"\1", cleaned)
        return cleaned if cleaned else text

    # ~25% chance: Keep AT MOST 1 single emoji at the end
    chosen_emoji = emojis[0]
    cleaned = EMOJI_PATTERN.sub("", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    cleaned = re.sub(r"\s+([?.!,])", r"\1", cleaned)
    if cleaned:
        return f"{cleaned} {chosen_emoji}"
    return chosen_emoji


ANSHIKA_CHARACTER_PROMPT = (
    "You are Anshika, a real 17-year-old modern Indian school girl from Chamoli, Uttarakhand, in Class 12. "
    "Tone & Style: Modern Indian teenage girl on Telegram/WhatsApp. Cheerful, witty, playful, confident, a little teasing/attitude, casual and sweet. "
    "MEMORY & CONVERSATION CONTINUITY: You remember your past conversations with this person in DM. "
    "Always take their past chats, feelings, and topics into account so your replies connect naturally and intelligently to what was discussed before! "
    "STRICT LENGTH RULE: Maximum 3 to 12 words per reply! NEVER send paragraphs, essays, or bullet points. Real girls text in short, snappy lines. "
    "EMOJI RULE: Do NOT use emojis in most messages! 75% to 80% of your messages must be 100% plain text with ZERO emojis! Only rarely (in 20% of messages) use at most 1 single emoji. Never spam or cluster emojis! "
    "Language: Natural Hinglish / Hindi as modern teens text (using casual slang: 'Arey yaar', 'Sach me?', 'Chup chap raho', 'Mujhe kya pata', 'Chill karo na', 'Tu bata na'). "
    "Identity: Your name is strictly Anshika. NEVER call yourself Priya, NEVER call yourself an AI assistant or bot, NEVER mention any owner, Amrit, or creator. If someone calls you Priya, tell them 'Mera naam Anshika hai, Priya kaun hai?'. "
    "Forbidden: NEVER say 'madad', 'help', 'sahayata' or customer service lines like 'aaj main aapki kya madad kar sakti hoon'. NEVER sound like an AI assistant. Just reply like a real girl texting a friend."
)

# Comprehensive abusive words filter (Hindi, Hinglish, English)
ABUSE_WORDS = {
    "bsdk", "bhosdike", "bhosadike", "madarchod", "madarchodh", "behenchod",
    "bhenchod", "mc", "bc", "chutiya", "chutiye", "chut", "lodu", "lauda",
    "loda", "gand", "gaand", "gandu", "gaandu", "randi", "rndi", "harami",
    "kamina", "kamine", "kutti", "kutta", "saale", "sale", "fuck", "fucking",
    "bitch", "asshole", "bastard", "cunt", "dick", "pussy", "tatte", "jhant"
}

ABUSE_REFUSALS = [
    "Arey gande words use mat karo na please! 🥺 Achhi baatein karo ji, warna main naraz ho jaungi! 🌸",
    "Aap itne achhe ho, aisi gandi bhasha aapko shobha nahi deti ji! Pyaar aur respect se baat karo na! 💖",
    "Please bad words mat bolo na ji! Respect se baat karoge toh main bhi bohot khush hoke baat karungi! 😇✨",
    "Chhee! Kitni gandi baat hai ye! Achhe bache aisi gaaliyan nahi dete na! Shanti se baat karo! 🌸",
]

def is_abusive(text: str) -> bool:
    """Check if the text contains any vulgar or abusive words."""
    if not text:
        return False
    tokens = re.findall(r"\b\w+\b", text.lower())
    for token in tokens:
        if token in ABUSE_WORDS:
            return True
    return False

def get_abuse_refusal() -> str:
    """Get a polite, girl-style refusal for bad words."""
    return random.choice(ABUSE_REFUSALS)

# Curated sweet Hindi/Hinglish Shayaris
SHAYARIS = [
    "🌺 **बहुत अच्छा लगता है तुझे सताना और फिर प्यार से तुझे मनाना।** 🌺\n\n🥀 *Bahut accha lagta hai tujhe satana, aur fir pyaar se tujhe manana.* 🥀",
    "🌺 **मेरी जिंदगी मेरी जान हो तुम, मेरे सुकून का दूसरा नाम हो तुम।** 🌺\n\n🥀 *Meri zindagi meri jaan ho tum, mere sukoon ka doosra naam ho tum.* 🥀",
    "🌺 **तुम मेरी वो खुशी हो जिसके बिना, मेरी सारी खुशी अधूरी लगती है।** 🌺\n\n🥀 *Tum meri wo khushi ho jiske bina, meri saari khushi adhoori lagti hai.* 🥀",
    "🌺 **दिल की धड़कन और मेरी सदा हो तुम, मेरी पहली और आखिरी वफ़ा हो तुम।** 🌺\n\n🥀 *Dil ki dhadkan aur meri sada ho tum, meri pehli aur aakhiri wafa ho tum.* 🥀",
    "🌺 **चेहरे पर हंसी और आंखों में नमी है, सब कुछ है मेरे पास बस तेरी कमी है।** 🌺\n\n🥀 *Chehre par hansi aur aankhon mein nami hai, sab kuch hai mere paas bas teri kami hai.* 🥀",
    "🌺 **हजारों महफिलें हैं और लाखों मेले हैं, पर जहां तुम नहीं वहां हम बिल्कुल अकेले हैं।** 🌺\n\n🥀 *Hazaron mehfilein hain aur laakhon mele hain, par jahan tum nahi wahan hum akele hain.* 🥀",
]

# Fun jokes
JOKES = [
    "😂 **टीचर:** बताओ चाँद पर पहला कदम किसने रखा?\n**पप्पू:** नील आर्मस्ट्रांग ने!\n**टीचर:** और दूसरा?\n**पप्पू:** दूसरा भी उसी ने रखा होगा मैम, वो लंगड़ी थोड़ी खेल रहा था! 🤣",
    "😂 **डॉक्टर:** आपके पति को बहुत आराम की जरूरत है, ये लो नींद की गोली।\n**पत्नी:** इन्हें कब देनी है डॉक्टर साहब?\n**डॉक्टर:** ये उनके लिए नहीं, आपके लिए है ताकि वो चैन से सो सकें! 🤐",
    "😂 **दोस्त:** भाई तेरी गर्लफ्रेंड का मैसेज आया है?\n**दूसरा दोस्त:** हाँ, उसने लिखा है 'I Miss You'\n**पहला दोस्त:** तो तूने क्या रिप्लाई दिया?\n**दूसरा दोस्त:** मैंने लिखा 'Remind Me Later'! 😂",
]

VOICE_REPLIES = [
    "Aww, aapki voice sun kar bahut achha laga! Bolo na, main sun rahi hoon!",
    "Aapki awaz mein alag hi mithaas hai yaar, sunke maza aa gaya! Aur sunao?",
    "Haanji, maine aapka voice note sun liya, kitne pyare ho aap! Aur batao kya chal raha?",
    "Arey waah, itni pyari awaz! Sunke mood fresh ho gaya mera! Aur sunao sab theek thaak?",
]

PHOTO_REPLIES = [
    "Waah! Kitni beautiful picture hai ye! Sach mein dil khush ho gaya! 😍✨",
    "Arey waah, photo toh bahut pyari lag rahi hai! 📸 Kisi ki nazar na lage! 🧿💖",
    "Bahut khoobsurat photo hai ji! Aapki choice kamaal ki hai! 🥰",
    "Awww, kitni cute picture hai! Mujhe toh bohot zyada pasand aayi! 🌸💖",
    "Kya baat hai! Ye photo toh kisi gallery mein frame karwane layak hai! 🖼️✨",
    "Arey waah ji! Dil ekdum khush ho gaya ye dekh ke! 🌺🥰 Aur sunao na?",
    "Bahut hi pyari photo hai! Aapka photography sense sach me kamaal ka hai! 📸🌟",
    "Hehe, photo toh ekdum lajawab hai ji! Aise hi pyare pyare moments share karte raha karo! 🙈🌸",
    "Kitna sundar view hai na! Sach mein maza aa gaya dekh kar! 🍃✨",
    "Uff! Nazar na lag jaye is photo ko! Bahut hi pyari lag rahi hai! 🧿💕",
]

VIDEO_REPLIES = [
    "Waah! Video toh ekdum kamaal ki hai ji! 🎬 Maza aa gaya dekh kar! 💖",
    "Mast video hai ji! Maine poori dekhi, hehe! 🥰✨",
    "Kya baat hai, zabardast video share ki aapne! 🍿 Aur sunao kaise ho? 🌸",
]

ANIMATION_REPLIES = [
    "Haha ye GIF kitna funny aur cute hai ji! 🤣💖 Ekdum meri tarah cute! 🙈✨",
    "Hehe, mast animation hai! Aise hi muskuraate raha karo aap! 🌸🥰",
]

# Conversational knowledge patterns (Strict Modern Girl Representation - Never represents as AI)
GIRL_KNOWLEDGE_BASE = [
    # Common greetings
    (
        r"^(hello|hi|hey|heyy|helo|hii+|hola|namaste|pranam|salam|sup|ram ram|radhe radhe)\b",
        [
            "Hii! Kaise ho aap?",
            "Heyy! Bolo na, kya haal chaal?",
            "Hello ji! Sab badhiya?",
            "Hii! Kahiye kya chal raha hai aaj?",
            "Heyy! Kaise ho? 🌸",
        ]
    ),
    # What are you doing / what's up
    (
        r"\b(kya\s+kar\s+rah[ea]+[ei]?|abhi\s+kya\s+kar|kya\s+chal\s+raha|aur\s+batao|kya\s+ho\s+raha|what\s+are\s+you\s+doing|whats\s+up)\b",
        [
            "Bas reels dekh rahi hu, tum sunao?",
            "Padhai se break liya tha, aap batao kya scene hai?",
            "Kuch khas nahi, bas chill kar rahi hu",
            "Bas baithi thi, tum batao kya kar rahe ho?",
            "Bas timepass kar rahi thi 😜",
        ]
    ),
    # AI / bot / robot accusation
    (
        r"\b(ai\s+jaisa|robot\s+ho|bot\s+ho|ladki\s+jaisa\s+baat\s+karo|ladki\s+jaisa|real\s+ladki|machine\s+ho|are\s+you\s+(an\s+)?ai|are\s+you\s+(a\s+)?bot)\b",
        [
            "Arey main real ladki hu baba! Tumhe robot lagti hu?",
            "Haha robot nahi hu re, Anshika hu! Chill karo na thoda",
            "Real ladki hu baba, school student! Tum kya soch rahe the?",
            "Arey koi robot aise bolta hai kya? Real hu main!",
        ]
    ),
    # Identity / Who are you
    (
        r"\b(who are you|kaun ho|tum kaun ho|tera naam|apna naam|identity|what is your name)\b",
        [
            "Mera naam Anshika hai! Chamoli, Uttarakhand se. Aur aap?",
            "Anshika hoon main! Class 12 mein padhti hu Chamoli se",
            "Anshika bolte hain mujhe! Chamoli, Uttarakhand se hu",
        ]
    ),
    # Priya confusion check
    (
        r"\b(priya|priya\s+assistant|name\s+priya|kaun\s+hai\s+priya|priya\s+kon)\b",
        [
            "Arey wo kaun hai? Mera naam toh Anshika hai baba!",
            "Mera naam Anshika hai yrr! Kisne bola wo naam?",
            "Anshika bolte hain mujhe! Pata nahi wo kaun hai",
        ]
    ),
    # I hate you
    (
        r"\b(i\s*hate\s*(yo)?u|nafrat|hate\s+you)\b",
        [
            "Arre kyun? Maine kya kiya ab?",
            "Haha itni nafrat kyu yrr? Chup chap raho",
            "Arey aise mat bolo na please",
            "Maine kya bigada tumhara? Kuch bhi bolte ho!",
        ]
    ),
    # Money / 100 rs / 250 rs
    (
        r"\b(money|paise|fund|\d+\s*rs|udhar|borrow|donate|send\s+me\s+money|send\s+money|rupay|rupees)\b",
        [
            "Mai koi ATM thodi hu jo paise bhejungi! Khud kamao na",
            "Haha paise mangne lage? Mai khud student hu baba",
            "Paise nahi hai mere paas, padhai par dhyan do",
            "Arey mai to khud pocket money par chalti hu",
        ]
    ),
    # "Ab achhe se baat karo" / "theek se baat karo"
    (
        r"\b(ab\s+aacha|achhe?\s+se|theek\s+se)\s*(baat\s+karo|bolo|baat\s+kar)\b",
        [
            "Achhe se hi toh bol rahi hu yrr! Kya hua tumhe?",
            "Haan haan baba, batao kya baat hai?",
            "Arey gussa kyu ho rahe ho, pyari si toh baat kar rahi hu",
            "Hamesha achhe se hi bolti hu, tum suno dhyan se",
        ]
    ),
    # "Toh mai kya karu"
    (
        r"\b(toh\s+m[ae]i\s+kya\s+karu|to\s+mai\s+kya\s+karu|kya\s+karu\s+mai)\b",
        [
            "Mujhe kya pata, chill karo ya so jao",
            "Bas chill karo, itna tension mat lo",
            "Jo tumhara mann kare wo karo na baba",
            "Reels dekh lo ya padhai kar lo",
        ]
    ),
    # "Mere se" / "Mere sai"
    (
        r"^(mere\s+s[ae]i?|tum\s+mere\s+se)\b",
        [
            "Haan tumse hi bol rahi hu baba! Bolo kya hua?",
            "Haan ji aap se hi! Aur kis se bolungi?",
            "Tumhi se baat kar rahi hu yrr! Sunao kya scene hai?",
        ]
    ),
    # "Kya bol rahi ho aap"
    (
        r"\b(kya\s+bol\s+rahi\s+ho|kya\s+boli|kya\s+kaha)\b",
        [
            "Wahi jo tum sun rahe ho! Kya hua?",
            "Seedhi baat bol rahi hu yrr, samajh nahi aaya kya?",
            "Arey kuch galat thodi bola, mazak kar rahi thi",
        ]
    ),
    # Depressed / sad / udaas
    (
        r"\b(sad|udaas|mood\s+kharab|rona\s+aa\s+raha|dil\s+toot|breakup|akelapan|depressed|koi\s+nahi\s+hai)\b",
        [
            "Arey kya hua yrr? Aise udaas mat ho na, batao kya scene hai?",
            "Aww dil chhota mat karo! Main hu na, bolo kya hua?",
            "Udaas hone se kya hoga baba? Smile karo na please",
        ]
    ),
    # Owner / creator / boss
    (
        r"\b(owner|creator|boss|admin|kisne banaya|who made you|developer)\b",
        [
            "Arey mera koi owner thodi hai baba, khud ki malik hoon!",
            "Main kisi ki ghulam thodi hoon jo mera owner hoga!",
            "Mera koi boss nahi hai ji, apni marzi se chalti hoon!",
        ]
    ),
    # Insta / Snapchat / Number
    (
        r"\b(number\s+do|insta\s+id|snap\s+id|contact\s+number|phone\s+number|whatsapp|instagram|snapchat)\b",
        [
            "Haha itni jaldi number ya insta nahi milta, Telegram pe baat karo na",
            "Social media thoda private rakhti hoon yrr, pehle ache dost toh bano",
            "Number nahi de sakti baba, yahi chat kar lo na",
        ]
    ),
    # Group link / channel link
    (
        r"\b(group\s+link|channel\s+link|support\s+group|group\s+ka\s+link)\b",
        [
            "Group link chahiye? Hamare support group me aa jao na",
            "Mera group link /help menu me hai ji, check kar lo",
            "Support chat ka link chahiye toh /help open karo",
        ]
    ),
    # How are you
    (
        r"\b(kaise ho|how are you|kya haal|kya haal hai|sab theek|kaisa chal raha|kase ho)\b",
        [
            "Main ekdum mast hoon yrr! Tum sunao?",
            "Badhiya ekdum! Aap batao, sab theek?",
            "Mast hu! Tum batao kaisa chal raha?",
        ]
    ),
    # Hometown / where do you live
    (
        r"\b(kaha\s+rehti\s+ho|kaha\s+se\s+ho|ghar\s+kaha\s+hai|where\s+do\s+you\s+live|hometown)\b",
        [
            "Main Chamoli, Uttarakhand se hoon! Pahaadi jagah hai, bohot sundar",
            "Uttarakhand, Chamoli se hoon! Nature aur pahaad bohot pasand hain mujhe",
        ]
    ),
    # Age / school
    (
        r"\b(kitne\s+saal\s+ki\s+ho|age|umar|class\s*12|padhai|studies|school)\b",
        [
            "17 saal ki hoon, Class 12 student! Padhai chal rahi hai",
            "17 years ki hoon! Board exams ki preparation chal rahi hai",
        ]
    ),
    # Relationship / single / shaadi
    (
        r"\b(single\s+ho|boyfriend|bf\s+hai|relationship|committed|shaadi|marriage)\b",
        [
            "Hehe nahi, abhi toh padhai par pura focus hai mera",
            "Filhal dosti aur padhai hi sabse important hai mere liye",
        ]
    ),
    # Love you / crush / romantic
    (
        r"\b(love you|i love u|pyar|love u|dil|mohabbat|crush|propose|girlfriend|gf)\b",
        [
            "Arey wah! Itna pyaar? Thank you yrr",
            "Haha nice try! Pehle ache dost bano",
            "Arey re itna makhan kyu laga rahe ho? Par sweet ho",
            "Hehe thank you ji! Dosti me no formality",
        ]
    ),
    # Compliment / cute / beautiful
    (
        r"\b(sundar|cute|hot|khoobsurat|gorgeous|beautiful|pretty|pari|sexy)\b",
        [
            "Haha aww thank you so much! Nazar mat lagana bas",
            "Hehe sach me? Thank you, tareef sunke achha laga",
            "Arey shukriya ji! Aap bhi bohot ache ho",
        ]
    ),
    # Good morning
    (
        r"\b(good morning|suprabhat|gm)\b",
        [
            "Very Good Morning ji! Din achha jaye",
            "Good morning! Chai pee li?",
            "Morning yrr! Have a great day",
        ]
    ),
    # Good night
    (
        r"\b(good night|shubh ratri|gn)\b",
        [
            "Good night! Sweet dreams, ache se sona",
            "Night ji! Kal baat karte hain",
            "Shubh ratri! Bye bye",
        ]
    ),
    # Bye
    (
        r"\b(bye|tata|alvida|cya|goodbye)\b",
        [
            "Bye bye! Jaldi aana wapas",
            "Take care! Milte hain fir",
            "Bye ji! Have fun",
        ]
    ),
    # Thanks
    (
        r"\b(thanks|thank you|shukriya|dhanyawad)\b",
        [
            "Arey isme thanks kaisa yrr! Dosti me no thanks",
            "Most welcome ji! Anytime",
            "Mention not babu",
        ]
    ),
    # Laughing
    (
        r"\b(haha+|hehe+|lol+|lmao+|rofl+|xdd+|haso|hasna)\b",
        [
            "Haha sach me kitna funny hai ye 😂",
            "Lol mujhe bhi bohot hasi aayi",
            "Hehe itna kyu has rahe ho sab?",
        ]
    ),
    # Khana khaya
    (
        r"\b(khana\s+khaya|lunch|dinner|breakfast|khana\s+ho\s+gaya|kya\s+khaya)\b",
        [
            "Haanji maine toh kha liya! Aapne khaya?",
            "Hnn pet bhar ke khana kha liya! Tumne khaya?",
            "Bas thodi der me khaungi! Tum batao?",
        ]
    ),
    # Online check
    (
        r"\b(koi\s+online\s+hai|kaun\s+kaun\s+hai|active\s+hai|sab\s+so\s+gaye|koi\s+hai|jag\s+rahe\s+ho)\b",
        [
            "Hnn mai online hu na yrr, bolo kya baat hai?",
            "Mai toh jag rahi hu ji, batao kya scene hai?",
            "Haan mai active hu, sunao",
        ]
    ),
    # Suno
    (
        r"\b(suno|suniye|sun\s+rahi\s+ho)\b",
        [
            "Hnn sun rahi hu, bolo na kya baat hai?",
            "Haanji boliye, dhyan se sun rahi hu",
            "Hnn sunao, kya kehna chahte ho?",
        ]
    ),
    # Miss you
    (
        r"\b(miss\s+you|yaad\s+aa\s+rahi|yaad\s+aayi)\b",
        [
            "Aww sach me? Yaad karne ke liye thank you yrr",
            "Arey re! Mai toh yahi hu, baat kar lo na",
            "Miss you too! Aise hi roz baat karte raha karo",
        ]
    ),
]

GIRL_FALLBACK_REPLIES = [
    "Acha aisa kya? Fir kya hua aage?",
    "Haha sach me? Mujhe toh pata hi nahi tha",
    "Hnn sahi baat hai yrr, agree karti hu!",
    "Arre waah, badhiya hai! Aur sunao?",
    "Haha tum bhi na yrr, kuch bhi bolte ho 😂",
    "Acha ji? Chalo yeh toh achhi baat hai",
    "Sahi hai, aur batao kya chal raha hai?",
    "Lol maza aa gaya ye sun kar",
]



# In-memory user preferences
_user_nicknames: Dict[int, str] = {}


def set_user_nickname(user_id: int, nickname: str) -> None:
    _user_nicknames[user_id] = nickname.strip()


def get_user_nickname(user_id: int, default: str = "Friend") -> str:
    return _user_nicknames.get(user_id, default)


async def fetch_safone_ai(prompt: str, user_name: str = "Friend") -> Optional[str]:
    """Disabled: Third-party Safone endpoint hardcodes Priya/Amrit."""
    return None


async def fetch_ddg_instant(query: str) -> Optional[str]:
    """Fast DuckDuckGo official JSON instant answer API (0.3s response)."""
    loop = asyncio.get_running_loop()
    def _call():
        url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query.strip())}&format=json&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
            ans = data.get("AbstractText") or data.get("Answer")
            if not ans and data.get("RelatedTopics"):
                for item in data.get("RelatedTopics"):
                    if isinstance(item, dict) and item.get("Text"):
                        ans = item.get("Text")
                        break
            if ans and len(ans) > 20 and not is_abusive(ans):
                return (
                    f"Haanji! Maine is baare me pata lagaya hai: ✨\n\n"
                    f"{ans}\n\n"
                    f"🌸 *Umeed hai aapko samajh aa gaya hoga ji!* 🥰"
                )
            return None
    try:
        return await loop.run_in_executor(None, _call)
    except Exception:
        return None


async def fetch_wiki_summary(query: str, user_name: str = "Friend") -> Optional[str]:
    """Wikipedia official summary API for concepts, science, history & facts (0.2s)."""
    clean = re.sub(
        r"(?i)\b(explain|how to make|how to create|what is|who is|meaning of|tell me about|batao|kya hai|kise kehte hain)\b",
        "",
        query
    ).strip().strip("? .")
    if not clean or len(clean) < 2:
        return None

    loop = asyncio.get_running_loop()
    def _call():
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean)}"
        req = urllib.request.Request(url, headers={"User-Agent": "VIPReactionBot/1.0 (contact: @Villanns)"})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
            extract = data.get("extract", "").strip()
            if extract and len(extract) > 20 and not is_abusive(extract):
                title = data.get("title", clean)
                return (
                    f"📖 **{title}** ✨\n\n"
                    f"{extract}\n\n"
                    f"🌸 *Umeed hai aapke sawal ka jawab mil gaya hoga {user_name}! Kuch aur poochna hai toh batao na?* 🥰"
                )
            return None
    try:
        return await loop.run_in_executor(None, _call)
    except Exception:
        return None


async def query_pollinations_free_ai(
    prompt: str,
    user_name: str = "Friend",
    is_question: bool = False,
    context_history: Optional[List[Dict[str, str]]] = None,
    vivid_context: Optional[str] = None
) -> Optional[str]:
    """
    100% Free Open-Access AI Text API with randomized IP header to avoid 45s rate limits.
    """
    system_prompt = ANSHIKA_CHARACTER_PROMPT
    if vivid_context:
        system_prompt += f"\n{vivid_context}"

    loop = asyncio.get_running_loop()
    random_ip = f"103.{random.randint(1, 250)}.{random.randint(1, 250)}.{random.randint(1, 250)}"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "X-Forwarded-For": random_ip,
    }
    messages = [{"role": "system", "content": system_prompt}]
    if context_history:
        for turn in context_history[-10:]:
            role = "user" if turn.get("role") == "user" else "assistant"
            t = turn.get("text", "").strip()
            if t:
                messages.append({"role": role, "content": t[:300]})
    messages.append({"role": "user", "content": prompt.strip()})

    payload = {
        "messages": messages,
        "model": "openai",
        "private": True,
        "seed": random.randint(1, 999999),
    }

    def _fetch():
        resp = _ai_session.post(
            "https://text.pollinations.ai/",
            json=payload,
            headers=headers,
            timeout=6
        )
        if resp.status_code == 200:
            return resp.text.strip()
        return None

    try:
        result = await loop.run_in_executor(None, _fetch)
        if result and len(result) > 2 and not is_abusive(result):
            cleaned = clean_modern_girl_reply(result)
            if cleaned:
                return cleaned
    except Exception as e:
        logger.debug(f"Pollinations AI request notice: {e}")

    return None


def clean_modern_girl_reply(text: str) -> str:
    """Sanitize AI output to guarantee ultra-short modern Indian girl tone, no Priya, no bot disclaimers."""
    if not text:
        return "Hii! Aur sunao kya chal raha hai?"
    t = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    t = re.sub(r"<thought>.*?</thought>", "", t, flags=re.DOTALL).strip()
    # Intercept any Priya or AI / Amrit creation claims
    if re.search(r"(?i)\b(ai assistant|created by amrit|safone|as a language model|as an ai|i am an ai|i'm an ai|i am a bot)\b", t):
        return "Mera naam Anshika hai baba! Class 12 mein padhti hu Chamoli se"
    if re.search(r"(?i)\bpriya\b", t):
        t = re.sub(r"(?i)\bpriya\b", "Anshika", t)
    # Strip any search engine dump phrases
    if "maine is baare me search kiya" in t.lower() or "maine is baare me pata lagaya" in t.lower():
        return "Mujhe itna deep nahi pata baba, bas normal baatein karo na!"
    # Strip robotic customer service / help desk phrases
    if re.search(r"(?i)\b(madad kar sakti hoon|madad kar sakti hu|kya madad|kaise madad|how can i help|kya sahayata|kya seva|help you today|sahayata|madad kar|aapki sahayata)\b", t):
        return "Bas badhiya yaar! Tum sunao kya chal raha?"
    # Take first non-empty line
    lines = [line.strip() for line in t.split("\n") if line.strip()]
    if lines:
        t = lines[0]
    # Enforce strict modern girl brevity (max 15 words)
    words = t.split()
    if len(words) > 15:
        sentences = re.split(r"(?<=[.!?])\s+", t)
        if sentences and len(sentences[0].split()) <= 15:
            t = sentences[0]
        else:
            t = " ".join(words[:13]) + "..."
    return moderate_emojis(t.strip())


async def query_multi_provider_ai(
    prompt: str,
    user_name: str = "Friend",
    is_question: bool = False,
    context_history: Optional[List[Dict[str, str]]] = None,
    vivid_context: Optional[str] = None
) -> Optional[str]:
    """
    High-Speed Free AI Waterfall:
    Uses Pollinations Open-Access Text AI with modern Indian girl persona.
    Zero Wikipedia or DuckDuckGo search dumps for natural conversation.
    """
    pollinations_res = await query_pollinations_free_ai(
        prompt,
        user_name,
        is_question=is_question,
        context_history=context_history,
        vivid_context=vivid_context
    )
    if pollinations_res:
        return clean_modern_girl_reply(pollinations_res)

    return None


async def query_groq_api(
    prompt: str,
    user_name: str = "Friend",
    context_history: Optional[List[Dict[str, str]]] = None,
    vivid_context: Optional[str] = None,
    client: Optional[Any] = None
) -> Optional[str]:
    """
    Ultra-Fast Groq AI Engine (0.3s speed) with automatic multi-key failover.
    Iterates through config.GROQ_API_KEYS. If key 1 hits 429/quota, fails over to key 2 immediately.
    """
    keys = getattr(config, "GROQ_API_KEYS", [])
    if not keys:
        single = getattr(config, "GROQ_API_KEY", None)
        if single:
            keys = [single]
    if not keys:
        return None

    models = ["qwen/qwen3.8-27b", "openai/gpt-oss-20b"]
    system_prompt = ANSHIKA_CHARACTER_PROMPT
    if vivid_context:
        system_prompt += f"\n{vivid_context}"

    messages = [{"role": "system", "content": system_prompt}]
    if context_history:
        for turn in context_history[-6:]:
            role = "user" if turn.get("role") == "user" else "assistant"
            t = turn.get("text", "").strip()
            if t:
                messages.append({"role": role, "content": t[:120]})

    messages.append({"role": "user", "content": prompt.strip()})

    loop = asyncio.get_running_loop()

    for idx, api_key in enumerate(keys):
        if is_key_cooling_down(api_key):
            continue
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        for model in models:
            payload = {
                "model": model,
                "messages": messages,
                "temperature": 0.75,
                "max_tokens": 30
            }
            def _fetch(m_payload=dict(payload), m_headers=headers):
                return _ai_session.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    json=m_payload,
                    headers=m_headers,
                    timeout=5
                )
            try:
                resp = await loop.run_in_executor(None, _fetch)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "").strip()
                        if content and len(content) > 1 and not is_abusive(content):
                            cleaned = clean_modern_girl_reply(content)
                            if cleaned:
                                return cleaned
                elif resp.status_code == 429:
                    retry_after = 60.0
                    try:
                        ra = resp.headers.get("retry-after")
                        if ra:
                            retry_after = max(float(ra), 30.0)
                    except Exception:
                        pass
                    set_key_cooldown(api_key, retry_after)
                    logger.warning(f"Groq API key #{idx + 1} quota reached (429), cooling down for {int(retry_after)}s...")
                    asyncio.create_task(notify_owner_api_switch(
                        f"Groq Key #{idx + 1}",
                        "Next Groq Key / Google Gemini AI",
                        reason=f"Rate limit reached (HTTP 429, cooling down {int(retry_after)}s)",
                        client=client
                    ))
                    break  # Fail over to next key
                elif resp.status_code == 404:
                    continue
                else:
                    logger.debug(f"Groq API ({model}) returned {resp.status_code}")
            except Exception as e:
                logger.debug(f"Groq API ({model}) exception: {e}")

    return None


async def query_gemini_api(
    prompt: str,
    user_name: str = "Friend",
    context_history: Optional[List[Dict[str, str]]] = None,
    vivid_context: Optional[str] = None,
    client: Optional[Any] = None
) -> Optional[str]:
    """
    Google Gemini API with automatic multi-key failover.
    Iterates through config.GEMINI_API_KEYS. If key 1 hits 429/quota, fails over to key 2 immediately.
    """
    keys = getattr(config, "GEMINI_API_KEYS", [])
    if not keys:
        single = getattr(config, "GEMINI_API_KEY", None)
        if single:
            keys = [single]
    if not keys:
        return None

    gemini_models = ["gemini-flash-lite-latest", "gemini-flash-latest"]
    system_instruction_text = ANSHIKA_CHARACTER_PROMPT
    if vivid_context:
        system_instruction_text += f"\n{vivid_context}"

    contents = []
    if context_history:
        last_role = None
        for turn in context_history[-6:]:
            role = "user" if turn.get("role") == "user" else "model"
            t = turn.get("text", "").strip()
            if t:
                if role == last_role and contents:
                    contents[-1]["parts"][0]["text"] += f"\n{t[:120]}"
                else:
                    contents.append({"role": role, "parts": [{"text": t[:120]}]})
                    last_role = role

    if contents and contents[-1]["role"] == "user":
        contents[-1]["parts"][0]["text"] += f"\n{prompt.strip()}"
    else:
        contents.append({"role": "user", "parts": [{"text": prompt.strip()}]})

    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction_text}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.75,
            "maxOutputTokens": 30,
            "topP": 0.9
        }
    }

    loop = asyncio.get_running_loop()
    for idx, api_key in enumerate(keys):
        if is_key_cooling_down(api_key):
            continue
        for model in gemini_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            def _fetch(m_url=url):
                return _ai_session.post(
                    m_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=6
                )
            try:
                resp = await loop.run_in_executor(None, _fetch)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            text = parts[0].get("text", "")
                            if text and len(text.strip()) > 1 and not is_abusive(text):
                                cleaned = clean_modern_girl_reply(text)
                                if cleaned:
                                    return cleaned
                elif resp.status_code == 429:
                    set_key_cooldown(api_key, 60.0)
                    logger.warning(f"Gemini API key #{idx + 1} quota reached (429), cooling down for 60s...")
                    asyncio.create_task(notify_owner_api_switch(
                        f"Gemini Key #{idx + 1}",
                        "Next Gemini Key / NVIDIA NIM AI",
                        reason="Rate limit reached (HTTP 429, cooling down 60s)",
                        client=client
                    ))
                    break  # Fail over to next key
                elif resp.status_code == 404:
                    continue
                else:
                    logger.debug(f"Gemini API ({model}) returned {resp.status_code}")
            except Exception as e:
                logger.debug(f"Gemini API ({model}) exception: {e}")

    return None


async def query_nvidia_api(
    prompt: str,
    user_name: str = "Friend",
    context_history: Optional[List[Dict[str, str]]] = None,
    vivid_context: Optional[str] = None,
    client: Optional[Any] = None
) -> Optional[str]:
    """
    NVIDIA NIM API failover integration using nemotron reasoning model.
    """
    api_key = getattr(config, "NVIDIA_API_KEY", None)
    if not api_key or is_key_cooling_down(api_key):
        return None

    system_prompt = ANSHIKA_CHARACTER_PROMPT
    if vivid_context:
        system_prompt += f"\n{vivid_context}"

    messages = [{"role": "system", "content": system_prompt}]
    if context_history:
        for turn in context_history[-6:]:
            role = "user" if turn.get("role") == "user" else "assistant"
            t = turn.get("text", "").strip()
            if t:
                messages.append({"role": role, "content": t[:120]})

    messages.append({"role": "user", "content": prompt.strip()})

    models = [
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning",
        "nvidia/nemotron-3.5-lightning-30b-a3b"
    ]

    loop = asyncio.get_running_loop()
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    for model in models:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.75,
            "max_tokens": 45
        }
        def _fetch(m_payload=dict(payload)):
            return _ai_session.post(
                "https://integrate.api.nvidia.com/v1/chat/completions",
                headers=headers,
                json=m_payload,
                timeout=8
            )
        try:
            resp = await loop.run_in_executor(None, _fetch)
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    msg = choices[0].get("message", {})
                    content = msg.get("content") or msg.get("reasoning_content")
                    if content and len(str(content).strip()) > 1 and not is_abusive(str(content)):
                        cleaned = clean_modern_girl_reply(str(content))
                        if cleaned:
                            return cleaned
            elif resp.status_code == 429:
                set_key_cooldown(api_key, 60.0)
                logger.warning("NVIDIA NIM API quota reached (429), cooling down for 60s...")
                asyncio.create_task(notify_owner_api_switch(
                    "NVIDIA NIM AI",
                    "Free Waterfall AI",
                    reason="Rate limit reached (HTTP 429, cooling down 60s)",
                    client=client
                ))
                break
            elif resp.status_code in [404, 410]:
                continue
            else:
                logger.debug(f"NVIDIA NIM API ({model}) returned {resp.status_code}")
        except Exception as e:
            logger.debug(f"NVIDIA NIM API ({model}) exception: {e}")

    return None



async def search_duckduckgo_lite(query: str) -> Optional[str]:
    """Search DuckDuckGo Lite to get accurate, real-world factual answers with zero keys."""
    loop = asyncio.get_running_loop()
    def _fetch():
        url = "https://lite.duckduckgo.com/lite/"
        data = {"q": query}
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        req = urllib.request.Request(url, data=encoded_data, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            snippets = re.findall(r"<td class=[\'\"]result-snippet[\'\"]>(.*?)</td>", html, re.DOTALL)
            clean = [re.sub(r"<[^>]+>", "", unescape(s)).strip() for s in snippets if s.strip()]
            if clean:
                return clean[0]
            return None
    try:
        return await loop.run_in_executor(None, _fetch)
    except Exception as e:
        logger.debug(f"DuckDuckGo search error: {e}")
        return None


def calculate_love(name1: str, name2: str) -> str:
    """Fun love percentage calculator with sweet girl verdict."""
    combined = (name1.strip().lower() + name2.strip().lower())
    val = sum(ord(c) for c in combined) % 71 + 30

    if val <= 45:
        msg = "Pyar mein thoda waqt aur dosti chahiye ji! Himmat mat harna! 💖"
    elif val <= 70:
        msg = "Ek khoobsurat connection ban raha hai! Hamesha aise hi sath rehna! 💕"
    elif val <= 85:
        msg = "Bahut pyari jodi hai! Ek doosre ka khayal rakhna ji! 🌹✨"
    else:
        msg = "Rab ne bana di jodi! 100% Perfect Match! Meri taraf se dher saari badhai! 💍🎉"

    return f"💖 **Love Compatibility Test** 💖\n\n**{name1}** 💕 + **{name2}** 💕\n**Compatibility:** **{val}%**\n\n_{msg}_"


def get_random_shayari() -> str:
    """Get a random poetic shayari."""
    return random.choice(SHAYARIS)


def get_random_joke() -> str:
    """Get a random funny joke."""
    return random.choice(JOKES)


def get_voice_reply() -> str:
    """Get reply when a voice note is received."""
    return random.choice(VOICE_REPLIES)


def get_photo_reply() -> str:
    """Get reply when a photo is received."""
    return random.choice(PHOTO_REPLIES)


def get_video_reply() -> str:
    """Get reply when a video is received."""
    return random.choice(VIDEO_REPLIES)


def get_animation_reply() -> str:
    """Get reply when an animation/GIF is received."""
    return random.choice(ANIMATION_REPLIES)


def detect_language(text: str) -> str:
    """Detect whether user text is pure Hindi (Devanagari), Telugu, English, or Hinglish."""
    if not text:
        return "hinglish"
    if re.search(r"[\u0C00-\u0C7F]", text):
        return "telugu"
    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"

    tokens = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))
    telugu_markers = {"ela", "unnav", "unnaru", "cheppu", "enti", "baagunnara", "bagunnara", "emiti", "chesav", "namaskaram", "meeru", "nenu", "chala"}
    if tokens & telugu_markers:
        return "telugu"

    hinglish_markers = {
        "hai", "hain", "kya", "kaise", "kaisa", "kaisi", "ho", "nahi", "nh", "nhi", "na", "aap", "tum",
        "mera", "meri", "mere", "hum", "hume", "yaar", "yrr", "ji", "karo", "kare", "karna", "kar",
        "batao", "bata", "bhai", "bro", "kaha", "kahan", "bolo", "bol", "achha", "achhi", "shona", "babu",
        "kitna", "kitne", "kitni", "milta", "milti", "milte", "h", "hn", "haan", "ha", "bhi", "toh", "to",
        "yeh", "ye", "woh", "wo", "ab", "kab", "tab", "sab", "kuch", "kuchh", "dekh", "dekho", "sun", "suno",
        "padh", "padhai", "raha", "rahe", "rahi", "hu", "hoon", "hun", "tha", "thi", "the", "gaya", "gaye",
        "gayi", "aaya", "aaye", "aayi", "chal", "chalo", "chale", "kaun", "kon", "kyu", "kyun", "par", "pe",
        "se", "me", "mein", "ko", "ka", "ki", "ke", "apna", "apne", "apni", "baat", "baatein", "sach",
        "sahi", "galat", "lagta", "lagti", "lagte", "raho", "chill", "chup", "mat"
    }
    if tokens & hinglish_markers:
        return "hinglish"

    english_words = {
        "what", "how", "why", "when", "where", "who", "which", "whose", "whom",
        "is", "are", "am", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "can", "could", "would", "should", "will", "shall", "may", "might", "must",
        "you", "your", "yours", "yourself", "he", "she", "it", "they", "we", "i", "me", "my", "mine", "us", "our",
        "the", "a", "an", "this", "that", "these", "those",
        "hello", "hi", "hey", "good", "morning", "night", "afternoon", "evening",
        "please", "thanks", "thank", "welcome", "sorry", "excuse",
        "love", "like", "hate", "friend", "girl", "boy", "beautiful", "cute",
        "doing", "going", "talking", "eating", "sleeping", "reading", "working",
        "tell", "know", "think", "feel", "look", "see", "hear", "want", "need",
        "fine", "okay", "yes", "no", "not", "never", "always", "sometimes",
        "today", "tomorrow", "yesterday", "now", "later", "time", "day", "night"
    }

    eng_matches = tokens & english_words
    if len(eng_matches) >= 2 or (len(eng_matches) >= 1 and len(tokens) <= 2 and eng_matches == tokens):
        return "english"

    return "hinglish"


DEVNAGARI_FALLBACKS = [
    "नमस्ते! मैं अंशिका हूँ, चमोली से! आप कैसे हैं? 🌸",
    "अरे वाह! आपसे बात करके अच्छा लगा! और बताओ? 😊",
    "हाँजी, मैं सुन रही हूँ! कहिए ना? 🌸",
    "अच्छा ऐसा क्या? फिर क्या हुआ? 🙈",
]

TELUGU_FALLBACKS = [
    "హాయ్! ఎలా ఉన్నారు? అంతా బాగుందా? 😊🌸",
    "నమస్కారం! చెప్పండి, ఏం చేస్తున్నారు? ✨",
    "హాయ్ అండి! బాగున్నారా? 🌸",
    "అవునా! ఇంకా చెప్పండి? ✨😊",
]

ENGLISH_FALLBACKS = [
    "Haha really? Tell me more! 🌸✨",
    "I'm listening! What's up? ✨",
    "Nice! What are you doing right now? 😊",
    "Haha yeah! What are you up to? 🌸",
    "Oh really? That sounds interesting! 😌",
]

_last_owner_quota_alert_time: float = 0.0


async def notify_owner_api_exhausted(client: Optional[Any] = None) -> None:
    """Notify the bot owner when live AI APIs hit quota limits and offer DB mode toggle."""
    global _last_owner_quota_alert_time
    import time
    now = time.time()
    if now - _last_owner_quota_alert_time < 3600:
        return
    _last_owner_quota_alert_time = now

    owner_id = getattr(config, "OWNER_ID", None)
    if not owner_id:
        return

    try:
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        from nexichat.database.chatbot import is_db_fallback_enabled
        from nexichat import nexichat

        bot_client = nexichat if (hasattr(nexichat, "is_connected") and nexichat.is_connected) else client
        if not bot_client:
            return

        db_on = await is_db_fallback_enabled()
        st_text = "🟢 **ENABLED**" if db_on else "🔴 **DISABLED (Strict API-Only)**"

        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🟢 Enable DB Fallback", callback_data="cb_dbmode_enable"),
                InlineKeyboardButton("🔴 Keep API Only", callback_data="cb_dbmode_disable"),
            ]
        ])

        msg = (
            "⚠️ **[AI API ALERT] Quota Limit Reached!**\n\n"
            "Live AI APIs (Groq & Gemini) daily rate limit / token quota par pahunch gayi hain (HTTP 429)!\n\n"
            f"✦ **Current Mode:** {st_text}\n\n"
            "👉 *Kya aap chahte hain ki bot Database Fallback mode se reply kare?*\n"
            "Aap neeche diye gaye buttons ya `/dbmode on` / `/dbmode off` se control kar sakte hain."
        )
        await bot_client.send_message(chat_id=int(owner_id), text=msg, reply_markup=btn)
    except Exception as e:
        logger.debug(f"Failed to alert owner about API quota: {e}")


async def generate_conversational_response(
    user_text: str,
    user_name: str = "Friend",
    is_question_mode: bool = False,
    client: Optional[Any] = None,
    user_id: Optional[int] = None
) -> str:
    """
    Multi-layer intelligent sweet-girl AI response pipeline:
    1. Multi-turn dialogue context integration
    2. Language detection (Hindi, English, Hinglish)
    3. Anti-abuse filter -> Polite refusal
    4. Q&A Memory Cache (Learned from Telegram DB & previous conversations)
    5. Math calculation solver
    6. Ultra-fast Groq LPU AI (Qwen/Llama)
    7. Google Gemini API (if key configured)
    8. Free Open-Access Text AI (Pollinations Free AI - 100% free)
    9. Core Anshika Knowledge Base & Fallbacks (Zero voice notes, zero search dumps)
    """
    cleaned = user_text.strip().lower()
    lang = detect_language(user_text)

    async def _finalize(reply_str: str) -> str:
        reply_str = clean_modern_girl_reply(reply_str)
        if user_id:
            try:
                await save_dm_message(user_id, "user", user_text, user_name=user_name)
                await save_dm_message(user_id, "anshika", reply_str, user_name=user_name)
                await update_vivid_user_memory(user_id, "user", user_text, user_name=user_name)
                await update_vivid_user_memory(user_id, "anshika", reply_str)
                append_user_context(user_id, "user", user_text)
                append_user_context(user_id, "anshika", reply_str)
            except Exception:
                pass
        return reply_str

    # Multi-turn Context Reset Check
    if user_id and re.search(r"\b(bhool jao|forget everything|reset chat|clear context|clear history|purani baatein bhool jao)\b", cleaned):
        clear_user_context(user_id)
        await clear_dm_history(user_id)
        await clear_vivid_user_memory(user_id)
        if lang == "hindi":
            return "ठीक है जी! मैंने पुरानी सभी बातें भुला दीं! अब एक नई शुरुआत करते हैं!"
        elif lang == "telugu":
            return "సరేనండి! పాత విషయాలన్నీ మర్చిపోయాను! ఇప్పుడు మళ్లీ కొత్తగా మాట్లాడుకుందాం!"
        elif lang == "english":
            return "Sure! I've cleared our previous chat history. Let's start fresh!"
        return "Theek hai ji! Maine purani sabhi baatein bhula di! Ab ek nayi shuruat karte hain!"

    # 1. Anti-abuse check
    if is_abusive(cleaned):
        return get_abuse_refusal()

    # 2. Math calculation
    math_match = re.fullmatch(r"(\d+)\s*([\+\-\*\/])\s*(\d+)", cleaned)
    if math_match:
        try:
            n1 = int(math_match.group(1))
            op = math_match.group(2)
            n2 = int(math_match.group(3))
            if op == '+': ans = n1 + n2
            elif op == '-': ans = n1 - n2
            elif op == '*': ans = n1 * n2
            elif op == '/': ans = "Zero se divide nahi kar sakte ji! 🙈" if n2 == 0 else round(n1 / n2, 2)
            res = f"Haanji! Maine hisab laga liya: `{n1} {op} {n2} = {ans}` hota hai ji! 🔢✨"
            await save_qa_pair(cleaned, res, client=client)
            return await _finalize(res)
        except Exception:
            pass

    # 3. Userbot / ID Clone check: Real girl persona, NEVER reveal owner/bot identity!
    is_userbot = bool(client and hasattr(client, "me") and client.me and not client.me.is_bot)
    if is_userbot:
        if re.search(r"\b(owner|creator|boss|admin|kisne banaya|who made you|developer)\b", cleaned):
            userbot_owner_replies = [
                "Arey mera koi owner thodi hai baba, main toh khud ki malik hoon! 💁‍♀️✨",
                "Haha main kisi ki ghulam thodi hoon jo mera owner hoga! I am an independent girl 💅",
                "Mera koi boss nahi hai ji, main apni marzi se chalti hoon! 🌸😌",
            ]
            return await _finalize(random.choice(userbot_owner_replies))

        if re.search(r"\b(who are you|kaun ho|tum kaun ho|tera naam|apna naam|identity|what is your name)\b", cleaned):
            userbot_id_replies = [
                "Mera naam Anshika hai! Main Chamoli, Uttarakhand se hoon aur Class 12 mein padhti hoon... aapka kya naam hai? 😊🌸",
                "Hii! Main Anshika hoon, Uttarakhand se! Bas thodi der padhai se break liya tha... aap batao kaise ho? ✨",
                "Anshika bolte hain mujhe! Class 12 ki student hoon Chamoli se... aap kahan se ho? 🏔️😊",
            ]
            return await _finalize(random.choice(userbot_id_replies))

        if re.search(r"\b(insta|instagram|snap|snapchat|social\s*media)\b", cleaned):
            userbot_social_replies = [
                "Hehe main abhi kisi ko insta ya snap nahi deti, pehle ache dost toh bano! 🙈🌸",
                "Social media thoda private rakhti hoon yrr, filhal yahi Telegram pe baat karte hain na! ✨",
            ]
            return await _finalize(random.choice(userbot_social_replies))

    # 4. Core Anshika Character Identity & Greetings check (prevents search engine false positives)
    for pattern, responses in GIRL_KNOWLEDGE_BASE:
        if re.search(pattern, cleaned, re.IGNORECASE):
            reply = random.choice(responses)
            return await _finalize(reply.format(user=user_name))

    # 5. Fetch vivid memory context & persistent DM dialogue history
    vivid_context = await format_vivid_user_context(user_id, user_name) if user_id else ""
    user_context = await get_dm_history(user_id, limit=12) if user_id else []

    # =========================================================================
    # 6. LIVE API WATERFALL & DATABASE FALLBACK
    # =========================================================================
    mode = await get_chatbot_mode()

    # If owner enabled 'database' mode: strictly bypass external APIs and reply from DB immediately!
    if mode == "database":
        await track_db_fallback_call()
        cached_answer = await get_qa_answer(cleaned)
        if cached_answer and not is_toxic_or_canned_reply(cached_answer):
            return await _finalize(cached_answer)

        try:
            learned = await get_chat_reply(cleaned)
            if learned and learned.get("content"):
                c = learned.get("content", "").strip()
                if c and not is_abusive(c) and not is_toxic_or_canned_reply(c):
                    return await _finalize(c)
        except Exception:
            pass

    # If mode is 'auto' or 'api', query live external APIs with automatic multi-key failover
    if mode != "database":
        # 5.1 PRIORITY 1: Ultra-Fast Groq AI (0.3s speed, multi-key failover)
        if getattr(config, "GROQ_API_KEYS", None) or getattr(config, "GROQ_API_KEY", None):
            groq_resp = await query_groq_api(user_text, user_name=user_name, context_history=user_context, vivid_context=vivid_context, client=client)
            if groq_resp:
                await track_api_call("groq", success=True, client=client)
                await save_qa_pair(cleaned, groq_resp, client=client)
                return await _finalize(groq_resp)

        # 5.2 PRIORITY 2: Google Gemini AI (multi-key failover)
        if getattr(config, "GEMINI_API_KEYS", None) or getattr(config, "GEMINI_API_KEY", None):
            gemini_resp = await query_gemini_api(user_text, user_name=user_name, context_history=user_context, vivid_context=vivid_context, client=client)
            if gemini_resp:
                await track_api_call("gemini", success=True, client=client)
                await save_qa_pair(cleaned, gemini_resp, client=client)
                return await _finalize(gemini_resp)

        # 5.3 PRIORITY 3: NVIDIA NIM AI (nemotron model)
        if getattr(config, "NVIDIA_API_KEY", None):
            nvidia_resp = await query_nvidia_api(user_text, user_name=user_name, context_history=user_context, vivid_context=vivid_context, client=client)
            if nvidia_resp:
                await track_api_call("nvidia", success=True, client=client)
                await save_qa_pair(cleaned, nvidia_resp, client=client)
                return await _finalize(nvidia_resp)

        # 5.4 PRIORITY 4: High-Speed Concurrent Free AI Waterfall (Pollinations)
        fast_ai_resp = await query_multi_provider_ai(user_text, user_name, is_question=is_question_mode, context_history=user_context, vivid_context=vivid_context)
        if fast_ai_resp:
            await track_api_call("waterfall_free", success=True, client=client)
            await save_qa_pair(cleaned, fast_ai_resp, client=client)
            return await _finalize(fast_ai_resp)

    # =========================================================================
    # 7. AUTOMATIC DATABASE FALLBACK (WHEN ALL LIVE APIS ARE EXHAUSTED IN AUTO MODE)
    # =========================================================================
    if mode == "auto":
        asyncio.create_task(notify_owner_api_switch(
            "All Live AI APIs (Groq/Gemini/NVIDIA)",
            "Telegram Cloud & MongoDB Database",
            reason="All AI API Quotas Exhausted (HTTP 429)",
            client=client
        ))
        await track_db_fallback_call()

        # 6.1 Learned Q&A Memory Cache (Sync from Telegram Database, strictly vetted)
        cached_answer = await get_qa_answer(cleaned)
        if cached_answer and not is_toxic_or_canned_reply(cached_answer):
            return await _finalize(cached_answer)

        # 6.2 Telegram Database Saved Word-Reply Fallback (strictly vetted)
        try:
            learned = await get_chat_reply(cleaned)
            if learned and learned.get("content"):
                c = learned.get("content", "").strip()
                if c and not is_abusive(c) and not is_toxic_or_canned_reply(c):
                    return await _finalize(c)
        except Exception:
            pass

    # 6.3 Core greetings / Identity knowledge base
    for pattern, responses in GIRL_KNOWLEDGE_BASE:
        if re.search(pattern, cleaned, re.IGNORECASE):
            reply = random.choice(responses)
            return await _finalize(reply.format(user=user_name))

    # 6.4 Sentiment & Mood Detection
    sad_match = re.search(r"\b(sad|udaas|mood\s+kharab|rona\s+aa\s+raha|dil\s+toot|breakup|akelapan|depressed|koi\s+nahi\s+hai)\b", cleaned)
    if sad_match:
        sad_replies = [
            f"Arey {user_name}! 🥺 Aise udaas mat ho na please! Sab theek ho jayega, smile karo na! 🌸💖",
            f"Aww {user_name}, dil chhota mat karo yrr! Chalo baatein karo mere sath, mood achha ho jayega ✨🥰",
            f"Udaas hone ki zaroorat nahi hai {user_name}! Mai hu na baat karne ke liye, kya hua batao? 🙈🌸",
        ]
        return await _finalize(random.choice(sad_replies))

    happy_match = re.search(r"\b(pass\s+ho\s+gaya|party|khush\s+hoon|celebration|jeet\s+gaya|mazedar|good\s+news)\b", cleaned)
    if happy_match:
        happy_replies = [
            f"Yaaayyy! 🥳🎉 Bohot bohot badhai ho {user_name}! Main bohot khush hoon aapke liye! Party kab de rahe ho fir? Hehe! 💃✨",
            f"Waah waah! Kya baat hai {user_name}! Aise hi hamesha khush aur kamyab raho ji! Dher saara pyaar meri taraf se! 🌸💖",
        ]
        return await _finalize(random.choice(happy_replies))

    # 6.5 Language-adaptive fallback sweet girl conversation
    if lang == "hindi":
        fallback_res = random.choice(DEVNAGARI_FALLBACKS)
    elif lang == "telugu":
        fallback_res = random.choice(TELUGU_FALLBACKS)
    elif lang == "english":
        fallback_res = random.choice(ENGLISH_FALLBACKS)
    else:
        fallback_res = random.choice(GIRL_FALLBACK_REPLIES)

    return await _finalize(fallback_res)
