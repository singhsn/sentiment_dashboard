from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, from_json
from pyspark.sql.types import StringType, StructType, StructField
import json
import os

# Initialize Spark with more memory for transformers
spark = SparkSession.builder \
    .master("local[*]") \
    .appName("TwitterSentiment") \
    .config("spark.jars.packages",
            "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,"
            "org.apache.kafka:kafka-clients:3.5.0") \
    .getOrCreate()

# Configure S3 bucket name (can be set via environment variable)
S3_BUCKET = os.getenv('TAGGED_TWEETS_BUCKET', 'pgd-cleaned-tweets')

# Read from Kafka
df = spark.readStream.format("kafka") \
    .option("subscribe", "twitter-stream") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .load()

# Define schema for tweet data (handles both periodic and streaming formats)
tweet_schema = StructType([
    StructField("text", StringType(), True),
    StructField("created_at", StringType(), True),
    StructField("id", StringType(), True),
    StructField("lang", StringType(), True)
])

# Convert Kafka value to string and parse JSON
df = df.withColumn("value_str", col("value").cast("string"))
df = df.withColumn("tweet_data", from_json(col("value_str"), tweet_schema))

# Extract tweet text - handle both formats
df = df.withColumn("tweet_text", col("tweet_data.text"))
df = df.filter(col("tweet_text").isNotNull())

# Sentiment analysis function (using a simpler approach to avoid serialization issues)
def get_sentiment_batch(texts):
    """Process sentiment for a batch of texts"""
    try:
        from transformers import pipeline
        sentiment_analyzer = pipeline("sentiment-analysis", 
                                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                                    truncation=True, 
                                    max_length=512)
        
        results = []
        for text in texts:
            if text and len(text.strip()) > 0:
                try:
                    result = sentiment_analyzer(text[:512])  # Limit text length
                    sentiment = result[0]['label'] if result else 'NEUTRAL'
                    # Normalize sentiment labels
                    if sentiment in ['LABEL_0', 'NEGATIVE']:
                        sentiment = 'NEGATIVE'
                    elif sentiment in ['LABEL_1', 'NEUTRAL']:
                        sentiment = 'NEUTRAL'
                    elif sentiment in ['LABEL_2', 'POSITIVE']:
                        sentiment = 'POSITIVE'
                    results.append(sentiment)
                except Exception as e:
                    print(f"Error processing text: {e}")
                    results.append('NEUTRAL')
            else:
                results.append('NEUTRAL')
        return results
    except Exception as e:
        print(f"Error in sentiment analysis: {e}")
        return ['NEUTRAL'] * len(texts)

def write_to_s3(batch_df, batch_id):
    """Write batch of tweets with sentiment to S3"""
    try:
        import boto3
        import uuid
        from datetime import datetime
        
        s3 = boto3.client('s3')
        
        # Collect all tweets in the batch
        rows = batch_df.collect()
        
        if not rows:
            print(f"Batch {batch_id}: No data to process")
            return
            
        # Extract texts for batch sentiment analysis
        texts = [row['tweet_text'] for row in rows]
        sentiments = get_sentiment_batch(texts)
        
        # Upload each tweet with sentiment
        for i, row in enumerate(rows):
            try:
                tweet_obj = {
                    "text": row['tweet_text'],
                    "sentiment": sentiments[i],
                    "created_at": row['tweet_data']['created_at'] if row['tweet_data'] else None,
                    "processed_at": datetime.utcnow().isoformat(),
                    "tweet_id": row['tweet_data']['id'] if row['tweet_data'] else str(uuid.uuid4())
                }
                
                # Create organized S3 key with date partition
                date_str = datetime.utcnow().strftime('%Y/%m/%d')
                key = f"tagged/{date_str}/{uuid.uuid4()}.json"
                
                s3.put_object(
                    Bucket=S3_BUCKET, 
                    Key=key, 
                    Body=json.dumps(tweet_obj),
                    ContentType='application/json'
                )
                
                print(f"Uploaded tweet with sentiment: {sentiments[i]}")
                
            except Exception as e:
                print(f"Error uploading tweet {i}: {e}")
                
        print(f"Batch {batch_id}: Processed {len(rows)} tweets")
        
    except Exception as e:
        print(f"Error in write_to_s3 for batch {batch_id}: {e}")

# Start the streaming query
query = df.writeStream \
    .foreachBatch(write_to_s3) \
    .option("checkpointLocation", "/tmp/spark-checkpoint") \
    .start()

print("Starting Twitter sentiment analysis stream...")
print(f"Writing to S3 bucket: {S3_BUCKET}")

query.awaitTermination()