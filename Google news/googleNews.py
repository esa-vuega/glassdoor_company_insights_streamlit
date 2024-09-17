import streamlit as st
from serpapi import GoogleSearch
import os
from dotenv import load_dotenv

load_dotenv()

# Replace with your SerpAPI API key
API_KEY = os.getenv("API_KEY")

def fetch_news_serpapi(query):
    params = {
        "engine": "google_news",
        "q": query,
        "gl": "us",
        "hl": "en",
        "api_key": API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    news_results = results.get("news_results", [])
    
    news_list = []
    for article in news_results:
        news_list.append({
            'title': article['title'],
            'link': article['link']
        })
    
    return news_list

# Streamlit UI
st.title("Google News Fetcher with SerpAPI")

# Input search query
query_input = st.text_input("Enter News Query", "Technology")

if st.button("Fetch News"):
    if query_input:
        news_articles = fetch_news_serpapi(query_input)
        
        if news_articles:
            # Display news articles
            st.subheader(f"News Articles:")
            for idx, article in enumerate(news_articles):
                st.markdown(f"<span style=' font-weight: bold;'>Article {idx + 1}:</span> <a href='{article['link']}'>{article['title']}</a>", unsafe_allow_html=True)
                
                st.write("---")
        else:
            st.error("Failed to fetch news or no articles found.")
    else:
        st.error("Please enter a search query.")
