from scr.translator.translator import translate
from scr.tts.gtts_engine import GTTS_LANGUAGES, GTTS_ACCENTS

# All scripts agrupated by script
_STRINGS = {
# ================ app.py ================

"select_lang": "Select Language for the website",

"title": "Text-to-Speech Application",
"markdown1": "🎙️ **This application allows you to convert text into speech** using *GTTS*.",
"markdown2": "🎛️ You can personalize the **__speed__**, **__language__**, and **__accent__** of the generated speech.",
"markdown3": "✍️ You can **input text directly** or provide a *URL* to extract text from a webpage.",
"markdown4": "🔊 The generated speech can be **played directly in the browser**",

"audio_subheader": "Generated Audios 🔊",

"input_subheader": "Input Text or URL ✍️",
"text_button": "Text",
"url_button": "URL",
"text_input_label": "Enter your text:",
"url_input_label": "Enter the URL:",

"tts_subheader": "TTS Parameters",

"generate_speech": "Generate Speech",
"generate_audio": "Generating audio...",

# ============ audio_utils.py ============
"au_Untitled": "Untitled",
"au_no_audios": "No audio generated yet.",
"au_label_audio": "audio",
"au_label_audios": "audios",
"au_label_generated": "generated",
"au_label_generated_plural": "generados",

# ============ gtts_engine.py ============
"gtts_select_lang": "Select language for gTTS:",
"gtts_slow_speed": "Slow speed",
"gtts_select_tld": "Select accent for gTTS:",

# ============ process_text.py ============
"url_extracting": "Extracting text from URL...",
"url_downloading": "⬇️ Downloading article...",
"url_parsing": "🔍 Parsing content...",
"url_nlp": "🧠 Running NLP analysis...",
"url_ready": "✅ Article ready!",
"url_error": "Error extracting text from URL:",
"txt_error_text_empty": "Please enter some text to convert to speech.",
"txt_error_url_empty": "Please enter a URL to extract text from.",
"txt_error_url_error": "Failed to extract text from the provided URL.",
"txt_error_url_extraction": "No text could be extracted from the provided URL."
}

# MEJORAR PROXIMAMENTE
def get_translations(lang: str) -> dict:
    """Returns a dictionary with all the translations for the given language."""
    # Translate Constants
    for lang in GTTS_LANGUAGES:
        _STRINGS[GTTS_LANGUAGES[lang]] = GTTS_LANGUAGES[lang] # Add language names to translations if not already present
    for lang in GTTS_ACCENTS:
        for accent in GTTS_ACCENTS[lang]:
            _STRINGS[accent["accent"]] = accent["accent"] # Add accent names to translations if not already present


    return {k: translate(v, lang) for k, v in _STRINGS.items()}