import boto3, json
from datetime import datetime
import uuid

s3 = boto3.client('s3')
RAW_BUCKET = "your-raw-tweets-bucket"
TAGGED_BUCKET = "your-tagged-tweets-bucket"

def upload_raw_tweet(tweet):
    key = f"raw/{datetime.utcnow().date()}/{uuid.uuid4()}.json"
    s3.put_object(Bucket=RAW_BUCKET, Key=key, Body=json.dumps(tweet))

def upload_tagged_tweet(tweet, sentiment):
    tweet["sentiment"] = sentiment
    key = f"tagged/{datetime.utcnow().date()}/{uuid.uuid4()}.json"
    s3.put_object(Bucket=TAGGED_BUCKET, Key=key, Body=json.dumps(tweet))