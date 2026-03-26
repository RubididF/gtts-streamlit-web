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
#=============================================================
# Constants
#=============================================================
GTTSLENGUAGES = tts_langs()  # Languages supported by gTTS
GTTS_ACCENTS: dict[str, list[dict[str, str]]] = {

    # ── Idiomas CON múltiples acentos ──────────────────────────────────

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
        {"tld": "be", "accent": "Belgique"},
        {"tld": "ch", "accent": "Suisse"},
    ],
    # fr-CA ya es un código propio, pero también acepta TLD
    "fr-CA": [
        {"tld": "ca", "accent": "Canada"},
        {"tld": "fr", "accent": "France"},
    ],
    "es": [
        {"tld": "es",     "accent": "España"},
        {"tld": "com.mx", "accent": "México"},
        {"tld": "com",    "accent": "Latinoamérica (neutro)"},
        {"tld": "com.ar", "accent": "Argentina"},
        {"tld": "co",     "accent": "Colombia"},
        {"tld": "cl",     "accent": "Chile"},
    ],
    "pt": [
        {"tld": "com.br", "accent": "Brasil"},
        {"tld": "pt",     "accent": "Portugal"},
    ],
    # pt-PT ya es un código propio
    "pt-PT": [
        {"tld": "pt",     "accent": "Portugal"},
        {"tld": "com.br", "accent": "Brasil"},
    ],
    "de": [
        {"tld": "de", "accent": "Deutschland"},
        {"tld": "at", "accent": "Österreich"},
        {"tld": "ch", "accent": "Schweiz"},
    ],
    "nl": [
        {"tld": "nl", "accent": "Nederland"},
        {"tld": "be", "accent": "België"},
    ],
    "it": [
        {"tld": "it", "accent": "Italia"},
        {"tld": "ch", "accent": "Svizzera"},
    ],
    "ru": [
        {"tld": "ru",  "accent": "Россия"},
        {"tld": "com", "accent": "Internacional"},
    ],
    "zh-CN": [
        {"tld": "com",    "accent": "普通话（大陆）"},
        {"tld": "com.hk", "accent": "香港"},
    ],
    "zh-TW": [
        {"tld": "com.tw", "accent": "台灣"},
        {"tld": "com",    "accent": "Internacional"},
    ],
    "zh": [
        {"tld": "com",    "accent": "普通话"},
        {"tld": "com.hk", "accent": "香港"},
    ],
    # Cantonés (yue) — variantes HK vs internacional
    "yue": [
        {"tld": "com.hk", "accent": "香港"},
        {"tld": "com",    "accent": "Internacional"},
    ],

    # ── Idiomas con UN solo TLD funcional ──────────────────────────────
    # (se incluyen igualmente para que get_accents() siempre devuelva algo)

    "af":  [{"tld": "com",     "accent": "Afrikaans"}],
    "am":  [{"tld": "com",     "accent": "Amharic"}],
    "ar":  [{"tld": "com",     "accent": "عربي"}],
    "bg":  [{"tld": "com",     "accent": "Български"}],
    "bn":  [{"tld": "com",     "accent": "বাংলা"}],
    "bs":  [{"tld": "com",     "accent": "Bosanski"}],
    "ca":  [{"tld": "com",     "accent": "Català"}],
    "cs":  [{"tld": "com",     "accent": "Čeština"}],
    "cy":  [{"tld": "com",     "accent": "Cymraeg"}],
    "da":  [{"tld": "com",     "accent": "Dansk"}],
    "el":  [{"tld": "com",     "accent": "Ελληνικά"}],
    "et":  [{"tld": "com",     "accent": "Eesti"}],
    "eu":  [{"tld": "com",     "accent": "Euskara"}],
    "fi":  [{"tld": "com",     "accent": "Suomi"}],
    "gl":  [{"tld": "com",     "accent": "Galego"}],
    "gu":  [{"tld": "co.in",   "accent": "ગુજરાતી"}],
    "ha":  [{"tld": "com",     "accent": "Hausa"}],
    "hi":  [{"tld": "co.in",   "accent": "हिन्दी"}],
    "hr":  [{"tld": "com",     "accent": "Hrvatski"}],
    "hu":  [{"tld": "com",     "accent": "Magyar"}],
    "id":  [{"tld": "com",     "accent": "Bahasa Indonesia"}],
    "is":  [{"tld": "com",     "accent": "Íslenska"}],
    "iw":  [{"tld": "com",     "accent": "עברית"}],
    "ja":  [{"tld": "co.jp",   "accent": "日本語"}],
    "jw":  [{"tld": "com",     "accent": "Basa Jawa"}],
    "km":  [{"tld": "com",     "accent": "ខ្មែរ"}],
    "kn":  [{"tld": "co.in",   "accent": "ಕನ್ನಡ"}],
    "ko":  [{"tld": "co.kr",   "accent": "한국어"}],
    "la":  [{"tld": "com",     "accent": "Latina"}],
    "lt":  [{"tld": "com",     "accent": "Lietuvių"}],
    "lv":  [{"tld": "com",     "accent": "Latviešu"}],
    "ml":  [{"tld": "co.in",   "accent": "മലയാളം"}],
    "mr":  [{"tld": "co.in",   "accent": "मराठी"}],
    "ms":  [{"tld": "com",     "accent": "Bahasa Melayu"}],
    "my":  [{"tld": "com",     "accent": "မြန်မာ"}],
    "ne":  [{"tld": "com",     "accent": "नेपाली"}],
    "no":  [{"tld": "com",     "accent": "Norsk"}],
    "pa":  [{"tld": "co.in",   "accent": "ਪੰਜਾਬੀ"}],
    "pl":  [{"tld": "com",     "accent": "Polski"}],
    "ro":  [{"tld": "com",     "accent": "Română"}],
    "si":  [{"tld": "com",     "accent": "සිංහල"}],
    "sk":  [{"tld": "com",     "accent": "Slovenčina"}],
    "sq":  [{"tld": "com",     "accent": "Shqip"}],
    "sr":  [{"tld": "com",     "accent": "Српски"}],
    "su":  [{"tld": "com",     "accent": "Basa Sunda"}],
    "sv":  [{"tld": "com",     "accent": "Svenska"}],
    "sw":  [{"tld": "com",     "accent": "Kiswahili"}],
    "ta":  [{"tld": "co.in",   "accent": "தமிழ்"}],
    "te":  [{"tld": "co.in",   "accent": "తెలుగు"}],
    "th":  [{"tld": "com",     "accent": "ภาษาไทย"}],
    "tl":  [{"tld": "com",     "accent": "Filipino"}],
    "tr":  [{"tld": "com.tr",  "accent": "Türkçe"}],
    "uk":  [{"tld": "com.ua",  "accent": "Українська"}],
    "ur":  [{"tld": "com",     "accent": "اردو"}],
    "vi":  [{"tld": "com.vn",  "accent": "Tiếng Việt"}],
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
 
