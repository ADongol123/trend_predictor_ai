from googleapiclient.discovery import build
import csv
import time
from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Get the YouTube API key from the environment variable
api_key = os.getenv('YOUTUBE_API_KEY')

if api_key is None:
    raise ValueError("API Key not found. Make sure it's in your .env file.")

# Build the YouTube API client
youtube = build('youtube', 'v3', developerKey=api_key)

# Load previous view counts from a CSV file
def load_previous_view_counts(filename):
    previous_views = {}
    try:
        with open(filename, 'r', newline='', encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header row
            for row in reader:
                video_id = row[1].split('v=')[-1]
                views = int(row[2])  # Previous views
                previous_views[video_id] = views
    except FileNotFoundError:
        print(f"File {filename} not found.")
    return previous_views

# Function to fetch trending videos
def get_trending_videos():
    videos = []
    nextPageToken = None
    while len(videos) < 100000:
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            regionCode="US",
            maxResults=50,
            pageToken=nextPageToken
        )
        response = request.execute()
        videos.extend(response['items'])
        nextPageToken = response.get('nextPageToken')
        time.sleep(1)
        if not nextPageToken:
            break
    return videos

# Function to calculate the view increase rate
def calculate_view_rate(current_views, previous_views):
    if previous_views == 0:
        return 0
    return (current_views - previous_views) / previous_views * 100

# Save the results to a CSV file
def save_to_csv(videos, previous_views_dict):
    with open("../data/raw/youtube_trending_with_rate.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Video URL", "Current Views", "Previous Views", "View Increase Rate (%)", "Likes", "Comments", "Published At"])
        
        for video in videos:
            title = video['snippet']['title']
            url = f"https://www.youtube.com/watch?v={video['id']}"
            current_views = int(video['statistics'].get('viewCount', 0))
            previous_views = previous_views_dict.get(video['id'], 0)
            view_rate = calculate_view_rate(current_views, previous_views)
            likes = video['statistics'].get('likeCount', 'N/A')
            comments = video['statistics'].get('commentCount', 'N/A')
            published_at = video['snippet']['publishedAt']

            writer.writerow([title, url, current_views, previous_views, view_rate, likes, comments, published_at])
            previous_views_dict[video['id']] = current_views

    print(f"YouTube trending videos with view rate saved to youtube_trending_with_rate.csv")

# Main script
previous_views_dict = load_previous_view_counts("../data/raw/youtube_trending.csv")
trending_videos = get_trending_videos()
save_to_csv(trending_videos, previous_views_dict)
