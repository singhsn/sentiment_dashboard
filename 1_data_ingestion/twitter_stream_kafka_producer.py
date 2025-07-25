import tweepy, json
from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

bearer_token = 'AAAAAAAAAAAAAAAAAAAAANro3AEAAAAATole9QajL%2Fxh9ALjaQ%2F%2BDnRJIz4%3DpA0p5lvAEynLPBFpGiCVDEp7X4P99m2owvpqVj2kcv4yLPwK58'

class StreamListener(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        # Convert tweet data to standardized format for Spark processing
        tweet_data = {
            "text": tweet.text,
            "created_at": tweet.created_at.isoformat() if tweet.created_at else "",
            "id": str(tweet.id),
            "lang": getattr(tweet, 'lang', 'en')
        }
        
        print("Tweet received:", tweet_data['text'][:100])
        producer.send("twitter-stream", tweet_data)

stream = StreamListener(bearer_token)
stream.add_rules(tweepy.StreamRule("elections OR india OR movies"))
stream.filter(tweet_fields=["created_at", "lang", "geo"])