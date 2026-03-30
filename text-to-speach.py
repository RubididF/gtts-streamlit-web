"""
Text-to-Speech Application using Streamlit

This application allows users to convert text into speech using gTTS.
You can personalize language of the generated speech. Users can input text directly or provide a URL
to extract text from a webpage. The generated speech can be played directly in the browser or downloaded as an .mp3 file.

Author: Rubén García Lajara
Version: 1.2
File: text-to-speech.py

"""
# ============================================================
# Import necessary libraries
# ============================================================
import streamlit as st
from gtts import gTTS
from newspaper import Article, Config
import nltk
nltk.download('punkt_tab')
from translator_button import language_selector, translate
from gtts.lang import tts_langs
from io import BytesIO
import uuid
import time
# ============================================================
# Classes
# ============================================================
class Audio:
    def __init__(self, input: str | Article, model: str, text_mode: str, audio_bytes: bytes):
        self.input        = input
        self.model        = model
        self.text_mode    = text_mode
        self.audio_bytes  = audio_bytes
        self.id           = str(uuid.uuid4())
 
    @property
    def color(self):
        return MODEL_COLORS.get(self.model, MODEL_COLORS["default"])
 
    @property
    def display_text(self):
        if len(self.input) <= MAX_TEXT_CHARS:
            return self.input
        return self.input[:MAX_TEXT_CHARS] + "…"


# =============================================================
# Constants
# =============================================================
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
MODEL_COLORS = {
    "gtts": {
        "border":     "#F59E0B",
        "bg":         "rgba(245, 158, 11, 0.07)",
        "tag_bg":     "rgba(245, 158, 11, 0.15)",
        "tag_text":   "#FCD34D",
        "glow":       "rgba(245, 158, 11, 0.15)",
    },
    "default": {
        "border":     "#6B7280",
        "bg":         "rgba(107, 114, 128, 0.07)",
        "tag_bg":     "rgba(107, 114, 128, 0.15)",
        "tag_text":   "#D1D5DB",
        "glow":       "rgba(107, 114, 128, 0.15)",
    }
}
MAX_TEXT_CHARS = 130  # Maximum visible characters in the audio card


