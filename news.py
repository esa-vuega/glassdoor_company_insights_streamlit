import streamlit as st
import requests

# Replace 'your_api_key' with your actual NewsAPI key
API_KEY = 'afb4d5bf49764c2d97e3c0f4f05270f8'
BASE_URL = 'https://newsapi.org/v2/everything'

def fetch_news(query, language='en', page_size=5):
    """
    Fetches news articles based on the query.

    :param query: The search term for news articles.
    :param language: Language of the articles.
    :param page_size: Number of articles to fetch.
    :return: A list of articles.
    """
    params = {
        'q': query,
        'language': language,
        'pageSize': page_size,
        'apiKey': API_KEY
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        return data['articles']
    else:
        st.error(f"Failed to fetch news: {response.status_code}")
        return []

def main():
    st.title('News Article Finder')

    query = st.text_input("Enter search query", "")
    page_size = st.slider("Number of articles to display", min_value=1, max_value=100, value=5)
    
    if st.button('Fetch News'):
        if query:
            with st.spinner('Fetching news articles...'):
                articles = fetch_news(query, page_size=page_size)
                if articles:
                    for article in articles:
                        st.subheader(article['title'])
                        st.write(f"**Source**: {article['source']['name']}")
                        st.write(f"**Published At**: {article['publishedAt']}")
                        st.write(f"[Read More]({article['url']})")
                        st.write(f"**Description**: {article['description']}\n")
                else:
                    st.write("No articles found.")
        else:
            st.warning("Please enter a search query.")

if __name__ == "__main__":
    main()
