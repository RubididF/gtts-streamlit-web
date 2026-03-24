from deep_translator import GoogleTranslator
import streamlit as st

# ── Diccionario de idiomas: código -> nombre ───────────────────────────────
LANGUAGES = {
    "af": "Afrikáans",      "sq": "Albanés",
    "ar": "Árabe",          "hy": "Armenio",
    "az": "Azerbaiyano",    "eu": "Euskera",
    "be": "Bielorruso",     "bn": "Bengalí",
    "bs": "Bosnio",         "bg": "Búlgaro",
    "ca": "Catalán",        "km": "Jemer",
    "zh-CN": "Chino (Simpl.)", "zh-TW": "Chino (Trad.)",
    "hr": "Croata",         "cs": "Checo",
    "da": "Danés",          "nl": "Neerlandés",
    "en": "Inglés",         "eo": "Esperanto",
    "et": "Estonio",        "fi": "Finlandés",
    "fr": "Francés",        "gl": "Galego",
    "ka": "Georgiano",      "de": "Alemán",
    "el": "Griego",         "gu": "Gujarati",
    "ht": "Criollo haitiano", "ha": "Hausa",
    "iw": "Hebreo",         "hi": "Hindi",
    "hu": "Húngaro",        "is": "Islandés",
    "id": "Indonesio",      "ga": "Irlandés",
    "it": "Italiano",       "ja": "Japonés",
    "kn": "Kannada",        "kk": "Kazajo",
    "ko": "Coreano",        "ky": "Kirguís",
    "lo": "Lao",            "la": "Latín",
    "lv": "Letón",          "lt": "Lituano",
    "lb": "Luxemburgués",   "mk": "Macedonio",
    "ml": "Malayalam",      "ms": "Malayo",
    "mt": "Maltés",         "mr": "Marathi",
    "mn": "Mongol",         "my": "Birmano",
    "ne": "Nepalés",        "no": "Noruego",
    "ny": "Nyanja",         "fa": "Persa",
    "pl": "Polaco",         "pt": "Portugués",
    "pa": "Punjabi",        "ro": "Rumano",
    "ru": "Ruso",           "sr": "Serbio",
    "si": "Cingalés",       "sk": "Eslovaco",
    "sl": "Esloveno",       "so": "Somalí",
    "es": "Español",        "sw": "Suajili",
    "sv": "Sueco",          "tg": "Tayiko",
    "ta": "Tamil",          "te": "Telugu",
    "th": "Tailandés",      "tl": "Filipino",
    "tr": "Turco",          "tk": "Turcomano",
    "uk": "Ucraniano",      "ur": "Urdu",
    "uz": "Uzbeko",         "vi": "Vietnamita",
    "cy": "Galés",          "yi": "Yiddish",
    "yo": "Yoruba",         "zu": "Zulú",
}

_lang_options = list(LANGUAGES.values())
_lang_keys    = list(LANGUAGES.keys())

# Function to create a language selector dropdown in Streamlit, allowing users to choose a target language for translation
def language_selector(default_lang: str = "en", key: str = "lang_selector") -> str:
    default_index = _lang_keys.index(default_lang) if default_lang in _lang_keys else 0
    selected_label = st.selectbox(
        "🌐",
        options=_lang_options,
        index=default_index,
        key=key,
    )
    return _lang_keys[_lang_options.index(selected_label)]

# Function to perform translation using GoogleTranslator, with caching to optimize performance
@st.cache_data(show_spinner=False)
def translate(text: str, target_lang: str, source_lang: str = "auto") -> str:
    if not text.strip():
        return text
    return GoogleTranslator(source=source_lang, target=target_lang).translate(text)