# ============================================================
# Global CSS
# ============================================================

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
    </style>
    """, unsafe_allow_html=True)

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

# ================================================================
# Processing Functions - Text extraction
# ================================================================

# Newspaper configuration to speed up article extraction by disabling image fetching and memoization
config = Config()
config.fetch_images = False
config.memoize_articles = False

def extract_text_from_url(url: str) -> Article | str:
    """Extracts the main text from a webpage given its URL."""
    try:
        with st.status(translate("Extracting text from URL...", lang), expanded=True) as status:
            st.info(translate("⬇️ Downloading article...", lang))
            article = Article(url, config=config)
            article.download()

            st.info(translate("🔍 Parsing content...", lang))
            article.parse()

            st.info(translate("🧠 Running NLP analysis...", lang))
            article.nlp()

            status.update(label=translate("✅ Article ready!", lang), state="complete", expanded=False)
        return article
    except Exception as e:
        st.error(translate("Error extracting text from URL:", lang) + f" {e}")
        return "Error"

# ============================================================
# Audio Management - List to store generated audio objects, function to create audio objects and manage them
# ============================================================

def render_card(audio: Audio, index: int):
    c = audio.color
    if audio.text_mode == "url":
        art = audio.input

        title = art.title or translate("Untitled", lang)

        date_str = ""
        if art.publish_date:
            date_str = f'<div style="color:rgba(200,210,230,0.4);font-size:0.72rem;font-family:\'JetBrains Mono\',monospace;margin-top:6px;">📅 {art.publish_date.strftime("%d %b %Y")}</div>'

        authors_str = ""
        if art.authors:
            authors_joined = ", ".join(art.authors)
            authors_str = f'<div style="color:rgba(200,210,230,0.4);font-size:0.72rem;font-family:\'JetBrains Mono\',monospace;margin-top:4px;">✍️ {authors_joined}</div>'

        summary_str = ""
        if art.summary:
            summary_str = f'<div style="color:rgba(200,210,230,0.7);font-size:0.8rem;font-family:\'JetBrains Mono\',monospace;margin-top:10px;line-height:1.5;">{art.summary}</div>'

        inner_content = f"""<div style="margin-bottom:8px;"><p style="color:rgba(220,230,245,0.92);font-size:1.05rem;font-family:'JetBrains Mono',monospace;font-weight:700;line-height:1.4;margin:0;">{title}</p>{date_str}{authors_str}{summary_str}</div>"""
    else:
        inner_content = f"""<p style="font-style:italic;color:rgba(200,210,230,0.45);font-size:0.85rem;font-family:'JetBrains Mono',monospace;line-height:1.5;margin:0 0 10px 0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">&ldquo;{audio.display_text}&rdquo;</p>"""
        
    st.markdown(f"""<div class="audio-card-wrapper"><div style="position:relative;border:1.5px solid {c['border']};border-radius:14px;padding:16px 18px 12px 18px;background:{c['bg']};box-shadow:0 0 18px {c['glow']},0 2px 8px rgba(0,0,0,0.3);"><span style="font-family:'JetBrains Mono',monospace;font-size:0.65rem;opacity:0.4; position:absolute;top:10px;right:14px;">#{index + 1}</span><div style="margin-bottom:10px;"><span style="background:{c['tag_bg']};color:{c['tag_text']};border:1px solid {c['border']};border-radius:20px;padding:2px 10px;font-size:0.7rem; font-family:'JetBrains Mono',monospace;font-weight:600; letter-spacing:0.06em;text-transform:uppercase;">⬡ {audio.model}</span></div>{inner_content}</div></div>""", unsafe_allow_html=True)
    
    st.audio(audio.audio_bytes, format="audio/mp3")

    col1, col2 = st.columns([1.33, 0.66])
    
    with col1:
        st.download_button(
            label="⬇️",
            data=audio.audio_bytes,
            file_name=f"{audio.model}_{index + 1}_{int(time.time())}.mp3",
            use_container_width=True
        )

    with col2:    
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
    label_generated  = translate("generated", lang)
    label_generated_plural = translate("generated", lang)

    st.markdown(f"""<p style="color:rgba(150,160,180,0.5);font-size:0.8rem;font-family:'JetBrains Mono',monospace;margin-bottom:12px;">{n} {label_audios if n != 1 else label_audio} {label_generated_plural if n != 1 else label_generated}</p>""", unsafe_allow_html=True)

    # Groups of 4 cards per row
    for row_start in range(0, n, 4):
        row_audios = audios[row_start : row_start + 4]
        cols = st.columns(len(row_audios))
        for col, (audio, abs_index) in zip(cols, [(a, row_start + i) for i, a in enumerate(row_audios)]):
            with col:
                render_card(audio, abs_index)

# ============================================================
# Initialize Session State Variables
# ============================================================

if 'audios' not in st.session_state:
    st.session_state.audios = []  # List to store generated audio objects

if 'text_mode' not in st.session_state:
    st.session_state.text_mode = "text"  # Default input mode

if 'previous_lang' not in st.session_state:
    st.session_state.previous_lang = ""  # To track language changes for showing spinner

# ============================================================
# Language Selection
# ============================================================

inject_css()  # Inject global CSS styles

lang = language_selector(default_lang="en")  # Language selector, default English
st.write(translate("Select Language for the website", lang))

spinner_placeholder = st.empty()

if st.session_state.previous_lang != lang:
    st.session_state.previous_lang = lang
    spinner_placeholder = st.spinner(translate("Translating interface...", lang))
    spinner_placeholder.__enter__()

st.session_state.previous_lang = lang

# ============================================================
# Title Area
# ============================================================

