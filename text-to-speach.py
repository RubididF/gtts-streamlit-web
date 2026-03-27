"""
Text-to-Speech Application using Streamlit

This application allows users to convert text into speech using various TTS engines.
You can personalize the voice, speed, and language of the generated speech. The application supports
multiple TTS engines, including gTTS, Edge TTS, PyHT, pyttsx3, and aitts_maker. Users can input text directly or provide a URL
to extract text from a webpage. The generated speech can be played directly in the browser or downloaded as an audio file.

Author: Rubén García Lajara
Version: 0.3
File: text-to-speach.py

"""

# ============================================================
# Import necessary libraries
# ============================================================
import streamlit as st
from gtts import gTTS
import nltk
import newspaper
import edge_tts, asyncio
from pyht import Client
from pyht.client import TTSOptions
import pyttsx3
from aitts_maker import generate_tts
from translator_button import language_selector, translate
from gtts.lang import tts_langs
from io import BytesIO
import tempfile
import uuid
import base64
import html

#============================================================
# Classes
#============================================================

class Audio:
    def __init__(self, text: str, model: str, audio_bytes: bytes):
        self.text        = text
        self.model       = model
        self.audio_bytes = audio_bytes
        self.id          = str(uuid.uuid4())
 
    @property
    def color(self):
        return MODEL_COLORS.get(self.model, MODEL_COLORS["default"])
 
    @property
    def display_text(self):
        if len(self.text) <= MAX_TEXT_CHARS:
            return self.text
        return self.text[:MAX_TEXT_CHARS] + "…"

class EdgeVoice:
    """
    Represents an edge-tts voice with all its associated information.
 
    Attributes:
        voice   (str)       : ShortName of the voice (e.g.: 'es-ES-AlvaroNeural').
        lang    (str)       : Language and region in readable text (e.g.: 'Spanish (Spain)').
        gender  (str)       : Voice gender. Expected value: 'M' or 'F'.
        styles  (list[str]) : List of available styles. Empty if it has no styles.
    """
 
    def __init__(self, voice: str, lang: str, gender: str, styles: list = None):
        self.voice  = voice
        self.lang   = lang
        self.gender = gender
        self.styles = styles if styles is not None else []
 
    # ------------------------------------------------------------------ #
    #  Convenience Properties                                             #
    # ------------------------------------------------------------------ #
 
    @property
    def locale(self) -> str:
        """Returns the BCP-47 locale extracted from the voice name (e.g.: 'es-ES')."""
        return "-".join(self.voice.split("-")[:2])
 
    @property
    def has_styles(self) -> bool:
        """True if the voice has at least one available style."""
        return bool(self.styles)
 
    @property
    def gender_label(self) -> str:
        """Returns 'Female' or 'Male' depending on gender."""
        return "Female" if self.gender.upper() == "F" else "Male"
 
    # ------------------------------------------------------------------ #
    #  Query Methods                                                      #
    # ------------------------------------------------------------------ #
 
    def supports_style(self, style: str) -> bool:
        """Returns True if the voice supports the indicated style."""
        return style in self.styles
 
    def get_style(self, style: str) -> str | None:
        """
        Returns the style if the voice supports it, or None otherwise.
        Useful to pass it directly to other methods without checking first.
        """
        return style if self.supports_style(style) else None
 
    # ------------------------------------------------------------------ #
    #  Representation                                                     #
    # ------------------------------------------------------------------ #
 
    def __str__(self) -> str:
        styles_str = ", ".join(self.styles) if self.has_styles else "No styles"
        return (
            f"Voice(\n"
            f"  voice  = {self.voice}\n"
            f"  lang   = {self.lang}\n"
            f"  locale = {self.locale}\n"
            f"  gender = {self.gender_label}\n"
            f"  styles = [{styles_str}]\n"
            f")"
        )
 
    def __repr__(self) -> str:
        return (
            f"Voice(voice={self.voice!r}, lang={self.lang!r}, "
            f"gender={self.gender!r}, styles={self.styles!r})"
        )

