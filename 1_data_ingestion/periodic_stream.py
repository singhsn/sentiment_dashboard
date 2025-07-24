import time
import requests
import json
from kafka import KafkaProducer

BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAANro3AEAAAAATole9QajL%2Fxh9ALjaQ%2F%2BDnRJIz4%3DpA0p5lvAEynLPBFpGiCVDEp7X4P99m2owvpqVj2kcv4yLPwK58'

headers = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

url = "https://api.twitter.com/2/tweets/search/recent"

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

while True:
    params = {
        "query": "india OR elections OR movies",
        "max_results": 100,
        "tweet.fields": "created_at,text"
    }

    response = requests.get(url, headers=headers, params=params)

    print(f"Status: {response.status_code}")

    if response.status_code == 429:
        print("Rate limit hit. Sleeping for 15 minutes...")
        time.sleep(900)
        continue

    if response.status_code != 200:
        print("Error:", response.text)
        break

    data = response.json()
    tweets = data.get("data", [])

    if not tweets:
        print("No new tweets at this moment.")
    else:
        for tweet in tweets:
            print(f"[{tweet['created_at']}] {tweet['text']}\n")
            producer.send("twitter-stream", tweet)

    print("Waiting 60 seconds...\n")
    time.sleep(60)




