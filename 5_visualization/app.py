import streamlit as st
import boto3, json
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

TAGGED_BUCKET = "your-tagged-tweets-bucket"

st.title("📈 Real-Time Twitter Sentiment Dashboard")

s3 = boto3.client('s3')
response = s3.list_objects_v2(Bucket=TAGGED_BUCKET, Prefix="tagged/")
all_objs = response.get('Contents', [])

tweets = []
for obj in all_objs[-100:]:
    content = s3.get_object(Bucket=TAGGED_BUCKET, Key=obj['Key'])['Body'].read()
    tweet = json.loads(content)
    tweets.append(tweet)

df = pd.DataFrame(tweets)

st.subheader("Sentiment Distribution")
st.bar_chart(df['sentiment'].value_counts())

st.subheader("Latest Tweets")
st.dataframe(df[['text', 'sentiment']].tail(10))

st.subheader("WordCloud (Positive Tweets)")
positive_text = " ".join(df[df["sentiment"] == "POSITIVE"]['text'].values)
wc = WordCloud(width=800, height=300).generate(positive_text)
st.image(wc.to_array())