st.title(translate("Text-to-Speech Application", lang))
st.markdown(translate("🎙️ **This application allows you to convert text into speech** using *GTTS*.", lang))
st.markdown(translate("🎛️ You can personalize the **__speed__**, **__language__**, and **__accent__** of the generated speech.", lang))
st.markdown(translate("✍️ You can **input text directly** or provide a *URL* to extract text from a webpage.", lang))
st.markdown(translate("🔊 The generated speech can be **played directly in the browser** or **downloaded as an .mp3 file**.", lang))

# ============================================================
# Audio Area
# ============================================================

st.divider()
st.subheader(translate("Generated Audios", lang))

# Initialize audio list in session state if it doesn't exist
if "audios" not in st.session_state:
    st.session_state.audios = []

render_audio_grid(lang)

# ============================================================
# Text Area - Text Input / URL Input
# ============================================================

st.divider()
st.markdown(translate("### Input Text or URL", lang))

col1, col2 = st.columns([1,1])

with col1:
    if st.button(translate("Text Mode", lang), use_container_width=True):
        st.session_state.text_mode = "text"
with col2:
    if st.button(translate("URL Mode", lang), use_container_width=True):
        st.session_state.text_mode = "url"

if st.session_state.text_mode == "text":
    text_input = st.text_area(translate("Enter your text:", lang))
if st.session_state.text_mode == "url":
    url_input = st.text_input(translate("Enter the URL:", lang))

# ============================================================
# Processing Area - Select GTTS Parameters 
# ============================================================

st.divider()
st.markdown(translate("### gTTS Parameters", lang))

index_gtts = 0
if lang in GTTS_LANGUAGES:
    index_gtts = list(GTTS_LANGUAGES.keys()).index(lang)
gtts_lang = st.selectbox(
    translate("Select language for gTTS:", lang),
    options=list(GTTS_LANGUAGES.keys()),
    index=index_gtts,
    format_func=lambda x: translate(GTTS_LANGUAGES[x], lang).capitalize())

gtts_slow = st.checkbox(translate("Slow speed", lang), value=False)
gtts_options = gtts_get_accents(gtts_lang)
gtts_tld = st.selectbox(
    translate("Select TLD for gTTS:", lang),
    options=[accent["tld"] for accent in gtts_options],
    index=0,
    format_func=lambda tld: translate(next(accent["accent"] for accent in gtts_options if accent["tld"] == tld), lang).capitalize())

# ============================================================
# Process Button - Generate TTS
# ============================================================

generate_button = st.button(translate("Generate Speech", lang))
if generate_button:
    if st.session_state.text_mode == "url":
        if not url_input.strip():
            st.error(translate("Please enter a URL.", lang))
            st.stop()
        url_input = extract_text_from_url(url_input)
        if isinstance(url_input, str):
            st.error(translate("Failed to extract text from the provided URL.", lang))
            st.stop()
        if not url_input.text.strip():
            st.error(translate("No text could be extracted from the provided URL.", lang))
            st.stop()
        
    if (st.session_state.text_mode == "text" and not text_input.strip()):
        st.error(translate("Please enter some text to convert to speech.", lang))
        st.stop()
    if (st.session_state.text_mode == "url" and not url_input.text.strip()):
        st.error(translate("Please enter a URL to extract text from.", lang))
        st.stop()
    
    with st.spinner(translate("Generating audio...", lang)):
        if st.session_state.text_mode == "text":
            tts = gTTS(text=text_input, lang=gtts_lang, slow=gtts_slow, tld=gtts_tld)
            input_for_audio = text_input
        else:
            tts = gTTS(text=url_input.text, lang=gtts_lang, slow=gtts_slow, tld=gtts_tld)
            input_for_audio = url_input
        
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)

    new_audio = Audio(
        input=input_for_audio,
        model=st.session_state.get("speech_model", "gtts"),   
        text_mode=st.session_state.get("text_mode"),
        audio_bytes=audio_buffer.getvalue()
    )

    st.session_state.audios.append(new_audio)
    st.rerun()

spinner_placeholder.__exit__(None, None, None)