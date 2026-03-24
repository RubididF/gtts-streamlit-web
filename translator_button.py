from deep_translator import GoogleTranslator
import streamlit as st

# Top 5 idiomas más hablados del mundo
LANGUAGES = {
    "zh-CN": "Chino",
    "es":    "Español",
    "en":    "Inglés",
    "hi":    "Hindi",
    "fr":    "Francés",
}

_lang_options = list(LANGUAGES.values())
_lang_keys    = list(LANGUAGES.keys())

def language_selector(default_lang: str = "es", key: str = "lang_selector") -> str:
    # Columnas para que ocupe poco ancho: la primera es el selector, las demás son espacio vacío
    col, _ = st.columns([1, 4])
    with col:
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