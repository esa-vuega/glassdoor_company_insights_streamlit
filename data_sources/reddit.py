import os
import praw
import re
import spacy
import pandas as pd
from textblob import TextBlob
from dotenv import load_dotenv

load_dotenv()

nlp = spacy.load('en_core_web_sm')

SECRET_KEY = os.getenv('REDDIT-SECRET-KEY')
CLIENT_ID = os.getenv('REDDIT-CLIENT-ID')

reddit = praw.Reddit(client_id=CLIENT_ID,
                     client_secret=SECRET_KEY,
                     user_agent='Reddit-API')

subreddits = ['cscareerquestions', 'techjobs', 'Google', 'Amazon']

salary_pattern = r'(\$\d{1,3}(,\d{3})+|\d{1,3}k)'

def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity, analysis.sentiment.subjectivity

def extract_salary(text):
    return re.findall(salary_pattern, text.lower())

def extract_company_info(text, company_name):
    doc = nlp(text)
    return any(ent.text.lower() == company_name.lower() for ent in doc.ents)

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

def save_to_csv(data, filename):
    flat_data = []
    for post in data:
        for comment in post['comments']:
            flat_data.append({
                'title': post['title'],
                'selftext': post['selftext'],
                'url': post['url'],
                'upvotes': post['upvotes'],
                'post_sentiment': post['sentiment'],
                'post_salaries': post['salaries'],
                'post_company_mentions': post['company_mentions'],
                'comment_body': comment['body'],
                'comment_sentiment': comment['sentiment'],
                'comment_salaries': comment['salaries'],
                'comment_company_mentions': comment['company_mentions']
            })

    df = pd.DataFrame(flat_data)

    df.to_csv(filename, index=False)
    print(f'Data saved to {filename}')

if __name__ == "__main__":
    company_name = 'Nexer group'
    data = collect_data(company_name)
    save_to_csv(data, 'reddit_company_data.csv')