#=============================================================
# Constants
#=============================================================
GTTSLENGUAGES = tts_langs()  # Languages supported by gTTS
GTTS_ACCENTS: dict[str, list[dict[str, str]]] = {

    # ── Languages WITH multiple accents ────────────────────────────────

    "en": [
        {"tld": "com",    "accent": "United States"},
        {"tld": "co.uk",  "accent": "United Kingdom"},
        {"tld": "com.au", "accent": "Australia"},
        {"tld": "ca",     "accent": "Canada"},
        {"tld": "co.in",  "accent": "India"},
        {"tld": "ie",     "accent": "Ireland"},
        {"tld": "co.za",  "accent": "South Africa"},
        {"tld": "com.ng", "accent": "Nigeria"},
    ],
    "fr": [
        {"tld": "fr", "accent": "France"},
        {"tld": "ca", "accent": "Canada"},
        {"tld": "be", "accent": "Belgium"},
        {"tld": "ch", "accent": "Switzerland"},
    ],
    # fr-CA is already its own code, but also accepts TLD
    "fr-CA": [
        {"tld": "ca", "accent": "Canada"},
        {"tld": "fr", "accent": "France"},
    ],
    "es": [
        {"tld": "es",     "accent": "Spain"},
        {"tld": "com.mx", "accent": "Mexico"},
        {"tld": "com",    "accent": "Latin America (neutral)"},
        {"tld": "com.ar", "accent": "Argentina"},
        {"tld": "co",     "accent": "Colombia"},
        {"tld": "cl",     "accent": "Chile"},
    ],
    "pt": [
        {"tld": "com.br", "accent": "Brazil"},
        {"tld": "pt",     "accent": "Portugal"},
    ],
    # pt-PT is already its own code
    "pt-PT": [
        {"tld": "pt",     "accent": "Portugal"},
        {"tld": "com.br", "accent": "Brazil"},
    ],
    "de": [
        {"tld": "de", "accent": "Germany"},
        {"tld": "at", "accent": "Austria"},
        {"tld": "ch", "accent": "Switzerland"},
    ],
    "nl": [
        {"tld": "nl", "accent": "Netherlands"},
        {"tld": "be", "accent": "Belgium"},
    ],
    "it": [
        {"tld": "it", "accent": "Italy"},
        {"tld": "ch", "accent": "Switzerland"},
    ],
    "ru": [
        {"tld": "ru",  "accent": "Russia"},
        {"tld": "com", "accent": "International"},
    ],
    "zh-CN": [
        {"tld": "com",    "accent": "Mandarin (Mainland)"},
        {"tld": "com.hk", "accent": "Hong Kong"},
    ],
    "zh-TW": [
        {"tld": "com.tw", "accent": "Taiwan"},
        {"tld": "com",    "accent": "International"},
    ],
    "zh": [
        {"tld": "com",    "accent": "Mandarin"},
        {"tld": "com.hk", "accent": "Hong Kong"},
    ],
    # Cantonese (yue) — HK vs international variants
    "yue": [
        {"tld": "com.hk", "accent": "Hong Kong"},
        {"tld": "com",    "accent": "International"},
    ],

    # ── Languages with ONE single functional TLD ──────────────────────────
    # (included nonetheless so get_accents() always returns something)

    "af":  [{"tld": "com",     "accent": "Afrikaans"}],
    "am":  [{"tld": "com",     "accent": "Amharic"}],
    "ar":  [{"tld": "com",     "accent": "Arabic"}],
    "bg":  [{"tld": "com",     "accent": "Bulgarian"}],
    "bn":  [{"tld": "com",     "accent": "Bengali"}],
    "bs":  [{"tld": "com",     "accent": "Bosnian"}],
    "ca":  [{"tld": "com",     "accent": "Catalan"}],
    "cs":  [{"tld": "com",     "accent": "Czech"}],
    "cy":  [{"tld": "com",     "accent": "Welsh"}],
    "da":  [{"tld": "com",     "accent": "Danish"}],
    "el":  [{"tld": "com",     "accent": "Greek"}],
    "et":  [{"tld": "com",     "accent": "Estonian"}],
    "eu":  [{"tld": "com",     "accent": "Basque"}],
    "fi":  [{"tld": "com",     "accent": "Finnish"}],
    "gl":  [{"tld": "com",     "accent": "Galician"}],
    "gu":  [{"tld": "co.in",   "accent": "Gujarati"}],
    "ha":  [{"tld": "com",     "accent": "Hausa"}],
    "hi":  [{"tld": "co.in",   "accent": "Hindi"}],
    "hr":  [{"tld": "com",     "accent": "Croatian"}],
    "hu":  [{"tld": "com",     "accent": "Hungarian"}],
    "id":  [{"tld": "com",     "accent": "Indonesian"}],
    "is":  [{"tld": "com",     "accent": "Icelandic"}],
    "iw":  [{"tld": "com",     "accent": "Hebrew"}],
    "ja":  [{"tld": "co.jp",   "accent": "Japanese"}],
    "jw":  [{"tld": "com",     "accent": "Javanese"}],
    "km":  [{"tld": "com",     "accent": "Khmer"}],
    "kn":  [{"tld": "co.in",   "accent": "Kannada"}],
    "ko":  [{"tld": "co.kr",   "accent": "Korean"}],
    "la":  [{"tld": "com",     "accent": "Latin"}],
    "lt":  [{"tld": "com",     "accent": "Lithuanian"}],
    "lv":  [{"tld": "com",     "accent": "Latvian"}],
    "ml":  [{"tld": "co.in",   "accent": "Malayalam"}],
    "mr":  [{"tld": "co.in",   "accent": "Marathi"}],
    "ms":  [{"tld": "com",     "accent": "Malay"}],
    "my":  [{"tld": "com",     "accent": "Burmese"}],
    "ne":  [{"tld": "com",     "accent": "Nepali"}],
    "no":  [{"tld": "com",     "accent": "Norwegian"}],
    "pa":  [{"tld": "co.in",   "accent": "Punjabi"}],
    "pl":  [{"tld": "com",     "accent": "Polish"}],
    "ro":  [{"tld": "com",     "accent": "Romanian"}],
    "si":  [{"tld": "com",     "accent": "Sinhala"}],
    "sk":  [{"tld": "com",     "accent": "Slovak"}],
    "sq":  [{"tld": "com",     "accent": "Albanian"}],
    "sr":  [{"tld": "com",     "accent": "Serbian"}],
    "su":  [{"tld": "com",     "accent": "Sundanese"}],
    "sv":  [{"tld": "com",     "accent": "Swedish"}],
    "sw":  [{"tld": "com",     "accent": "Swahili"}],
    "ta":  [{"tld": "co.in",   "accent": "Tamil"}],
    "te":  [{"tld": "co.in",   "accent": "Telugu"}],
    "th":  [{"tld": "com",     "accent": "Thai"}],
    "tl":  [{"tld": "com",     "accent": "Filipino"}],
    "tr":  [{"tld": "com.tr",  "accent": "Turkish"}],
    "uk":  [{"tld": "com.ua",  "accent": "Ukrainian"}],
    "ur":  [{"tld": "com",     "accent": "Urdu"}],
    "vi":  [{"tld": "com.vn",  "accent": "Vietnamese"}],
}
MODEL_COLORS = {
    "edge": {
        "border":     "#3B82F6",
        "bg":         "rgba(59, 130, 246, 0.07)",
        "tag_bg":     "rgba(59, 130, 246, 0.15)",
        "tag_text":   "#93C5FD",
        "glow":       "rgba(59, 130, 246, 0.15)",
    },
    "pyht": {
        "border":     "#10B981",
        "bg":         "rgba(16, 185, 129, 0.07)",
        "tag_bg":     "rgba(16, 185, 129, 0.15)",
        "tag_text":   "#6EE7B7",
        "glow":       "rgba(16, 185, 129, 0.15)",
    },
    "gtts": {
        "border":     "#F59E0B",
        "bg":         "rgba(245, 158, 11, 0.07)",
        "tag_bg":     "rgba(245, 158, 11, 0.15)",
        "tag_text":   "#FCD34D",
        "glow":       "rgba(245, 158, 11, 0.15)",
    },
    "pyttsx3": {
        "border":     "#8B5CF6",
        "bg":         "rgba(139, 92, 246, 0.07)",
        "tag_bg":     "rgba(139, 92, 246, 0.15)",
        "tag_text":   "#C4B5FD",
        "glow":       "rgba(139, 92, 246, 0.15)",
    },
    "aitts": {
        "border":     "#EC4899",
        "bg":         "rgba(236, 72, 153, 0.07)",
        "tag_bg":     "rgba(236, 72, 153, 0.15)",
        "tag_text":   "#F9A8D4",
        "glow":       "rgba(236, 72, 153, 0.15)",
    },
    "default": {
        "border":     "#6B7280",
        "bg":         "rgba(107, 114, 128, 0.07)",
        "tag_bg":     "rgba(107, 114, 128, 0.15)",
        "tag_text":   "#D1D5DB",
        "glow":       "rgba(107, 114, 128, 0.15)",
    },
}
MAX_TEXT_CHARS = 130  # Maximum visible characters in the audio card
EDGE_VOICES = [
    # ── Afrikaans ──────────────────────────────────────────────────────
    EdgeVoice("af-ZA-AdriNeural",          "Afrikaans (South Africa)",        "F"),
    EdgeVoice("af-ZA-WillemNeural",        "Afrikaans (South Africa)",        "M"),
 
    # ── Albanian ───────────────────────────────────────────────────────
    EdgeVoice("sq-AL-AnilaNeural",         "Albanian (Albania)",              "F"),
    EdgeVoice("sq-AL-IlirNeural",          "Albanian (Albania)",              "M"),
 
    # ── Amharic ────────────────────────────────────────────────────────
    EdgeVoice("am-ET-MekdesNeural",        "Amharic (Ethiopia)",              "F"),
    EdgeVoice("am-ET-AmehaNeural",         "Amharic (Ethiopia)",              "M"),
 
    # ── Arabic ─────────────────────────────────────────────────────────
    EdgeVoice("ar-AE-FatimaNeural",        "Arabic (Emirates)",               "F"),
    EdgeVoice("ar-AE-HamdanNeural",        "Arabic (Emirates)",               "M"),
    EdgeVoice("ar-BH-LailaNeural",         "Arabic (Bahrain)",                "F"),
    EdgeVoice("ar-BH-AliNeural",           "Arabic (Bahrain)",                "M"),
    EdgeVoice("ar-DZ-AminaNeural",         "Arabic (Algeria)",                "F"),
    EdgeVoice("ar-DZ-IsmaelNeural",        "Arabic (Algeria)",                "M"),
    EdgeVoice("ar-EG-SalmaNeural",         "Arabic (Egypt)",                  "F"),
    EdgeVoice("ar-EG-ShakirNeural",        "Arabic (Egypt)",                  "M"),
    EdgeVoice("ar-IQ-RanaNeural",          "Arabic (Iraq)",                   "F"),
    EdgeVoice("ar-IQ-BasselNeural",        "Arabic (Iraq)",                   "M"),
    EdgeVoice("ar-JO-SanaNeural",          "Arabic (Jordan)",                 "F"),
    EdgeVoice("ar-JO-TaimNeural",          "Arabic (Jordan)",                 "M"),
    EdgeVoice("ar-KW-NouraNeural",         "Arabic (Kuwait)",                 "F"),
    EdgeVoice("ar-KW-FahedNeural",         "Arabic (Kuwait)",                 "M"),
    EdgeVoice("ar-LB-LaylaNeural",         "Arabic (Lebanon)",                "F"),
    EdgeVoice("ar-LB-RamiNeural",          "Arabic (Lebanon)",                "M"),
    EdgeVoice("ar-LY-ImanNeural",          "Arabic (Libya)",                  "F"),
    EdgeVoice("ar-LY-OmarNeural",          "Arabic (Libya)",                  "M"),
    EdgeVoice("ar-MA-MounaNeural",         "Arabic (Morocco)",                "F"),
    EdgeVoice("ar-MA-JamalNeural",         "Arabic (Morocco)",                "M"),
    EdgeVoice("ar-OM-AyshaNeural",         "Arabic (Oman)",                   "F"),
    EdgeVoice("ar-OM-AbdullahNeural",      "Arabic (Oman)",                   "M"),
    EdgeVoice("ar-QA-AmalNeural",          "Arabic (Qatar)",                  "F"),
    EdgeVoice("ar-QA-MoazNeural",          "Arabic (Qatar)",                  "M"),
    EdgeVoice("ar-SA-ZariyahNeural",       "Arabic (Saudi Arabia)",           "F"),
    EdgeVoice("ar-SA-HamedNeural",         "Arabic (Saudi Arabia)",           "M"),
    EdgeVoice("ar-SY-AmanyNeural",         "Arabic (Syria)",                  "F"),
    EdgeVoice("ar-SY-LaithNeural",         "Arabic (Syria)",                  "M"),
    EdgeVoice("ar-TN-ReemNeural",          "Arabic (Tunisia)",                "F"),
    EdgeVoice("ar-TN-HediNeural",          "Arabic (Tunisia)",                "M"),
    EdgeVoice("ar-YE-MaryamNeural",        "Arabic (Yemen)",                  "F"),
    EdgeVoice("ar-YE-SalehNeural",         "Arabic (Yemen)",                  "M"),
 
    # ── Assamese ───────────────────────────────────────────────────────
    EdgeVoice("as-IN-YashicaNeural",       "Assamese (India)",                "F"),
    EdgeVoice("as-IN-PriyomNeural",        "Assamese (India)",                "M"),
 
    # ── Azerbaijani ────────────────────────────────────────────────────
    EdgeVoice("az-AZ-BanuNeural",          "Azerbaijani",                     "F"),
    EdgeVoice("az-AZ-BabekNeural",         "Azerbaijani",                     "M"),
 
    # ── Bengali ────────────────────────────────────────────────────────
    EdgeVoice("bn-BD-NabanitaNeural",      "Bengali (Bangladesh)",            "F"),
    EdgeVoice("bn-BD-PradeepNeural",       "Bengali (Bangladesh)",            "M"),
    EdgeVoice("bn-IN-TanishaaNeural",      "Bengali (India)",                 "F"),
    EdgeVoice("bn-IN-BashkarNeural",       "Bengali (India)",                 "M"),
 
    # ── Bosnian ────────────────────────────────────────────────────────
    EdgeVoice("bs-BA-VesnaNeural",         "Bosnian",                         "F"),
    EdgeVoice("bs-BA-GoranNeural",         "Bosnian",                         "M"),
 
    # ── Bulgarian ──────────────────────────────────────────────────────
    EdgeVoice("bg-BG-KalinaNeural",        "Bulgarian",                       "F"),
    EdgeVoice("bg-BG-BorislavNeural",      "Bulgarian",                       "M"),
 
    # ── Catalan ────────────────────────────────────────────────────────
    EdgeVoice("ca-ES-JoanaNeural",         "Catalan",                         "F"),
    EdgeVoice("ca-ES-EnricNeural",         "Catalan",                         "M"),
    EdgeVoice("ca-ES-AlbaNeural",          "Catalan",                         "F"),
 
    # ── Chinese (Simplified Mandarin) ──────────────────────────────────
    EdgeVoice("zh-CN-XiaoxiaoNeural",      "Chinese (Mandarin)",              "F", [
        "newscast", "customerservice", "narration-professional",
        "newscast-casual", "chat", "assistant", "audiobook", "lyrical",
        "affectionate", "gentle", "calm", "angry", "fearful", "disgruntled",
        "serious", "cheerful", "embarrassed", "sad", "depressed", "envious",
        "whispering", "poetry-reading",
    ]),
    EdgeVoice("zh-CN-YunxiNeural",         "Chinese (Mandarin)",              "M", [
        "narration-relaxed", "embarrassed", "fearful", "cheerful",
        "disgruntled", "serious", "angry", "sad", "depressed",
        "chat", "assistant", "newscast",
    ]),
    EdgeVoice("zh-CN-YunjianNeural",       "Chinese (Mandarin)",              "M", [
        "narration-relaxed", "sports-commentary", "sports-commentary-excited",
    ]),
    EdgeVoice("zh-CN-XiaoyiNeural",        "Chinese (Mandarin)",              "F", [
        "angry", "disgruntled", "affectionate", "fearful", "sad",
        "empathetic", "cheerful", "embarrassed", "serious", "gentle",
    ]),
    EdgeVoice("zh-CN-YunyeNeural",         "Chinese (Mandarin)",              "M", [
        "embarrassed", "calm", "fearful", "disgruntled",
        "serious", "angry", "sad", "cheerful",
    ]),
    EdgeVoice("zh-CN-XiaohanNeural",       "Chinese (Mandarin)",              "F", [
        "calm", "fearful", "cheerful", "disgruntled", "serious",
        "angry", "sad", "gentle", "affectionate", "embarrassed",
    ]),
    EdgeVoice("zh-CN-XiaomoNeural",        "Chinese (Mandarin)",              "F", [
        "calm", "fearful", "cheerful", "disgruntled", "serious",
        "angry", "sad", "depressed", "affectionate", "embarrassed", "gentle",
    ]),
    EdgeVoice("zh-CN-XiaoxuanNeural",      "Chinese (Mandarin)",              "F", [
        "calm", "fearful", "cheerful", "disgruntled",
        "serious", "angry", "gentle", "depressed",
    ]),
    EdgeVoice("zh-CN-XiaoruiNeural",       "Chinese (Mandarin)",              "F", [
        "calm", "fearful", "angry", "sad",
    ]),
    EdgeVoice("zh-CN-XiaoshuangNeural",    "Chinese (Mandarin)",              "F", ["chat"]),
    EdgeVoice("zh-CN-XiaoqiuNeural",       "Chinese (Mandarin)",              "F", ["narration-professional"]),
    EdgeVoice("zh-CN-YunfengNeural",       "Chinese (Mandarin)",              "M", [
        "angry", "disgruntled", "fearful", "cheerful",
        "serious", "sad", "depressed",
    ]),
    EdgeVoice("zh-CN-YunhaoNeural",        "Chinese (Mandarin)",              "M", ["advertisement-upbeat"]),
    EdgeVoice("zh-CN-YunzeNeural",         "Chinese (Mandarin)",              "M", [
        "calm", "fearful", "angry", "sad", "disgruntled",
        "serious", "depressed", "documentary-narration",
    ]),
    EdgeVoice("zh-CN-XiaoqingNeural",      "Chinese (Mandarin)",              "F"),
    EdgeVoice("zh-CN-XiaochenNeural",      "Chinese (Mandarin)",              "F"),
    EdgeVoice("zh-CN-XiaoyanNeural",       "Chinese (Mandarin)",              "F"),
    EdgeVoice("zh-CN-XiaoningNeural",      "Chinese (Mandarin)",              "F"),
    EdgeVoice("zh-CN-XiaorongNeural",      "Chinese (Mandarin)",              "F"),
    EdgeVoice("zh-CN-YunxiaNeural",        "Chinese (Mandarin)",              "M"),
    EdgeVoice("zh-CN-YunzheNeural",        "Chinese (Mandarin)",              "M"),
 
    # ── Chinese (Hong Kong) ────────────────────────────────────────────
    EdgeVoice("zh-HK-HiuMaanNeural",       "Chinese (Hong Kong)",             "F"),
    EdgeVoice("zh-HK-WanLungNeural",       "Chinese (Hong Kong)",             "M"),
    EdgeVoice("zh-HK-HiuGaaiNeural",       "Chinese (Hong Kong)",             "F"),
 
    # ── Chinese (Taiwan) ───────────────────────────────────────────────
    EdgeVoice("zh-TW-HsiaoChenNeural",     "Chinese (Taiwan)",                "F"),
    EdgeVoice("zh-TW-YunJheNeural",        "Chinese (Taiwan)",                "M"),
    EdgeVoice("zh-TW-HsiaoYuNeural",       "Chinese (Taiwan)",                "F"),
 
    # ── Croatian ───────────────────────────────────────────────────────
    EdgeVoice("hr-HR-GabrijelaNeural",     "Croatian",                        "F"),
    EdgeVoice("hr-HR-SreckoNeural",        "Croatian",                        "M"),
 
    # ── Czech ──────────────────────────────────────────────────────────
    EdgeVoice("cs-CZ-VlastaNeural",        "Czech",                           "F"),
    EdgeVoice("cs-CZ-AntoninNeural",       "Czech",                           "M"),
 
    # ── Danish ─────────────────────────────────────────────────────────
    EdgeVoice("da-DK-ChristelNeural",      "Danish",                          "F"),
    EdgeVoice("da-DK-JeppeNeural",         "Danish",                          "M"),
 
    # ── Dutch ──────────────────────────────────────────────────────────
    EdgeVoice("nl-BE-DenaNeural",          "Dutch (Belgium)",                 "F"),
    EdgeVoice("nl-BE-ArnaudNeural",        "Dutch (Belgium)",                 "M"),
    EdgeVoice("nl-NL-ColetteNeural",       "Dutch (Netherlands)",             "F"),
    EdgeVoice("nl-NL-FennaNeural",         "Dutch (Netherlands)",             "F"),
    EdgeVoice("nl-NL-MaaikeNeural",        "Dutch (Netherlands)",             "F"),
 
    # ── English ────────────────────────────────────────────────────────
    EdgeVoice("en-AU-NatashaNeural",       "English (Australia)",             "F"),
    EdgeVoice("en-AU-WilliamNeural",       "English (Australia)",             "M"),
    EdgeVoice("en-CA-ClaraNeural",         "English (Canada)",                "F"),
    EdgeVoice("en-CA-LiamNeural",          "English (Canada)",                "M"),
    EdgeVoice("en-GB-SoniaNeural",         "English (United Kingdom)",        "F"),
    EdgeVoice("en-GB-RyanNeural",          "English (United Kingdom)",        "M"),
    EdgeVoice("en-GB-LibbyNeural",         "English (United Kingdom)",        "F"),
    EdgeVoice("en-HK-YanNeural",           "English (Hong Kong)",             "F"),
    EdgeVoice("en-HK-SamNeural",           "English (Hong Kong)",             "M"),
    EdgeVoice("en-IE-EmilyNeural",         "English (Ireland)",               "F"),
    EdgeVoice("en-IE-ConnorNeural",        "English (Ireland)",               "M"),
    EdgeVoice("en-IN-NeerjaNeural",        "English (India)",                 "F"),
    EdgeVoice("en-IN-PrabhatNeural",       "English (India)",                 "M"),
    EdgeVoice("en-KE-AsiliaNeural",        "English (Kenya)",                 "F"),
    EdgeVoice("en-KE-ChilembaNeural",      "English (Kenya)",                 "M"),
    EdgeVoice("en-NG-EzinneNeural",        "English (Nigeria)",               "F"),
    EdgeVoice("en-NG-AbeoNeural",          "English (Nigeria)",               "M"),
    EdgeVoice("en-NZ-MollyNeural",         "English (New Zealand)",           "F"),
    EdgeVoice("en-NZ-MitchellNeural",      "English (New Zealand)",           "M"),
    EdgeVoice("en-PH-RosaNeural",          "English (Philippines)",           "F"),
    EdgeVoice("en-PH-JamesNeural",         "English (Philippines)",           "M"),
    EdgeVoice("en-SG-LunaNeural",          "English (Singapore)",             "F"),
    EdgeVoice("en-SG-WayneNeural",         "English (Singapore)",             "M"),
    EdgeVoice("en-TZ-ImaniNeural",         "English (Tanzania)",              "F"),
    EdgeVoice("en-TZ-ElimuNeural",         "English (Tanzania)",              "M"),
    EdgeVoice("en-US-AriaNeural",          "English (USA)",                   "F", [
        "newscast", "chat", "customerservice", "cheerful", "empathetic",
        "angry", "sad", "excited", "friendly", "terrified",
        "shouting", "unfriendly", "whispering", "hopeful",
    ]),
    EdgeVoice("en-US-JennyNeural",         "English (USA)",                   "F", [
        "assistant", "chat", "customerservice", "newscast", "angry",
        "cheerful", "sad", "excited", "friendly", "terrified",
        "shouting", "unfriendly", "whispering", "hopeful",
    ]),
    EdgeVoice("en-US-GuyNeural",           "English (USA)",                   "M", [
        "newscast", "angry", "cheerful", "sad", "excited", "friendly",
        "terrified", "shouting", "unfriendly", "whispering", "hopeful",
    ]),
    EdgeVoice("en-US-DavisNeural",         "English (USA)",                   "M", [
        "chat", "angry", "cheerful", "excited", "friendly",
        "hopeful", "sad", "shouting", "terrified", "unfriendly", "whispering",
    ]),
    EdgeVoice("en-US-JaneNeural",          "English (USA)",                   "F", [
        "angry", "cheerful", "excited", "friendly", "hopeful",
        "sad", "shouting", "terrified", "unfriendly", "whispering",
    ]),
    EdgeVoice("en-US-JasonNeural",         "English (USA)",                   "M", [
        "angry", "cheerful", "excited", "friendly", "hopeful",
        "sad", "shouting", "terrified", "unfriendly", "whispering",
    ]),
    EdgeVoice("en-US-NancyNeural",         "English (USA)",                   "F", [
        "angry", "cheerful", "excited", "friendly", "hopeful",
        "sad", "shouting", "terrified", "unfriendly", "whispering",
    ]),
    EdgeVoice("en-US-TonyNeural",          "English (USA)",                   "M", [
        "angry", "cheerful", "excited", "friendly", "hopeful",
        "sad", "shouting", "terrified", "unfriendly", "whispering",
    ]),
    EdgeVoice("en-US-SaraNeural",          "English (USA)",                   "F", [
        "angry", "cheerful", "excited", "friendly", "hopeful",
        "sad", "shouting", "terrified", "unfriendly", "whispering",
    ]),
    EdgeVoice("en-US-AvaNeural",           "English (USA)",                   "F"),
    EdgeVoice("en-US-AndrewNeural",        "English (USA)",                   "M"),
    EdgeVoice("en-US-EmmaNeural",          "English (USA)",                   "F"),
    EdgeVoice("en-US-BrianNeural",         "English (USA)",                   "M"),
    EdgeVoice("en-US-AmberNeural",         "English (USA)",                   "F"),
    EdgeVoice("en-US-AnaNeural",           "English (USA)",                   "F"),
    EdgeVoice("en-US-AshleyNeural",        "English (USA)",                   "F"),
    EdgeVoice("en-US-BrandonNeural",       "English (USA)",                   "M"),
    EdgeVoice("en-US-ChristopherNeural",   "English (USA)",                   "M"),
    EdgeVoice("en-US-CoraNeural",          "English (USA)",                   "F"),
    EdgeVoice("en-US-ElizabethNeural",     "English (USA)",                   "F"),
    EdgeVoice("en-US-EricNeural",          "English (USA)",                   "M"),
    EdgeVoice("en-US-JacobNeural",         "English (USA)",                   "M"),
    EdgeVoice("en-US-KaiNeural",           "English (USA)",                   "M"),
    EdgeVoice("en-US-LunaNeural",          "English (USA)",                   "F"),
    EdgeVoice("en-US-MichelleNeural",      "English (USA)",                   "F"),
    EdgeVoice("en-US-MonicaNeural",        "English (USA)",                   "F"),
    EdgeVoice("en-US-RogerNeural",         "English (USA)",                   "M"),
    EdgeVoice("en-US-SteffanNeural",       "English (USA)",                   "M"),
    EdgeVoice("en-ZA-LeahNeural",          "English (South Africa)",          "F"),
    EdgeVoice("en-ZA-LukeNeural",          "English (South Africa)",          "M"),
 
    # ── Estonian ───────────────────────────────────────────────────────
    EdgeVoice("et-EE-AnuNeural",           "Estonian",                        "F"),
    EdgeVoice("et-EE-KertNeural",          "Estonian",                        "M"),
 
    # ── Filipino ───────────────────────────────────────────────────────
    EdgeVoice("fil-PH-BlessicaNeural",     "Filipino",                        "F"),
    EdgeVoice("fil-PH-AngeloNeural",       "Filipino",                        "M"),
 
    # ── Finnish ────────────────────────────────────────────────────────
    EdgeVoice("fi-FI-SelmaNeural",         "Finnish",                         "F"),
    EdgeVoice("fi-FI-NooraNeural",         "Finnish",                         "F"),
    EdgeVoice("fi-FI-HarriNeural",         "Finnish",                         "M"),
 
    # ── French ─────────────────────────────────────────────────────────
    EdgeVoice("fr-BE-CharlineNeural",      "French (Belgium)",                "F"),
    EdgeVoice("fr-BE-GerardNeural",        "French (Belgium)",                "M"),
    EdgeVoice("fr-CA-SylvieNeural",        "French (Canada)",                 "F"),
    EdgeVoice("fr-CA-JeanNeural",          "French (Canada)",                 "M"),
    EdgeVoice("fr-CA-ThierryNeural",       "French (Canada)",                 "M"),
    EdgeVoice("fr-CH-ArianeNeural",        "French (Switzerland)",            "F"),
    EdgeVoice("fr-CH-FabriceNeural",       "French (Switzerland)",            "M"),
    EdgeVoice("fr-FR-DeniseNeural",        "French (France)",                 "F"),
    EdgeVoice("fr-FR-HenriNeural",         "French (France)",                 "M"),
    EdgeVoice("fr-FR-AlainNeural",         "French (France)",                 "M"),
    EdgeVoice("fr-FR-BrigitteNeural",      "French (France)",                 "F"),
    EdgeVoice("fr-FR-CelesteNeural",       "French (France)",                 "F"),
    EdgeVoice("fr-FR-ClaudeNeural",        "French (France)",                 "M"),
    EdgeVoice("fr-FR-CoralieNeural",       "French (France)",                 "F"),
    EdgeVoice("fr-FR-EloiseNeural",        "French (France)",                 "F"),
    EdgeVoice("fr-FR-JacquelineNeural",    "French (France)",                 "F"),
    EdgeVoice("fr-FR-JeromeNeural",        "French (France)",                 "M"),
    EdgeVoice("fr-FR-JosephineNeural",     "French (France)",                 "F"),
    EdgeVoice("fr-FR-MauriceNeural",       "French (France)",                 "M"),
    EdgeVoice("fr-FR-YvesNeural",          "French (France)",                 "M"),
    EdgeVoice("fr-FR-YvetteNeural",        "French (France)",                 "F"),
 
    # ── Galician ───────────────────────────────────────────────────────
    EdgeVoice("gl-ES-SabelaNeural",        "Galician",                        "F"),
    EdgeVoice("gl-ES-RoiNeural",           "Galician",                        "M"),
 
    # ── Georgian ───────────────────────────────────────────────────────
    EdgeVoice("ka-GE-EkaNeural",           "Georgian",                        "F"),
    EdgeVoice("ka-GE-GiorgiNeural",        "Georgian",                        "M"),
 
    # ── German ─────────────────────────────────────────────────────────
    EdgeVoice("de-AT-IngridNeural",        "German (Austria)",                "F"),
    EdgeVoice("de-AT-JonasNeural",         "German (Austria)",                "M"),
    EdgeVoice("de-CH-LeniNeural",          "German (Switzerland)",            "F"),
    EdgeVoice("de-CH-JanNeural",           "German (Switzerland)",            "M"),
    EdgeVoice("de-DE-KatjaNeural",         "German (Germany)",                "F"),
    EdgeVoice("de-DE-ConradNeural",        "German (Germany)",                "M"),
    EdgeVoice("de-DE-AmalaNeural",         "German (Germany)",                "F"),
    EdgeVoice("de-DE-BerndNeural",         "German (Germany)",                "M"),
    EdgeVoice("de-DE-ChristophNeural",     "German (Germany)",                "M"),
    EdgeVoice("de-DE-ElkeNeural",          "German (Germany)",                "F"),
    EdgeVoice("de-DE-GiselaNeural",        "German (Germany)",                "F"),
    EdgeVoice("de-DE-KasperNeural",        "German (Germany)",                "M"),
    EdgeVoice("de-DE-KillianNeural",       "German (Germany)",                "M"),
    EdgeVoice("de-DE-KlarissaNeural",      "German (Germany)",                "F"),
    EdgeVoice("de-DE-KlausNeural",         "German (Germany)",                "M"),
    EdgeVoice("de-DE-LouisaNeural",        "German (Germany)",                "F"),
    EdgeVoice("de-DE-MajaNeural",          "German (Germany)",                "F"),
    EdgeVoice("de-DE-RalfNeural",          "German (Germany)",                "M"),
    EdgeVoice("de-DE-TanjaNeural",         "German (Germany)",                "F"),
 
    # ── Greek ──────────────────────────────────────────────────────────
    EdgeVoice("el-GR-AthinaNeural",        "Greek",                           "F"),
    EdgeVoice("el-GR-NestorasNeural",      "Greek",                           "M"),
 
    # ── Gujarati ───────────────────────────────────────────────────────
    EdgeVoice("gu-IN-DhwaniNeural",        "Gujarati (India)",                "F"),
    EdgeVoice("gu-IN-NiranjanNeural",      "Gujarati (India)",                "M"),
 
    # ── Hebrew ─────────────────────────────────────────────────────────
    EdgeVoice("he-IL-HilaNeural",          "Hebrew",                          "F"),
    EdgeVoice("he-IL-AvriNeural",          "Hebrew",                          "M"),
 
    # ── Hindi ──────────────────────────────────────────────────────────
    EdgeVoice("hi-IN-SwaraNeural",         "Hindi",                           "F"),
    EdgeVoice("hi-IN-MadhurNeural",        "Hindi",                           "M"),
 
    # ── Hungarian ──────────────────────────────────────────────────────
    EdgeVoice("hu-HU-NoemiNeural",         "Hungarian",                       "F"),
    EdgeVoice("hu-HU-TamasNeural",         "Hungarian",                       "M"),
 
    # ── Icelandic ──────────────────────────────────────────────────────
    EdgeVoice("is-IS-GudrunNeural",        "Icelandic",                       "F"),
    EdgeVoice("is-IS-GunnarNeural",        "Icelandic",                       "M"),
 
    # ── Indonesian ─────────────────────────────────────────────────────
    EdgeVoice("id-ID-GadisNeural",         "Indonesian",                      "F"),
    EdgeVoice("id-ID-ArdiNeural",          "Indonesian",                      "M"),
 
    # ── Irish ──────────────────────────────────────────────────────────
    EdgeVoice("ga-IE-OrlaNeural",          "Irish",                           "F"),
    EdgeVoice("ga-IE-ColmNeural",          "Irish",                           "M"),
 
    # ── Italian ────────────────────────────────────────────────────────
    EdgeVoice("it-IT-ElsaNeural",          "Italian",                         "F"),
    EdgeVoice("it-IT-IsabellaNeural",      "Italian",                         "F"),
    EdgeVoice("it-IT-DiegoNeural",         "Italian",                         "M"),
    EdgeVoice("it-IT-BenignoNeural",       "Italian",                         "M"),
    EdgeVoice("it-IT-CalimeroNeural",      "Italian",                         "M"),
    EdgeVoice("it-IT-CataldoNeural",       "Italian",                         "M"),
    EdgeVoice("it-IT-FabiolaNeural",       "Italian",                         "F"),
    EdgeVoice("it-IT-FiammaNeural",        "Italian",                         "F"),
    EdgeVoice("it-IT-GianniNeural",        "Italian",                         "M"),
    EdgeVoice("it-IT-ImeldaNeural",        "Italian",                         "F"),
    EdgeVoice("it-IT-IrmaNeural",          "Italian",                         "F"),
    EdgeVoice("it-IT-LisandroNeural",      "Italian",                         "M"),
    EdgeVoice("it-IT-PalmiraNeural",       "Italian",                         "F"),
    EdgeVoice("it-IT-PierinaNeural",       "Italian",                         "F"),
    EdgeVoice("it-IT-RinaldoNeural",       "Italian",                         "M"),
 
    # ── Japanese ───────────────────────────────────────────────────────
    EdgeVoice("ja-JP-NanamiNeural",        "Japanese",                        "F", [
        "chat", "customerservice", "cheerful",
    ]),
    EdgeVoice("ja-JP-KeitaNeural",         "Japanese",                        "M"),
 
    # ── Javanese ───────────────────────────────────────────────────────
    EdgeVoice("jv-ID-SitiNeural",          "Javanese",                        "F"),
    EdgeVoice("jv-ID-DimasNeural",         "Javanese",                        "M"),
 
    # ── Kannada ────────────────────────────────────────────────────────
    EdgeVoice("kn-IN-SapnaNeural",         "Kannada (India)",                 "F"),
    EdgeVoice("kn-IN-GaganNeural",         "Kannada (India)",                 "M"),
 
    # ── Kazakh ─────────────────────────────────────────────────────────
    EdgeVoice("kk-KZ-AigulNeural",         "Kazakh",                          "F"),
    EdgeVoice("kk-KZ-DauletNeural",        "Kazakh",                          "M"),
 
    # ── Khmer ──────────────────────────────────────────────────────────
    EdgeVoice("km-KH-SreymomNeural",       "Khmer (Cambodia)",                "F"),
    EdgeVoice("km-KH-PisethNeural",        "Khmer (Cambodia)",                "M"),
 
    # ── Korean ─────────────────────────────────────────────────────────
    EdgeVoice("ko-KR-SunHiNeural",         "Korean",                          "F"),
    EdgeVoice("ko-KR-InJoonNeural",        "Korean",                          "M", [
        "cheerful", "sad",
    ]),
 
    # ── Lao ────────────────────────────────────────────────────────────
    EdgeVoice("lo-LA-KeomanyNeural",       "Lao",                             "F"),
    EdgeVoice("lo-LA-ChanthavongNeural",   "Lao",                             "M"),
 
    # ── Latvian ────────────────────────────────────────────────────────
    EdgeVoice("lv-LV-EveritaNeural",       "Latvian",                         "F"),
    EdgeVoice("lv-LV-NilsNeural",          "Latvian",                         "M"),
 
    # ── Lithuanian ─────────────────────────────────────────────────────
    EdgeVoice("lt-LT-OnaNeural",           "Lithuanian",                      "F"),
    EdgeVoice("lt-LT-LeonasNeural",        "Lithuanian",                      "M"),
 
    # ── Macedonian ─────────────────────────────────────────────────────
    EdgeVoice("mk-MK-MarijaNeural",        "Macedonian",                      "F"),
    EdgeVoice("mk-MK-AleksandarNeural",    "Macedonian",                      "M"),
 
    # ── Malay ──────────────────────────────────────────────────────────
    EdgeVoice("ms-MY-YasminNeural",        "Malay",                           "F"),
    EdgeVoice("ms-MY-OsmanNeural",         "Malay",                           "M"),
 
    # ── Malayalam ──────────────────────────────────────────────────────
    EdgeVoice("ml-IN-SobhanaNeural",       "Malayalam (India)",               "F"),
    EdgeVoice("ml-IN-MidhunNeural",        "Malayalam (India)",               "M"),
 
    # ── Maltese ────────────────────────────────────────────────────────
    EdgeVoice("mt-MT-GraceNeural",         "Maltese",                         "F"),
    EdgeVoice("mt-MT-JosephNeural",        "Maltese",                         "M"),
 
    # ── Marathi ────────────────────────────────────────────────────────
    EdgeVoice("mr-IN-AarohiNeural",        "Marathi (India)",                 "F"),
    EdgeVoice("mr-IN-ManoharNeural",       "Marathi (India)",                 "M"),
 
    # ── Mongolian ──────────────────────────────────────────────────────
    EdgeVoice("mn-MN-YesuiNeural",         "Mongolian",                       "F"),
    EdgeVoice("mn-MN-BataaNeural",         "Mongolian",                       "M"),
 
    # ── Burmese ────────────────────────────────────────────────────────
    EdgeVoice("my-MM-NilarNeural",         "Burmese (Myanmar)",               "F"),
    EdgeVoice("my-MM-ThihaNeural",         "Burmese (Myanmar)",               "M"),
 
    # ── Nepali ─────────────────────────────────────────────────────────
    EdgeVoice("ne-NP-HemkalaNeural",       "Nepali",                          "F"),
    EdgeVoice("ne-NP-SagarNeural",         "Nepali",                          "M"),
 
    # ── Norwegian ──────────────────────────────────────────────────────
    EdgeVoice("nb-NO-PernilleNeural",      "Norwegian",                       "F"),
    EdgeVoice("nb-NO-FinnNeural",          "Norwegian",                       "M"),
    EdgeVoice("nb-NO-IselinNeural",        "Norwegian",                       "F"),
 
    # ── Pashto ────────────────────────────────────────────────────────
    EdgeVoice("ps-AF-LatifaNeural",        "Pashto (Afghanistan)",            "F"),
    EdgeVoice("ps-AF-GulNawazNeural",      "Pashto (Afghanistan)",            "M"),
 
    # ── Persian ────────────────────────────────────────────────────────
    EdgeVoice("fa-IR-DilaraNeural",        "Persian (Iran)",                  "F"),
    EdgeVoice("fa-IR-FaridNeural",         "Persian (Iran)",                  "M"),
 
    # ── Polish ─────────────────────────────────────────────────────────
    EdgeVoice("pl-PL-ZofiaNeural",         "Polish",                          "F"),
    EdgeVoice("pl-PL-AgnieszkaNeural",     "Polish",                          "F"),
    EdgeVoice("pl-PL-MarekNeural",         "Polish",                          "M"),
 
    # ── Portuguese ─────────────────────────────────────────────────────
    EdgeVoice("pt-BR-FranciscaNeural",     "Portuguese (Brazil)",             "F", ["calm"]),
    EdgeVoice("pt-BR-AntonioNeural",       "Portuguese (Brazil)",             "M"),
    EdgeVoice("pt-BR-BrendaNeural",        "Portuguese (Brazil)",             "F"),
    EdgeVoice("pt-BR-DonatoNeural",        "Portuguese (Brazil)",             "M"),
    EdgeVoice("pt-BR-ElzaNeural",          "Portuguese (Brazil)",             "F"),
    EdgeVoice("pt-BR-FabioNeural",         "Portuguese (Brazil)",             "M"),
    EdgeVoice("pt-BR-GiovannaNeural",      "Portuguese (Brazil)",             "F"),
    EdgeVoice("pt-BR-HumbertoNeural",      "Portuguese (Brazil)",             "M"),
    EdgeVoice("pt-BR-JulioNeural",         "Portuguese (Brazil)",             "M"),
    EdgeVoice("pt-BR-LeiticiaNeural",      "Portuguese (Brazil)",             "F"),
    EdgeVoice("pt-BR-ManuelaNeural",       "Portuguese (Brazil)",             "F"),
    EdgeVoice("pt-BR-NicolauNeural",       "Portuguese (Brazil)",             "M"),
    EdgeVoice("pt-BR-ValerioNeural",       "Portuguese (Brazil)",             "M"),
    EdgeVoice("pt-BR-YaraNeural",          "Portuguese (Brazil)",             "F"),
    EdgeVoice("pt-PT-RaquelNeural",        "Portuguese (Portugal)",           "F"),
    EdgeVoice("pt-PT-DuarteNeural",        "Portuguese (Portugal)",           "M"),
    EdgeVoice("pt-PT-FernandaNeural",      "Portuguese (Portugal)",           "F"),
 
    # ── Romanian ───────────────────────────────────────────────────────
    EdgeVoice("ro-RO-AlinaNeural",         "Romanian",                        "F"),
    EdgeVoice("ro-RO-EmilNeural",          "Romanian",                        "M"),
 
    # ── Russian ────────────────────────────────────────────────────────
    EdgeVoice("ru-RU-SvetlanaNeural",      "Russian",                         "F"),
    EdgeVoice("ru-RU-DmitryNeural",        "Russian",                         "M"),
    EdgeVoice("ru-RU-DariyaNeural",        "Russian",                         "F"),
 
    # ── Serbian ────────────────────────────────────────────────────────
    EdgeVoice("sr-RS-SophieNeural",        "Serbian",                         "F"),
    EdgeVoice("sr-RS-NicholasNeural",      "Serbian",                         "M"),
 
    # ── Sinhala ────────────────────────────────────────────────────────
    EdgeVoice("si-LK-ThiliniNeural",       "Sinhala (Sri Lanka)",             "F"),
    EdgeVoice("si-LK-SameeraNeural",       "Sinhala (Sri Lanka)",             "M"),
 
    # ── Slovak ─────────────────────────────────────────────────────────
    EdgeVoice("sk-SK-ViktoriaNeural",      "Slovak",                          "F"),
    EdgeVoice("sk-SK-LukasNeural",         "Slovak",                          "M"),
 
    # ── Slovenian ──────────────────────────────────────────────────────
    EdgeVoice("sl-SI-PetraNeural",         "Slovenian",                       "F"),
    EdgeVoice("sl-SI-RokNeural",           "Slovenian",                       "M"),
 
    # ── Somali ─────────────────────────────────────────────────────────
    EdgeVoice("so-SO-UbaxNeural",          "Somali",                          "F"),
    EdgeVoice("so-SO-MuuseNeural",         "Somali",                          "M"),
 
    # ── Spanish ────────────────────────────────────────────────────────
    EdgeVoice("es-AR-ElenaNeural",         "Spanish (Argentina)",             "F"),
    EdgeVoice("es-AR-TomasNeural",         "Spanish (Argentina)",             "M"),
    EdgeVoice("es-BO-SofiaNeural",         "Spanish (Bolivia)",               "F"),
    EdgeVoice("es-BO-MarceloNeural",       "Spanish (Bolivia)",               "M"),
    EdgeVoice("es-CL-CatalinaNeural",      "Spanish (Chile)",                 "F"),
    EdgeVoice("es-CL-LorenzoNeural",       "Spanish (Chile)",                 "M"),
    EdgeVoice("es-CO-SalomeNeural",        "Spanish (Colombia)",              "F"),
    EdgeVoice("es-CO-GonzaloNeural",       "Spanish (Colombia)",              "M"),
    EdgeVoice("es-CR-MariaNeural",         "Spanish (Costa Rica)",            "F"),
    EdgeVoice("es-CR-JuanNeural",          "Spanish (Costa Rica)",            "M"),
    EdgeVoice("es-CU-BelkysNeural",        "Spanish (Cuba)",                  "F"),
    EdgeVoice("es-CU-ManuelNeural",        "Spanish (Cuba)",                  "M"),
    EdgeVoice("es-DO-RamonaNeural",        "Spanish (Dominican Republic)",    "F"),
    EdgeVoice("es-DO-EmilioNeural",        "Spanish (Dominican Republic)",    "M"),
    EdgeVoice("es-EC-AndreaNeural",        "Spanish (Ecuador)",               "F"),
    EdgeVoice("es-EC-LuisNeural",          "Spanish (Ecuador)",               "M"),
    EdgeVoice("es-ES-ElviraNeural",        "Spanish (Spain)",                 "F"),
    EdgeVoice("es-ES-AlvaroNeural",        "Spanish (Spain)",                 "M"),
    EdgeVoice("es-ES-AbrilNeural",         "Spanish (Spain)",                 "F"),
    EdgeVoice("es-ES-ArnauNeural",         "Spanish (Spain)",                 "M"),
    EdgeVoice("es-ES-DarioNeural",         "Spanish (Spain)",                 "M"),
    EdgeVoice("es-ES-EliasNeural",         "Spanish (Spain)",                 "M"),
    EdgeVoice("es-ES-EstrellaNeural",      "Spanish (Spain)",                 "F"),
    EdgeVoice("es-ES-IreneNeural",         "Spanish (Spain)",                 "F"),
    EdgeVoice("es-ES-LaiaNeural",          "Spanish (Spain)",                 "F"),
    EdgeVoice("es-ES-LiaNeural",           "Spanish (Spain)",                 "F"),
    EdgeVoice("es-ES-NilNeural",           "Spanish (Spain)",                 "M"),
    EdgeVoice("es-ES-SaulNeural",          "Spanish (Spain)",                 "M"),
    EdgeVoice("es-ES-TeoNeural",           "Spanish (Spain)",                 "M"),
    EdgeVoice("es-ES-TrianaNeural",        "Spanish (Spain)",                 "F"),
    EdgeVoice("es-ES-VeraNeural",          "Spanish (Spain)",                 "F"),
    EdgeVoice("es-ES-XimenaNeural",        "Spanish (Spain)",                 "F"),
    EdgeVoice("es-GQ-TeresitaNeural",      "Spanish (Equatorial Guinea)",     "F"),
    EdgeVoice("es-GQ-JavierNeural",        "Spanish (Equatorial Guinea)",     "M"),
    EdgeVoice("es-GT-MartaNeural",         "Spanish (Guatemala)",             "F"),
    EdgeVoice("es-GT-AndresNeural",        "Spanish (Guatemala)",             "M"),
    EdgeVoice("es-HN-KarlaNeural",         "Spanish (Honduras)",              "F"),
    EdgeVoice("es-HN-CarlosNeural",        "Spanish (Honduras)",              "M"),
    EdgeVoice("es-MX-DaliaNeural",         "Spanish (Mexico)",                "F"),
    EdgeVoice("es-MX-JorgeNeural",         "Spanish (Mexico)",                "M"),
    EdgeVoice("es-MX-BeatrizNeural",       "Spanish (Mexico)",                "F"),
    EdgeVoice("es-MX-CandelaNeural",       "Spanish (Mexico)",                "F"),
    EdgeVoice("es-MX-CarlotaNeural",       "Spanish (Mexico)",                "F"),
    EdgeVoice("es-MX-CecilioNeural",       "Spanish (Mexico)",                "M"),
    EdgeVoice("es-MX-GerardoNeural",       "Spanish (Mexico)",                "M"),
    EdgeVoice("es-MX-LarissaNeural",       "Spanish (Mexico)",                "F"),
    EdgeVoice("es-MX-LibertoNeural",       "Spanish (Mexico)",                "M"),
    EdgeVoice("es-MX-LucianoNeural",       "Spanish (Mexico)",                "M"),
    EdgeVoice("es-MX-MarinaNeural",        "Spanish (Mexico)",                "F"),
    EdgeVoice("es-MX-NuriaNeural",         "Spanish (Mexico)",                "F"),
    EdgeVoice("es-MX-PelayoNeural",        "Spanish (Mexico)",                "M"),
    EdgeVoice("es-MX-RenataNeural",        "Spanish (Mexico)",                "F"),
    EdgeVoice("es-MX-YagoNeural",          "Spanish (Mexico)",                "M"),
    EdgeVoice("es-NI-YolandaNeural",       "Spanish (Nicaragua)",             "F"),
    EdgeVoice("es-NI-FedericoNeural",      "Spanish (Nicaragua)",             "M"),
    EdgeVoice("es-PA-MargaritaNeural",     "Spanish (Panama)",                "F"),
    EdgeVoice("es-PA-RobertoNeural",       "Spanish (Panama)",                "M"),
    EdgeVoice("es-PE-CamilaNeural",        "Spanish (Peru)",                  "F"),
    EdgeVoice("es-PE-AlexNeural",          "Spanish (Peru)",                  "M"),
    EdgeVoice("es-PR-KarinaNeural",        "Spanish (Puerto Rico)",           "F"),
    EdgeVoice("es-PR-VictorNeural",        "Spanish (Puerto Rico)",           "M"),
    EdgeVoice("es-PY-TaniaNeural",         "Spanish (Paraguay)",              "F"),
    EdgeVoice("es-PY-MarioNeural",         "Spanish (Paraguay)",              "M"),
    EdgeVoice("es-SV-LorenaNeural",        "Spanish (El Salvador)",           "F"),
    EdgeVoice("es-SV-RodrigoNeural",       "Spanish (El Salvador)",           "M"),
    EdgeVoice("es-US-PalomaNeural",        "Spanish (USA)",                   "F"),
    EdgeVoice("es-US-AlonsoNeural",        "Spanish (USA)",                   "M"),
    EdgeVoice("es-UY-ValentinaNeural",     "Spanish (Uruguay)",               "F"),
    EdgeVoice("es-UY-MateoNeural",         "Spanish (Uruguay)",               "M"),
    EdgeVoice("es-VE-PaolaNeural",         "Spanish (Venezuela)",             "F"),
    EdgeVoice("es-VE-SebastianNeural",     "Spanish (Venezuela)",             "M"),
 
    # ── Swahili ────────────────────────────────────────────────────────
    EdgeVoice("sw-KE-ZuriNeural",          "Swahili (Kenya)",                 "F"),
    EdgeVoice("sw-KE-RafikiNeural",        "Swahili (Kenya)",                 "M"),
    EdgeVoice("sw-TZ-RehemaNeural",        "Swahili (Tanzania)",              "F"),
    EdgeVoice("sw-TZ-DaudiNeural",         "Swahili (Tanzania)",              "M"),
 
    # ── Swedish ────────────────────────────────────────────────────────
    EdgeVoice("sv-SE-SofieNeural",         "Swedish",                         "F"),
    EdgeVoice("sv-SE-HilleviNeural",       "Swedish",                         "F"),
    EdgeVoice("sv-SE-MattiasNeural",       "Swedish",                         "M"),
 
    # ── Tamil ──────────────────────────────────────────────────────────
    EdgeVoice("ta-IN-PallaviNeural",       "Tamil (India)",                   "F"),
    EdgeVoice("ta-IN-ValluvarNeural",      "Tamil (India)",                   "M"),
    EdgeVoice("ta-LK-SaranyaNeural",       "Tamil (Sri Lanka)",               "F"),
    EdgeVoice("ta-LK-KumarNeural",         "Tamil (Sri Lanka)",               "M"),
    EdgeVoice("ta-MY-KaniNeural",          "Tamil (Malaysia)",                "F"),
    EdgeVoice("ta-MY-SuryaNeural",         "Tamil (Malaysia)",                "M"),
    EdgeVoice("ta-SG-VenbaNeural",         "Tamil (Singapore)",               "F"),
    EdgeVoice("ta-SG-AnbuNeural",          "Tamil (Singapore)",               "M"),
 
    # ── Telugu ─────────────────────────────────────────────────────────
    EdgeVoice("te-IN-ShrutiNeural",        "Telugu (India)",                  "F"),
    EdgeVoice("te-IN-MohanNeural",         "Telugu (India)",                  "M"),
 
    # ── Thai ───────────────────────────────────────────────────────────
    EdgeVoice("th-TH-PremwadeeNeural",     "Thai",                            "F"),
    EdgeVoice("th-TH-AcharaNeural",        "Thai",                            "F"),
    EdgeVoice("th-TH-NiwatNeural",         "Thai",                            "M"),
 
    # ── Turkish ────────────────────────────────────────────────────────
    EdgeVoice("tr-TR-EmelNeural",          "Turkish",                         "F"),
    EdgeVoice("tr-TR-AhmetNeural",         "Turkish",                         "M"),
 
    # ── Ukrainian ──────────────────────────────────────────────────────
    EdgeVoice("uk-UA-PolinaNeural",        "Ukrainian",                       "F"),
    EdgeVoice("uk-UA-OstapNeural",         "Ukrainian",                       "M"),
 
    # ── Urdu ───────────────────────────────────────────────────────────
    EdgeVoice("ur-IN-GulNeural",           "Urdu (India)",                    "F"),
    EdgeVoice("ur-IN-SalmanNeural",        "Urdu (India)",                    "M"),
    EdgeVoice("ur-PK-UzmaNeural",          "Urdu (Pakistan)",                 "F"),
    EdgeVoice("ur-PK-AsadNeural",          "Urdu (Pakistan)",                 "M"),
 
    # ── Uzbek ──────────────────────────────────────────────────────────
    EdgeVoice("uz-UZ-MadinaNeural",        "Uzbek",                           "F"),
    EdgeVoice("uz-UZ-SardorNeural",        "Uzbek",                           "M"),
 
    # ── Vietnamese ─────────────────────────────────────────────────────
    EdgeVoice("vi-VN-HoaiMyNeural",        "Vietnamese",                      "F"),
    EdgeVoice("vi-VN-NamMinhNeural",       "Vietnamese",                      "M"),
 
    # ── Welsh ──────────────────────────────────────────────────────────
    EdgeVoice("cy-GB-NiaNeural",           "Welsh",                           "F"),
    EdgeVoice("cy-GB-AledNeural",          "Welsh",                           "M"),
 
    # ── Zulu ───────────────────────────────────────────────────────────
    EdgeVoice("zu-ZA-ThandoNeural",        "Zulu (South Africa)",             "F"),
    EdgeVoice("zu-ZA-ThembaNeural",        "Zulu (South Africa)",             "M"),
]

