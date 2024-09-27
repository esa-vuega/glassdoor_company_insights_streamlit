import streamlit as st
from serpapi.google_search import GoogleSearch
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
    
    # Create a dictionary to hold titles and their corresponding sources and links
    news_dict = {}
    
    for article in news_results:
        title = article.get('title', 'No Title Available')
        link = article.get('link')
        source = article.get('source', {}).get('name', 'Unknown Source')
        
        # If the main article has a link, add it to the dictionary under the title
        if link:
            if title not in news_dict:
                news_dict[title] = {'sources': [], 'links': []}
            news_dict[title]['sources'].append(source)
            news_dict[title]['links'].append(link)
        
        # Check if there are additional stories for the article
        if 'stories' in article:
            for story in article['stories']:
                story_link = story.get('link')
                story_source = story.get('source', {}).get('name', 'Unknown Source')
                
                if story_link:
                    # If the title already exists, append the story link and source
                    if title not in news_dict:
                        news_dict[title] = {'sources': [], 'links': []}
                    news_dict[title]['sources'].append(story_source)
                    news_dict[title]['links'].append(story_link)
    
    return news_dict

# Streamlit UI
st.title("Google News Fetcher with SerpAPI")

# Input search query
query_input = st.text_input("Enter News Query", "Technology")

if st.button("Fetch News"):
    if query_input:
        news_articles = fetch_news_serpapi(query_input)
        article_count = len(news_articles)  # Count the total number of unique articles
        
        if article_count > 0:
            # Display the number of unique articles fetched
            st.subheader(f"Found {article_count} unique articles:")
            
            # Display each main article title with its associated sources and links
            for idx, (title, details) in enumerate(news_articles.items()):
                st.markdown(f"### {idx + 1}: {title}")
                
                # List all sources and links for the current article
                for source, link in zip(details['sources'], details['links']):
                    st.markdown(f"- Source: [**{source}**]({link})", unsafe_allow_html=True)
                
                st.write("---")
        else:
            st.error("Failed to fetch news or no articles found.")
    else:
        st.error("Please enter a search query.")
