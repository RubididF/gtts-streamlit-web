import streamlit as st

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