#============================================================
# Global CSS
#============================================================

def inject_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,600;1,400&family=Syne:wght@400;600;700&display=swap');
 
        /* Dark Background */
        .stApp {
            background: #0F1117;
            font-family: 'Syne', sans-serif;
        }
 
        /* Hide Streamlit decorations */
        #MainMenu, footer, header { visibility: hidden; }
 
        /* Titles */
        h1, h2, h3 {
            font-family: 'Syne', sans-serif !important;
            color: #F1F5F9 !important;
        }
 
        /* Delete button — styled in card HTML */
        .audio-card-wrapper {
            margin-bottom: 16px;
            animation: fadeIn 0.35s ease;
        }
 
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to   { opacity: 1; transform: translateY(0); }
        }
 
        /* Streamlit audio player adjustment */
        audio {
            width: 100% !important;
            border-radius: 8px;
            margin-top: 4px;
        }
 
        /* Card number in corner */
        .card-number {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            opacity: 0.4;
            position: absolute;
            top: 10px;
            right: 14px;
        }
        
        
}       
    </style>
    """, unsafe_allow_html=True)

#============================================================
# gTTS Functions
#============================================================

def gtts_get_accents(language_code: str) -> list[dict[str, str]]:
    """
    Returns available accents for the given language code.

    Args:
        language_code: ISO language code (e.g. 'en', 'es', 'fr').

    Returns:
        List of dicts with keys 'tld' and 'accent'.
        If the language has no registered accents, returns default TLD 'com'.

    Raises:
        ValueError: If the language code is not valid for gTTS.
    """
    if language_code not in GTTSLENGUAGES:
        supported = ", ".join(sorted(GTTSLENGUAGES.keys()))
        raise ValueError(
            f"Language '{language_code}' not supported by gTTS. "
            f"Available languages: {supported}"
        )

    return GTTS_ACCENTS.get(
        language_code,
        [{"tld": "com", "accent": "Standard"}],  # fallback for languages without variants
    )

def gtts_has_accents(language_code: str) -> bool:
    """Returns True if the language has more than one accent variant."""
    return len(GTTS_ACCENTS.get(language_code, [])) > 1

#============================================================
# Edge TTS Functions
#============================================================

def get_voice_by_id(voice_id: str) -> EdgeVoice | None:
    """Returns the Voice object whose voice attribute matches exactly."""
    for v in EDGE_VOICES:
        if v.voice == voice_id:
            return v
    return None
 
 
def get_voices_by_locale(locale: str) -> list[EdgeVoice]:
    """Returns all voices whose BCP-47 locale matches (e.g.: 'es-ES')."""
    return [v for v in EDGE_VOICES if v.locale == locale]
 
 
def get_voices_with_styles() -> list[EdgeVoice]:
    """Returns only voices that have at least one style."""
    return [v for v in EDGE_VOICES if v.has_styles]
 
 
def get_voices_by_gender(gender: str) -> list[EdgeVoice]:
    """Returns voices filtered by gender ('M' or 'F')."""
    return [v for v in EDGE_VOICES if v.gender.upper() == gender.upper()]

def get_lenguages_with_voices() -> list[str]:
    """Returns a list of unique languages available in the EDGE voices.
    splits duplicates and preserves order.
    the format is: "Lenguage (Region)" if region is specified, otherwise just "Language"
    the list, removes de Regions and duplicates, so it only returns the unique languages, without regions.
    For example, if there are voices for "English (United States)", "English (United Kingdom)", and "Spanish (Spain)",
    the function will return ["English", "Spanish"].
    """
    seen = set()
    languages = []
    for v in EDGE_VOICES:
        edge_language = v.lang.split(" (")[0]  # Get the part before " (" to remove region
        if edge_language not in seen:
            seen.add(edge_language)
            languages.append(edge_language)
    return languages

edge_lenguages = get_lenguages_with_voices()
#================================================================
# Processing Functions - Text extraction
#================================================================

def extract_text_from_url(url: str) -> str:
    """Extracts the main text from a webpage given its URL."""
    try:
        article = newspaper.Article(url)
        article.download()
        article.parse()
        return article.text
    except Exception as e:
        st.error(translate("Error extracting text from URL:", lang) + f" {e}")
        return ""

#============================================================
# Audio Management - List to store generated audio objects, function to create audio objects and manage them
#============================================================

def render_card(audio: Audio, index: int):
    c = audio.color

    st.markdown(f"""<div class="audio-card-wrapper"><div style="position:relative;border:1.5px solid {c['border']};border-radius:14px;padding:16px 18px 12px 18px;background:{c['bg']};box-shadow:0 0 18px {c['glow']},0 2px 8px rgba(0,0,0,0.3);"><span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;opacity:0.4;position:absolute;top:10px;right:14px;">#{index + 1}</span><div style="margin-bottom:10px;"><span style="background:{c['tag_bg']};color:{c['tag_text']};border:1px solid {c['border']};border-radius:20px;padding:2px 10px;font-size:0.7rem;font-family:'JetBrains Mono',monospace;font-weight:600;letter-spacing:0.06em;text-transform:uppercase;">⬡ {audio.model}</span></div><p style="font-style:italic;color:rgba(200,210,230,0.45);font-size:0.85rem;font-family:'JetBrains Mono',monospace;line-height:1.5;margin:0 0 10px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">&ldquo;{audio.display_text}&rdquo;</p></div></div>""", unsafe_allow_html=True)

    st.audio(audio.audio_bytes, format="audio/mp3")

    if st.button("🗑️", key=f"del_{audio.id}", use_container_width=True):
        st.session_state.audios.pop(index)
        st.rerun()

