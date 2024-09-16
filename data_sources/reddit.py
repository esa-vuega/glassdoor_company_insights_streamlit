import os
import praw
from textblob import TextBlob
import re
import spacy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load spacy model for advanced text processing
nlp = spacy.load('en_core_web_sm')

# Reddit API credentials
SECRET_KEY = os.getenv('REDDIT-SECRET-KEY')
CLIENT_ID = os.getenv('REDDIT-CLIENT-ID')

# Reddit API client setup
reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=SECRET_KEY,
                     user_agent='Reddit-API')

# Define subreddits to analyze
subreddits = ['cscareerquestions', 'techjobs', 'Google', 'Amazon']

# Regex pattern to capture salary information (e.g., "$120,000", "120k")
salary_pattern = r'(\$\d{1,3}(,\d{3})+|\d{1,3}k)'

# Function to analyze sentiment using TextBlob
def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity, analysis.sentiment.subjectivity

# Function to extract salary information from text
def extract_salary(text):
    return re.findall(salary_pattern, text.lower())

# Function to detect company name mention in text
def extract_company_info(text, company_name):
    doc = nlp(text)
    return any(ent.text.lower() == company_name.lower() for ent in doc.ents)

# Function to collect Reddit posts and comments data
def collect_data(company_name):
    posts_data = []

    for subreddit_name in subreddits:
        subreddit = reddit.subreddit(subreddit_name)

        for submission in subreddit.top('week', limit=20):
            post_info = {
                'title': submission.title,
                'selftext': submission.selftext,
                'url': submission.url,
                'upvotes': submission.score,
                'sentiment': analyze_sentiment(submission.title + ' ' + submission.selftext),
                'salaries': extract_salary(submission.title + ' ' + submission.selftext),
                'company_mentions': extract_company_info(submission.title + ' ' + submission.selftext, company_name)
            }

            # Collect comments data
            comments = submission.comments[:20]
            post_info['comments'] = []
            for comment in comments:
                if isinstance(comment, praw.models.MoreComments):
                    continue

                comment_data = {
                    'body': comment.body,
                    'sentiment': analyze_sentiment(comment.body),
                    'salaries': extract_salary(comment.body),
                    'company_mentions': extract_company_info(comment.body, company_name)
                }
                post_info['comments'].append(comment_data)

            posts_data.append(post_info)

    return posts_data
