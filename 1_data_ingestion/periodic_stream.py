import time
import requests
import json
from kafka import KafkaProducer
import os

# Get configuration from environment variables
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', 'AAAAAAAAAAAAAAAAAAAAANro3AEAAAAATole9QajL%2Fxh9ALjaQ%2F%2BDnRJIz4%3DpA0p5lvAEynLPBFpGiCVDEp7X4P99m2owvpqVj2kcv4yLPwK58')

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

url = "https://api.twitter.com/2/tweets/search/recent"

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def normalize_tweet_format(tweet_data):
    """Normalize tweet data to standard format"""
    return {
        "text": tweet_data.get("text", ""),
        "created_at": tweet_data.get("created_at", ""),
        "id": tweet_data.get("id", ""),
        "lang": tweet_data.get("lang", "en")
    }

print("Starting periodic Twitter data collection...")
print("Searching for: india OR elections OR movies")

while True:
    try:
        params = {
            "query": "india OR elections OR movies",
            "max_results": 5,
            "tweet.fields": "created_at,text,lang,public_metrics"
        }

        response = requests.get(url, headers=headers, params=params)
        print(f"API Status: {response.status_code}")

        if response.status_code == 429:
            print("Rate limit hit. Sleeping for 15 minutes...")
            time.sleep(900)
            continue

        if response.status_code == 401:
            print("Authentication error. Please check your bearer token.")
            break

        if response.status_code != 200:
            print("Error:", response.text)
            print("Retrying in 5 minutes...")
            time.sleep(300)
            continue

        data = response.json()
        tweets = data.get("data", [])

        if not tweets:
            print("No new tweets at this moment.")
        else:
            print(f"Found {len(tweets)} tweets")
            
            for tweet in tweets:
                try:
                    # Normalize tweet format
                    normalized_tweet = normalize_tweet_format(tweet)
                    
                    # Send to Kafka
                    producer.send("twitter-stream", normalized_tweet)
                    
                    print(f"[{normalized_tweet['created_at']}] {normalized_tweet['text'][:100]}...")
                    
                except Exception as e:
                    print(f"Error processing tweet: {e}")
                    continue

        print("Waiting 60 seconds...\n")
        time.sleep(60)
        
    except KeyboardInterrupt:
        print("Stopping data collection...")
        break
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Retrying in 60 seconds...")
        time.sleep(60)

producer.close()
print("Data collection stopped.")




