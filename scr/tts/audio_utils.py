# ============================================================
# Imports
# ============================================================
import uuid
from newspaper import Article
import streamlit as st
import time
from io import BytesIO
t = st.session_state.get("t", {})  # Shortcut to access translations
# ============================================================
# Constants
# ============================================================

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


# ============================================================
# Audio Management - List to store generated audio objects, function to create audio objects and manage them
# ============================================================

def render_card(audio: Audio, index: int):
    c = audio.color
    if audio.text_mode == "url":
        art = audio.input

        title = art.title or t['au_Untitled']

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

def render_audio_grid():
    audios = st.session_state.audios
    if not audios:
        msg = t["au_no_audios"]
        st.markdown(f"""<div style="text-align:center;padding:40px;color:rgba(150,160,180,0.35);font-style:italic;">{msg}</div>""", unsafe_allow_html=True)
        return

    n = len(audios)
    label_audio   = t["au_label_audio"]
    label_audios  = t["au_label_audios"]
    label_generated  = t["au_label_generated"]
    label_generated_plural = t["au_label_generated_plural"]

    st.markdown(f"""<p style="color:rgba(150,160,180,0.5);font-size:0.8rem;font-family:'JetBrains Mono',monospace;margin-bottom:12px;">{n} {label_audios if n != 1 else label_audio} {label_generated_plural if n != 1 else label_generated}</p>""", unsafe_allow_html=True)

    # Groups of 4 cards per row
    for row_start in range(0, n, 4):
        row_audios = audios[row_start : row_start + 4]
        cols = st.columns(len(row_audios))
        for col, (audio, abs_index) in zip(cols, [(a, row_start + i) for i, a in enumerate(row_audios)]):
            with col:
                render_card(audio, abs_index)

# ============================================================
# Audio Creation and Management
# ============================================================

def process_audio(input, model, text_mode, preferences):
    
    if text_mode == "url":
        text = input.text
    else:
        text = input
    
    match model:
        case "gtts":
            from .gtts_engine import gtts_generate_audio
            gtts_lang, gtts_slow, gtts_tld = preferences
            tts = gtts_generate_audio(text, gtts_lang, gtts_slow, gtts_tld)
        case _:
            raise ValueError(f"Unsupported TTS model: {model}")

    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)

    new_audio = Audio(text, model, text_mode, audio_bytes=audio_buffer.getvalue())
    st.session_state.audios.append(new_audio)