def render_audio_grid(lang: str = "en"):
    audios = st.session_state.audios
    if not audios:
        msg = translate("No audio generated yet.", lang)
        st.markdown(f"""<div style="text-align:center;padding:40px;color:rgba(150,160,180,0.35);font-style:italic;">{msg}</div>""", unsafe_allow_html=True)
        return

    n = len(audios)
    label_audio   = translate("audio", lang)
    label_audios  = translate("audios", lang)
    label_generado  = translate("generated", lang)
    label_generados = translate("generated", lang)

    st.markdown(f"""<p style="color:rgba(150,160,180,0.5);font-size:0.8rem;font-family:'JetBrains Mono',monospace;margin-bottom:12px;">{n} {label_audios if n != 1 else label_audio} {label_generados if n != 1 else label_generado}</p>""", unsafe_allow_html=True)

    # Groups of 4 cards per row
    for row_start in range(0, n, 4):
        row_audios = audios[row_start : row_start + 4]
        cols = st.columns(len(row_audios))
        for col, (audio, abs_index) in zip(cols, [(a, row_start + i) for i, a in enumerate(row_audios)]):
            with col:
                render_card(audio, abs_index)

#============================================================
# Initialize Session State Variables
#============================================================

if 'speech_model' not in st.session_state:
    st.session_state.speech_model = "gtts"  # Default model for new sessions

