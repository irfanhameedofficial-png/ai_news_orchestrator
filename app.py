# app.py
import streamlit as st
from src.fetch.news_api import fetch_news
from src.summarize.gemini_summarizer import summarize_timeline
import os

st.set_page_config(page_title="AI News Orchestrator", layout="wide")

st.title("AI News Orchestrator — Timeline Builder (MVP)")

st.markdown(
    "Enter an event/topic. The app fetches top articles, builds a timeline and a short summary using Gemini (if configured)."
)

with st.sidebar:
    st.header("Settings")
    query = st.text_input("Event / topic", value="Chandrayaan-3 Mission")
    max_articles = st.slider("Number of articles to fetch", 1, 12, 6)
    st.write("Keys: set in Streamlit Secrets (NEWSAPI_KEY, GEMINI_API_KEY)")

if st.button("Run"):
    try:
        with st.spinner("Fetching articles from NewsAPI..."):
            articles = fetch_news(query, limit=max_articles)
        st.success(f"Fetched {len(articles)} articles")
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        st.stop()

    # show fetched articles
    st.subheader("Fetched articles")
    for a in articles:
        st.markdown(f"**{a['headline']}**")
        st.write(a["summary"])
        cols = st.columns([1,8,1])
        with cols[0]:
            st.write(a.get("published"))
        with cols[2]:
            st.write(a.get("source"))
        st.markdown(f"[Read original article]({a.get('url')})")
        st.divider()

    # call summarizer
    with st.spinner("Summarizing timeline (Gemini or fallback)..."):
        out = summarize_timeline(articles)

    st.subheader("Timeline & Summary")
    st.code(out)

import streamlit as st

st.write("Debug – NEWSAPI_KEY exists:", "NEWSAPI_KEY" in st.secrets)