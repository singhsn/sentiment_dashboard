# Real-Time Twitter Sentiment Dashboard (PGD Project)

## Setup Steps (Local)

### 1. Requirements

```bash
pip install tweepy kafka-python streamlit boto3 wordcloud matplotlib transformers pyspark
```

### 2. Kafka

- Start Kafka locally using Docker or from binaries.
- Create topic:
```bash
kafka-topics.sh --create --topic twitter-stream --bootstrap-server localhost:9092
```

### 3. AWS S3 Setup

- Create 2 buckets on https://s3.console.aws.amazon.com/
  - your-raw-tweets-bucket
  - your-tagged-tweets-bucket

- Create IAM user with `AmazonS3FullAccess`, then configure:
```bash
aws configure
```

### 4. Run Modules

```bash
# Ingestion
python 1_data_ingestion/twitter_stream_kafka_producer.py

# Spark Streaming
spark-submit 2_stream_processing/spark_sentiment_processor.py

# API
uvicorn 4_api_layer.api:app --reload

# Dashboard
streamlit run 5_visualization/app.py
```