if 'audios' not in st.session_state:
    st.session_state.audios = []  # List to store generated audio objects

if 'text_mode' not in st.session_state:
    st.session_state.text_mode = "text"  # Default input mode

#============================================================
# Language Selection
#============================================================

lang = language_selector(default_lang="en") # Language selector, default English
st.write(translate("Select Language for the website", lang))

#============================================================
# Title Area
#============================================================

# Title and description
st.title(translate("Text-to-Speech Application",lang))
st.markdown(translate("🎙️ **This application allows you to convert text into speech** using various *TTS engines*." ,lang))
st.markdown(translate("🎛️ You can personalize the **__voice__**, **__speed__**, and **__language__** of the generated speech." ,lang))
st.markdown(translate("🧠 The application supports multiple *TTS engines*, including **gTTS**, **Edge TTS**, **PyHT**, **pyttsx3**, and **aitts_maker**." ,lang))
st.markdown(translate("✍️ You can **input text directly** or provide a *URL* to extract text from a webpage." ,lang))
st.markdown(translate("🔊 The generated speech can be **played directly in the browser** or **downloaded as an audio file**.",lang))

#============================================================
# Audio Area
#============================================================

st.subheader(translate("Generated Audios", lang))

# Initialize audio list in session state if it doesn't exist
if "audios" not in st.session_state:
    st.session_state.audios = []

