import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
API_KEY = os.getenv('X_API_KEY')
API_SECRET_KEY = os.getenv('X_API_SECRET_KEY')
ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')
# Authenticate to Twitter API using OAuth 1.0a
auth = tweepy.OAuth1UserHandler(
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET
)
api = tweepy.API(auth)

# Fetch tweets using Twitter API v1.1
def fetch_company_tweets(query, count=10):
    tweets = []
    for tweet in tweepy.Cursor(api.search_tweets, q=query, lang="en", tweet_mode="extended").items(count):
        tweets.append({
            'created_at': tweet.created_at,
            'text': tweet.full_text,
            'user': tweet.user.screen_name
        })
    return tweets

# Example: Fetch tweets mentioning a company
company_tweets = fetch_company_tweets("Microsoft", count=1)

for tweet in company_tweets:
    print(f"{tweet['created_at']} - {tweet['user']}: {tweet['text']}")