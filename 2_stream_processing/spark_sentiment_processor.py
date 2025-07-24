from pyspark.sql import SparkSession
from transformers import pipeline
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType
import json

spark = SparkSession.builder     .appName("TwitterSentiment")     .getOrCreate()

df = spark.readStream.format("kafka") \
    .option("subscribe", "twitter-stream") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .load()

to_text = udf(lambda x: x.decode('utf-8'), StringType())
df = df.withColumn("tweet", to_text(col("value")))

sentiment_pipe = pipeline("sentiment-analysis")
predict_sentiment = udf(lambda text: sentiment_pipe(text)[0]['label'], StringType())
df = df.withColumn("sentiment", predict_sentiment("tweet"))

def write_to_s3(batch_df, batch_id):
    for row in batch_df.collect():
        import boto3, uuid
        s3 = boto3.client('s3')
        tweet_obj = {"text": row['tweet'], "sentiment": row['sentiment']}
        key = f"tagged/{uuid.uuid4()}.json"
        s3.put_object(Bucket="your-tagged-tweets-bucket", Key=key, Body=json.dumps(tweet_obj))

df.writeStream.foreachBatch(write_to_s3).start().awaitTermination()