render_audio_grid(lang)

#============================================================
# Text Area - Text Input / URL Input
#============================================================

tab_text, tab_url = st.tabs([translate("Plain text",lang), translate("URL",lang)])

with tab_text:
    st.session_state.text_mode = "text"
    text_input = st.text_area(translate("Enter your text:",lang))
with tab_url:
    st.session_state.text_mode = "url"
    url_input = st.text_input(translate("Enter the URL:",lang))

#============================================================
# Processing Area - Select TTS Engine and its parameters
#============================================================
st.subheader(translate("Select TTS Engine and Parameters",lang))
tab_gtts, tab_edge, tab_pyht, tab_pyttsx3, tab_aitts = st.tabs(["gTTS", "Edge TTS", "PyHT", "pyttsx3", "aitts_maker"])
with tab_gtts:
    st.markdown(translate("### gTTS Parameters",lang))
    st.session_state.speech_model = "gtts"
    gtts_lang = st.selectbox(
        translate("Select language for gTTS:", lang),
        options=list(GTTSLENGUAGES.keys()),
        index=list(GTTSLENGUAGES.keys()).index(lang),
        format_func=lambda x: translate(GTTSLENGUAGES[x], lang).capitalize())
    gtts_slow = st.checkbox(translate("Slow speed",lang), value=False)
    gtts_options = gtts_get_accents(gtts_lang)
    gtts_tld = st.selectbox(translate("Select TLD for gTTS:",lang),
            options=[accent["tld"] for accent in gtts_options], index=0,
            format_func=lambda tld: translate(next(accent["accent"] for accent in gtts_options if accent["tld"] == tld), lang).capitalize())
