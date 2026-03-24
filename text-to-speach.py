"""
Text-to-Speech Application using Streamlit

This application allows users to convert text into speech using various TTS engines.
You can personalize the voice, speed, and language of the generated speech. The application supports
multiple TTS engines, including gTTS, Edge TTS, PyHT, pyttsx3, and aitts_maker. Users can input text directly or provide a URL
to extract text from a webpage. The generated speech can be played directly in the browser or downloaded as an audio file.

Author: Rubén García Lajara
Version: 0.1
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

#============================================================
# Title Section
#============================================================
# Notas de Desarrollador:
# - Mejorar markdown visualmente con emojis y formato

st.title("Text-to-Speech Application")
st.markdown("""
🎙️ **This application allows you to convert text into speech** using various *TTS engines*.

🎛️ You can personalize the **__voice__**, **__speed__**, and **__language__** of the generated speech.

🧠 The application supports multiple *TTS engines*, including **gTTS**, **Edge TTS**, **PyHT**, **pyttsx3**, and **aitts_maker**.

✍️ You can **input text directly** or provide a *URL* to extract text from a webpage.

🔊 The generated speech can be **played directly in the browser** or **downloaded as an audio file**.
""")

#============================================================
# Text Mode - Text Input / URL Input
#============================================================
