from deep_translator import GoogleTranslator
import streamlit as st

LANGUAGES = {
    "af": "Afrikaans",          "sq": "Shqip",
    "ar": "العربية",            "hy": "Հայերեն",
    "az": "Azərbaycan",         "eu": "Euskara",
    "be": "Беларуская",         "bn": "বাংলা",
    "bs": "Bosanski",           "bg": "Български",
    "ca": "Català",             "km": "ខ្មែរ",
    "zh-CN": "中文（简体）",     "zh-TW": "中文（繁體）",
    "hr": "Hrvatski",           "cs": "Čeština",
    "da": "Dansk",              "nl": "Nederlands",
    "en": "English",            "eo": "Esperanto",
    "et": "Eesti",              "fi": "Suomi",
    "fr": "Français",           "gl": "Galego",
    "ka": "ქართული",            "de": "Deutsch",
    "el": "Ελληνικά",           "gu": "ગુજરાતી",
    "ht": "Kreyòl ayisyen",     "ha": "Hausa",
    "iw": "עברית",              "hi": "हिन्दी",
    "hu": "Magyar",             "is": "Íslenska",
    "id": "Bahasa Indonesia",   "ga": "Gaeilge",
    "it": "Italiano",           "ja": "日本語",
    "kn": "ಕನ್ನಡ",             "kk": "Қазақша",
    "ko": "한국어",              "ky": "Кыргызча",
    "lo": "ລາວ",                "la": "Latina",
    "lv": "Latviešu",           "lt": "Lietuvių",
    "lb": "Lëtzebuergesch",     "mk": "Македонски",
    "ml": "മലയാളം",            "ms": "Bahasa Melayu",
    "mt": "Malti",              "mr": "मराठी",
    "mn": "Монгол",             "my": "မြန်မာဘာသာ",
    "ne": "नेपाली",             "no": "Norsk",
    "ny": "Chichewa",           "fa": "فارسی",
    "pl": "Polski",             "pt": "Português",
    "pa": "ਪੰਜਾਬੀ",            "ro": "Română",
    "ru": "Русский",            "sr": "Српски",
    "si": "සිංහල",             "sk": "Slovenčina",
    "sl": "Slovenščina",        "so": "Soomaali",
    "es": "Español",            "sw": "Kiswahili",
    "sv": "Svenska",            "tg": "Тоҷикӣ",
    "ta": "தமிழ்",             "te": "తెలుగు",
    "th": "ภาษาไทย",           "tl": "Filipino",
    "tr": "Türkçe",             "tk": "Türkmençe",
    "uk": "Українська",         "ur": "اردو",
    "uz": "Oʻzbek",             "vi": "Tiếng Việt",
    "cy": "Cymraeg",            "yi": "ייִדיש",
    "yo": "Yorùbá",             "zu": "isiZulu",
}

_lang_options = list(LANGUAGES.values())
_lang_keys    = list(LANGUAGES.keys())


def language_selector(default_lang: str = "en", key: str = "lang_selector") -> str:
    # Columnas para que ocupe poco ancho: la primera es el selector, las demás son espacio vacío

    selected_label = st.selectbox(
        label="",                  # sin etiqueta para que sea más compacto
        options=_lang_options,
        index=_lang_keys.index(default_lang) if default_lang in _lang_keys else 0,
        key=key,
        label_visibility="collapsed",  # oculta el hueco del label
        )
    return _lang_keys[_lang_options.index(selected_label)]


@st.cache_data(show_spinner=False)
def translate(text: str, target_lang: str, source_lang: str = "auto") -> str:
    if not text.strip():
        return text
    return GoogleTranslator(source=source_lang, target=target_lang).translate(text)