with tab_edge:
    st.markdown(translate("### Edge TTS Parameters",lang))
    st.session_state.speech_model = "edge"
    edge_1, edge_2 = st.columns(2)
    with edge_1:
        edge_rate = st.slider(translate("Speech rate for Edge TTS:", lang), min_value=-100, max_value=200, value=0)
        edge_volume = st.slider(translate("Volume for Edge TTS:", lang), min_value=-100, max_value=100, value=0)
        edge_pitch = st.slider(translate("Pitch for Edge TTS:", lang), min_value=-100, max_value=100, value=0)
    with edge_2:
        edge_lenguage = st.selectbox(translate("Select language for Edge TTS:", lang),
            options= edge_lenguages,
            index=0,
            format_func=lambda l: translate(l, lang))
        edge_gender = st.selectbox(translate("Select gender for Edge TTS:", lang), options=["All","F", "M"], index=0, format_func=lambda g: translate("All" if g == "All" else ("Female" if g == "F" else "Male"), lang))
        edge_option_voices = [v for v in EDGE_VOICES if v.lang == edge_lenguage and (edge_gender == "All" or v.gender == edge_gender)]
        edge_voice = st.selectbox(translate("Select voice for Edge TTS:", lang), options=edge_option_voices, format_func=lambda v: f"{translate(v.voice, lang)} ({translate('Female' if v.gender == 'F' else 'Male', lang)})")
