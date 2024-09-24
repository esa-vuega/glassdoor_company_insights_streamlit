import requests
import csv

def get_news_about_company(company_name, api_key):
    url = f"https://newsapi.org/v2/everything"
    
    # Parameters for the API request
    params = {
        'q': company_name,
        'apiKey': api_key,
        'language': 'en',
        'sortBy': 'relevancy',
        'pageSize': 5,  # Limit to 5 results (increase as needed)
    }

    # Sending the request to the News API
    response = requests.get(url, params=params)

    if response.status_code == 200:
        # Parse and return the news data
        result = response.json()
        if 'articles' in result:
            return result['articles']
        else:
            return None  # No news found
    else:
        return f"Error: {response.status_code}, {response.text}"

def save_news_to_csv(news_articles, file_name):
    # Specify the column names for the CSV
    fieldnames = ['source', 'author', 'title', 'description', 'url', 'published_at']

    # Writing to the CSV file
    with open(file_name, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write the header
        writer.writeheader()

        # Write each news article as a row
        for article in news_articles:
            writer.writerow({
                'source': article['source']['name'],
                'author': article.get('author', 'N/A'),
                'title': article.get('title', 'N/A'),
                'description': article.get('description', 'N/A'),
                'url': article.get('url', 'N/A'),
                'published_at': article.get('publishedAt', 'N/A')
            })

# Example usage
api_key = 'bcade8f2365344dd8c0cd4e111df0b06'  # Replace with your actual News API key
company_name = 'Google'
news_articles = get_news_about_company(company_name, api_key)

if isinstance(news_articles, list):
    print(f"Found {len(news_articles)} articles.")
    save_news_to_csv(news_articles, 'company_news.csv')
else:
    print(news_articles)