MAX_TEXT_CHARS = 130  # Maximum Characters Visibles at the audio card
 
#============================================================
# Clases
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

#============================================================
# Global CSS
#===========================================================

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
# GTTS Functions
#=============================================================
def gtts_get_accents(language_code: str) -> list[dict[str, str]]:
    """
    Devuelve los acentos disponibles para el código de idioma dado.

    Args:
        language_code: Código ISO del idioma (e.g. 'en', 'es', 'fr').

    Returns:
        Lista de dicts con las claves 'tld' y 'accent'.
        Si el idioma no tiene acentos registrados, devuelve el TLD por defecto 'com'. 

    Raises:
        ValueError: Si el código de idioma no es válido para gTTS.
    """
    if language_code not in GTTSLENGUAGES:
        supported = ", ".join(sorted(GTTSLENGUAGES.keys()))
        raise ValueError(
            f"Language '{language_code}' not soported by gTTS. "
            f"Languages available: {supported}"
        )

    return GTTS_ACCENTS.get(
        language_code,
        [{"tld": "com", "accent": "Estándar"}],  # fallback para idiomas sin variantes
    )

def gtts_has_accents(language_code: str) -> bool:
    """Devuelve True si el idioma tiene más de una variante de acento."""
    return len(GTTS_ACCENTS.get(language_code, [])) > 1
2

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
#   Audio Management - List to store generated audio objects, function to create audio objects and manage them
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
        msg = translate("No hay audios generados todavía.", lang)
        st.markdown(f"""<div style="text-align:center;padding:40px;color:rgba(150,160,180,0.35);font-style:italic;">{msg}</div>""", unsafe_allow_html=True)
        return

    n = len(audios)
    label_audio   = translate("audio", lang)
    label_audios  = translate("audios", lang)
    label_generado  = translate("generado", lang)
    label_generados = translate("generados", lang)

    st.markdown(f"""<p style="color:rgba(150,160,180,0.5);font-size:0.8rem;font-family:'JetBrains Mono',monospace;margin-bottom:12px;">{n} {label_audios if n != 1 else label_audio} {label_generados if n != 1 else label_generado}</p>""", unsafe_allow_html=True)

    # Groups of 4 cards per row
    for row_start in range(0, n, 4):
        row_audios = audios[row_start : row_start + 4]
        cols = st.columns(len(row_audios))
        for col, (audio, abs_index) in zip(cols, [(a, row_start + i) for i, a in enumerate(row_audios)]):
            with col:
                render_card(audio, abs_index)

#============================================================
# Inicialize Session State Variables
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

#Title and description
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

#   Initialize audio list in session state if it doesn't exist
if "audios" not in st.session_state:
    st.session_state.audios = []

render_audio_grid(lang)

#============================================================
# Text Area - Text Input / URL Input
#============================================================

tab_text, tab_url = st.tabs([translate("Texto normal",lang), translate("URL",lang)])

with tab_text:
    st.session_state.text_mode = "text"
    text_input = st.text_area(translate("Introduce tu texto:",lang))
with tab_url:
    st.session_statetext_mode = "url"
    url_input = st.text_input(translate("Introduce la URL:",lang))

#============================================================
# Processing Area - Select TTS Engine and his parameters
#============================================================
st.subheader(translate("Select TTS Engine and Parameters",lang))
tab_gtts, tab_edge, tab_pyht, tab_pyttsx3, tab_aitts = st.tabs(["gTTS", "Edge TTS", "PyHT", "pyttsx3", "aitts_maker"])
with tab_gtts:
    st.markdown(translate("### gTTS Parameters",lang))
    st.session_state.speach_model = "gtts"
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
    st.markdown(translate("### edge_TTS Parameters",lang))
    st.session_state.speach_model = "edge"

with tab_pyht:
    st.markdown(translate("### PyHT Parameters",lang))
    st.session_state.speach_model = "pyht"
with tab_pyttsx3:
    st.markdown(translate("### pyttsx3 Parameters",lang))
    st.session_state.speach_model = "pyttsx3"
with tab_aitts: 
    st.markdown(translate("### aitts_maker Parameters",lang))
    st.session_state.speach_model = "aitts"

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
    if st.session_state.speach_model == "gtts":
        tts = gTTS(text=text_input, lang=gtts_lang, slow=gtts_slow, tld=gtts_tld)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)

    new_audio = Audio(
        text=text_input,
        model=st.session_state.get("speech_model", "gtts"),       
        audio_bytes=audio_buffer.getvalue()
    )
    st.session_state.audios.append(new_audio)
    st.rerun()  