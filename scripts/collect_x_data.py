import tweepy
import csv
from datetime import datetime 

import time


API_KEY =  "cBwXV0lXAAbYdXgMdNgfq34xk"
API_SECERET_KEY =  "DpY9QJIWmo8zoBejyuVv8BLjkY8CG0hvAIxWTgqOk9VVyiON4J"
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAE6xzwEAAAAADdO0NJj119rP%2FFspnkojnLET8ao%3DYBFeQHSfWTtC3XtlvSwNrFb9dynIKbJlnJlAu4XiSphokEA37o"


# Your Bearer Token
bearer_token = "your_bearer_token_here"

# Authenticate
client = tweepy.Client(bearer_token=bearer_token)

# Define categories with fewer keywords (to avoid hitting limits)
categories = {
    "Sports": ["#FIFA", "#NBA"],
    "Fashion": ["#fashion", "#style"],
    "Politics": ["#Elections", "#Politics"],
    "Technology": ["#AI", "#MachineLearning"],
    "Entertainment": ["#Hollywood", "#Netflix"]
}

# Open CSV file
with open("trending_topics.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Category", "Keyword", "Text", "Likes", "Retweets", "Timestamp"])
    
    # Loop through categories (rate-limited to avoid 429 errors)
    for category, keywords in categories.items():
        for keyword in keywords:
            print(f"Fetching tweets for {category} - {keyword}...")
            try:
                tweets = client.search_recent_tweets(
                    query=f"{keyword} -is:retweet",
                    max_results=10,  # Reduce requests to stay within limits
                    tweet_fields=["created_at", "public_metrics"]
                )
                if tweets.data:
                    for tweet in tweets.data:
                        writer.writerow([category, keyword, tweet.text, 
                                         tweet.public_metrics["like_count"], 
                                         tweet.public_metrics["retweet_count"], 
                                         tweet.created_at])
                else:
                    print(f"No tweets found for {keyword}.")
                
                # **Avoid hitting rate limits by waiting 15 seconds between calls**
                time.sleep(15)
            
            except tweepy.TooManyRequests:
                print("Rate limit reached! Waiting for 15 minutes before retrying...")
                time.sleep(900)  # 15 minutes cooldown
            except Exception as e:
                print(f"Error fetching {keyword}: {e}")

print("Trending topics data saved to trending_topics.csv")
