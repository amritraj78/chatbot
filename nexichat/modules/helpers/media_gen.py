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
  Ye file Voice Note (.mp3) aur AI Images (.jpg) generate karti hai:
  1. generate_voice_file(text): Google TTS endpoint se sweet girl voice note banati hai.
  2. generate_ai_image(prompt): Pollinations free AI se high-quality artwork image banati hai.
  3. Dynamic CACHE_DIR: Temp files ko ./cache me rakhti hai jise sentinel auto-clean karta hai.
================================================================================
"""

import os
import re
import uuid
import urllib.parse
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Optional

logger = logging.getLogger(__name__)

_media_session = requests.Session()
_media_adapter = HTTPAdapter(pool_connections=15, pool_maxsize=15, max_retries=Retry(total=1, backoff_factor=0.2))
_media_session.mount("https://", _media_adapter)
_media_session.mount("http://", _media_adapter)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CACHE_DIR = os.path.join(BASE_DIR, "cache")
os.makedirs(CACHE_DIR, exist_ok=True)


def clean_tts_text(text: str) -> str:
    """
    Clean and naturalize text for sweet, realistic human girl speech.
    Removes bot artifacts, links, user tags, markdown, and emojis.
    Softens punctuation and texting abbreviations so the speech flows naturally like talking into a phone mic.
    """
    if not text:
        return "Haanji, sun rahi hoon main!"
    # Strip URLs, mentions, bot markers
    t = re.sub(r"https?://\S+", "", text)
    t = re.sub(r"@\w+", "", t)
    for ch in ["*", "_", "`", "~", "#", "|", ">", "[", "]", "(", ")"]:
        t = t.replace(ch, " ")
    # Retain Latin letters, Devanagari Hindi, and essential punctuation
    t = re.sub(r"[^\w\s,\.\?\!\'\-\u0900-\u097F]", " ", t)
    # Soften harsh punctuation to natural breath pauses
    t = re.sub(r"[!]+", ", ", t)
    t = re.sub(r"\.{2,}", ", ", t)
    t = re.sub(r"\?+", "? ", t)
    # Convert texting shorthand to natural spoken words
    t = re.sub(r"\byrr\b", "yaar", t, flags=re.I)
    t = re.sub(r"\bhnn\b", "haan", t, flags=re.I)
    t = re.sub(r"\bmsg\b", "message", t, flags=re.I)
    t = re.sub(r"\bpls\b", "please", t, flags=re.I)
    words = [w for w in t.split() if w]
    cleaned = " ".join(words)
    return cleaned[:220]


def hinglish_to_hindi(text: str) -> str:
    """
    Transliterate Roman Hinglish to pure Devanagari Hindi using Google's official input tools.
    This enables Google TTS female voice to pronounce words with a 100% natural, sweet Indian girl accent!
    """
    if not text:
        return text
    # If already mostly Devanagari Hindi, keep as is
    if re.search(r"[\u0900-\u097F]", text):
        return text
    try:
        url = f"https://inputtools.google.com/request?text={urllib.parse.quote(text)}&itc=hi-t-i0-und&num=1"
        r = _media_session.get(url, timeout=3.5)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list) and len(data) > 1 and data[0] == "SUCCESS":
                translit = "".join(item[1][0] for item in data[1] if item and len(item) > 1 and item[1])
                if translit and len(translit) > 1:
                    return translit
    except Exception:
        pass
    return text


def generate_voice_file(text: str, lang: str = "hi", voice: str = "Aditi") -> Optional[str]:
    """
    Generate an audio voice file in a natural, sweet Indian girl voice (Amazon Polly Aditi/Raveena).
    Unlike robotic Google TTS, Amazon Polly Aditi is recorded by a real human Indian female voice artist.
    Uses conversational prosody (rate: 95%, pitch: +2%) so it sounds like a real girl speaking into a phone,
    not reading a script.
    """
    cleaned = clean_tts_text(text)
    if not cleaned:
        cleaned = "Haanji, boliye kya kehna chahte hain aap!"

    # 1. Primary: Natural Indian Female Voice via Amazon Polly (Aditi & Raveena)
    polly_url = "https://streamlabs.com/polly/speak"
    polly_headers = {
        "Referer": "https://streamlabs.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }

    # Wrap in gentle speech SSML for natural cadence
    ssml_text = f'<speak><prosody rate="95%" pitch="+2%">{cleaned}</prosody></speak>'

    for polly_voice in [voice, "Aditi", "Raveena"]:
        for payload_text in [ssml_text, cleaned]:
            try:
                r = _media_session.post(polly_url, headers=polly_headers, data={"text": payload_text, "voice": polly_voice}, timeout=6)
                if r.status_code == 200:
                    data = r.json()
                    if data.get("success") and data.get("speak_url"):
                        audio_r = _media_session.get(data["speak_url"], timeout=10)
                        if audio_r.status_code == 200 and len(audio_r.content) > 500:
                            file_name = f"voice_{uuid.uuid4().hex[:8]}.mp3"
                            file_path = os.path.join(CACHE_DIR, file_name)
                            with open(file_path, "wb") as f:
                                f.write(audio_r.content)
                            return file_path
            except Exception as pe:
                logger.debug(f"Polly voice ({polly_voice}) attempt: {pe}")

    # 2. Secondary Fallback: Google Transliterated Hindi TTS
    try:
        spoken_text = hinglish_to_hindi(cleaned)
        encoded_text = urllib.parse.quote(spoken_text)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded_text}&tl={lang}&client=tw-ob"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = _media_session.get(url, headers=headers, timeout=8)
        if response.status_code == 200 and len(response.content) > 500:
            file_name = f"voice_{uuid.uuid4().hex[:8]}.mp3"
            file_path = os.path.join(CACHE_DIR, file_name)
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
    except Exception as e:
        logger.error(f"Fallback TTS generation error: {e}")

    return None


def generate_ai_image(prompt: str) -> Optional[str]:
    """
    Generate an AI image using Pollinations.ai (free high-quality FLUX/SD, zero API key).
    Returns the file path of the generated .jpg image file.
    """
    if not prompt or len(prompt.strip()) < 2:
        prompt = "cute aesthetic girl holding flowers, masterpiece, 4k"

    encoded_prompt = urllib.parse.quote(prompt.strip())
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=768&height=768&nologo=true&seed={uuid.uuid4().int % 100000}"

    try:
        response = _media_session.get(url, timeout=25)
        if response.status_code == 200 and len(response.content) > 2000:
            file_name = f"image_{uuid.uuid4().hex[:8]}.jpg"
            file_path = os.path.join(CACHE_DIR, file_name)
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
    except Exception as e:
        logger.error(f"AI image generation error: {e}")

    return None
