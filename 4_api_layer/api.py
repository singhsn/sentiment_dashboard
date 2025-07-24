from fastapi import FastAPI
import boto3, json
from typing import List

app = FastAPI()
s3 = boto3.client('s3')
BUCKET = "your-tagged-tweets-bucket"

@app.get("/sentiment/")
def get_sentiment():
    response = s3.list_objects_v2(Bucket=BUCKET, Prefix="tagged/")
    tweets = []
    for obj in response.get('Contents', [])[-20:]:
        content = s3.get_object(Bucket=BUCKET, Key=obj['Key'])['Body'].read()
        tweets.append(json.loads(content))
    return tweets