with tab_pyht:
    st.markdown(translate("### PyHT Parameters",lang))
    st.session_state.speech_model = "pyht"
with tab_pyttsx3:
    st.markdown(translate("### pyttsx3 Parameters",lang))
    st.session_state.speech_model = "pyttsx3"
with tab_aitts: 
    st.markdown(translate("### aitts_maker Parameters",lang))
    st.session_state.speech_model = "aitts"

#============================================================
# Process Button - Generate TTS
#============================================================

generate_button = st.button(translate("Generate Speech",lang))
if generate_button:
    
    if st.session_state.text_mode == "url":
        if not url_input.strip():
            st.error(translate("Please enter a URL.", lang))
            st.stop()
        text_input = extract_text_from_url(url_input)
        if not text_input.strip():
            st.error(translate("No text could be extracted from the provided URL.", lang))
            st.stop()
    if st.session_state.text_mode == "text" and not text_input.strip():
        st.error(translate("Please enter some text to convert to speech.", lang))
        st.stop()
    if st.session_state.speech_model == "gtts":
        tts = gTTS(text=text_input, lang=gtts_lang, slow=gtts_slow, tld=gtts_tld)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
    if st.session_state.speech_model == "edge":
        edge_voice_id = edge_voice.voice
        audio_bytes = edge_tts.Communicate(text_input, edge_voice_id, edge_rate, edge_volume, edge_pitch)
        audio_buffer = BytesIO(audio_bytes)
    new_audio = Audio(
        text=text_input,
        model=st.session_state.get("speech_model", "gtts"),       
        audio_bytes=audio_buffer.getvalue()
    )
    st.session_state.audios.append(new_audio)
    st.rerun()