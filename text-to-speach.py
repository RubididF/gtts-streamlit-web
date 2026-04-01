"""
Text-to-Speech Application using Streamlit

This application allows users to convert text into speech using gTTS.
You can personalize language of the generated speech. Users can input text directly or provide a URL
to extract text from a webpage. The generated speech can be played directly in the browser or downloaded as an .mp3 file.

Author: Rubén García Lajara
Version: 2.0
File: text-to-speech.py

"""
# ============================================================
# Import necessary libraries
# ============================================================
import streamlit as st
from scr.translator.translator import language_selector, translate
from scr.translator.i18n import get_translations
from scr.tts.audio_utils import render_audio_grid, process_audio
from scr.tts.gtts_engine import gtts_streamlit_params, gtts_options_translation
from scr.process_text import process_final_text_and_errors
from scr.ui.components import inject_css

# ============================================================
# Initialize Session State Variables
# ============================================================

if 'audios' not in st.session_state:
    st.session_state.audios = []  # List to store generated audio objects

if 'text_mode' not in st.session_state:
    st.session_state.text_mode = "text"  # Default input mode

if 'speech_model' not in st.session_state:
    st.session_state.speech_model = "gtts"  # Default TTS model

if 't' not in st.session_state:
    st.session_state.t = {}  # Dictionary to store translations

if 'previous_lang' not in st.session_state:
    st.session_state.previous_lang = None  # To track previously selected language for translation updates
#=============================================================
# Web app layout
#=============================================================

st.set_page_config(page_title="TTS Online", page_icon="🗣️", layout="centered")
inject_css()  # Inject global CSS styles

# ============================================================
# Language Selection
# ============================================================

t = st.session_state.t  # Shortcut to access translations
lang_label = st.empty()  # Placeholder for language selector label, will be updated after translation is loaded
lang = language_selector(default_lang="en")  # Language selector, default English
if lang != st.session_state.previous_lang:
    with st.spinner(translate("Loading translations...", lang)):
        st.session_state.t = get_translations(lang)  # Update translations in session state based on selected language
    st.session_state.previous_lang = lang # Update previous language for next selection
    st.rerun()  # Rerun the app to update all text with new translations
lang_label.write(translate("Select Language for the website", lang))  # Label for language selector

# ============================================================
# Title Area
# ============================================================

st.title(t['title'])
st.markdown(t['markdown1'])
st.markdown(t['markdown2'])
st.markdown(t['markdown3'])
st.markdown(t['markdown4'])

# ============================================================
# Audio Area
# ============================================================

st.divider()
st.subheader(t['audio_subheader'])

# Initialize audio list in session state if it doesn't exist
if "audios" not in st.session_state:
    st.session_state.audios = []

render_audio_grid()

# ============================================================
# Text Area - Text Input / URL Input
# ============================================================

st.divider()
st.subheader(t['input_subheader'])

col1, col2 = st.columns([1,1])

with col1:
    if st.button(t['text_button'], use_container_width=True):
        st.session_state.text_mode = "text"
with col2:
    if st.button(t['url_button'], use_container_width=True):
        st.session_state.text_mode = "url"

if st.session_state.text_mode == "text":
    tts_input = st.text_area(t['text_input_label'])
if st.session_state.text_mode == "url":
    tts_input = st.text_input(t['url_input_label'])

# ============================================================
# Processing Area - Select TTS Parameters 
# ============================================================

st.divider()
st.subheader(t['tts_subheader'])

t_gtts = gtts_options_translation(lang)
lang_gtts, slow_gtts, tld_gtts = gtts_streamlit_params(lang, t_gtts)

# ============================================================
# Process Button - Generate TTS
# ============================================================

generate_button = st.button(t["generate_speech"])
if generate_button:
    final_input = process_final_text_and_errors(tts_input, st.session_state.text_mode)
    with st.spinner(t["generate_audio"]):
        process_audio(final_input, st.session_state.speech_model, st.session_state.text_mode, (lang_gtts, slow_gtts, tld_gtts))
    st.rerun()