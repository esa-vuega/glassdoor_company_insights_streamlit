import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('YOUTUBE-API-KEY')

youtube = build('youtube', 'v3', developerKey=api_key)

# Define the company you want to search for
company_name = "Tesla"  # Replace with any company name

# Step 1: Search for channels related to the company name
channel_search_request = youtube.search().list(
    q=company_name,
    part="snippet",
    type="channel",
    maxResults=1  # We're only interested in the first (most relevant) result
)
channel_search_response = channel_search_request.execute()

# Step 2: Extract the channelId of the first result
if channel_search_response['items']:
    channel_id = channel_search_response['items'][0]['snippet']['channelId']
    print(f"Found Channel ID: {channel_id}")
else:
    print(f"No channel found for {company_name}")
    exit()

# Step 3: Use the channelId to fetch detailed statistics for the channel
channel_request = youtube.channels().list(
    part="snippet,contentDetails,statistics",
    id=channel_id  # Use the found channelId
)
channel_response = channel_request.execute()

# Step 4: Extract and display channel statistics
for channel in channel_response['items']:
    print(f"Channel Title: {channel['snippet']['title']}")
    print(f"Subscribers: {channel['statistics']['subscriberCount']}")
    print(f"Total Views: {channel['statistics']['viewCount']}")
    print(f"Video Count: {channel['statistics']['videoCount']}")
    print(f"Channel Description: {channel['snippet']['description']}")
