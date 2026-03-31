from gtts.lang import tts_langs
import streamlit as st
from gtts import gTTS
t = st.session_state.get("t", {})  # Shortcut to access translations

# ============================================================
# gTTS Constants
# ============================================================

GTTS_LANGUAGES = tts_langs()  # Languages supported by gTTS
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

# ============================================================
# gTTS Functions
# ============================================================

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
    if language_code not in GTTS_LANGUAGES:
        supported = ", ".join(sorted(GTTS_LANGUAGES.keys()))
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

# ============================================================
# Parameters for gTTS generation
# ============================================================

def gtts_streamlit_params(lang: str):
    """Returns Streamlit input parameters for gTTS based on the selected language."""
    index_gtts = 0
    if lang in GTTS_LANGUAGES:
        index_gtts = list(GTTS_LANGUAGES.keys()).index(lang)
    gtts_lang = st.selectbox(
        t["gtts_select_lang"],
        options=list(GTTS_LANGUAGES.keys()),
        index=index_gtts,
        format_func=lambda x: t[GTTS_LANGUAGES[x]].capitalize())

    gtts_slow = st.checkbox(t["gtts_slow_speed"], value=False)
    gtts_options = gtts_get_accents(gtts_lang)
    gtts_tld = st.selectbox(
        t["gtts_select_tld"],
        options=[accent["tld"] for accent in gtts_options],
        index=0,
        format_func=lambda tld: t[tld].capitalize())
    return gtts_lang, gtts_slow, gtts_tld

# ============================================================
# gTTS Text-to-Speech Generation
# ============================================================

def gtts_generate_audio(text: str, lang: str, slow: bool, tld: str) -> bytes:
    """Generates audio bytes from text using gTTS with the specified parameters."""
    tts = gTTS(text=text, lang=lang, slow=slow, tld=tld)
    audio_bytes = tts.write_to_fp()  # Get audio as bytes
    return audio_bytes