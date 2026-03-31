# ================================================================
# Imports
# ================================================================
from newspaper import Article, Config
import nltk
nltk.download('punkt_tab')  # Download the 'punkt_tab' tokenizer for better sentence
import streamlit as st
t = st.session_state.get("t", {})  # Shortcut to access translations

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
        with st.status(t["url_extracting"], expanded=True) as status:
            st.info(t["url_downloading"])
            article = Article(url, config=config)
            article.download()

            st.info(t["url_parsing"])
            article.parse()

            st.info(t["url_nlp"])
            article.nlp()

            status.update(label=t["url_ready"], state="complete", expanded=False)
        return article
    except Exception as e:
        st.error(t["url_error"] + f" {e}")
        return "Error"
    
def process_final_text_and_errors(input, text_mode):
    if text_mode == "text":
        if not input.strip():
            st.error(t["txt_error_text_empty"])
            st.stop()
        return input
    elif text_mode == "url":
        if not input.strip():
            st.error(t["txt_error_url_empty"])
            st.stop()
        article = extract_text_from_url(input)
        if isinstance(article, str):  # If an error message was returned
            st.error(t["txt_error_url_error"])
            st.stop()
        if not article.text.strip():
            st.error(t["txt_error_url_extraction"])
            st.stop()
        return article.text