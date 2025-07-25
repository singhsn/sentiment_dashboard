import streamlit as st
import boto3, json
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Configuration
TAGGED_BUCKET = os.getenv('TAGGED_TWEETS_BUCKET', 'sachchida-tagged-tweets')

st.set_page_config(page_title="Twitter Sentiment Dashboard", page_icon="📈", layout="wide")
st.title("📈 Real-Time Twitter Sentiment Dashboard")

@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_tweet_data():
    """Load tweet data from S3 with error handling"""
    try:
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=TAGGED_BUCKET, Prefix="tagged/")
        all_objs = response.get('Contents', [])
        
        if not all_objs:
            return pd.DataFrame()
        
        tweets = []
        # Get last 200 tweets for better analysis
        for obj in sorted(all_objs, key=lambda x: x['LastModified'])[-200:]:
            try:
                content = s3.get_object(Bucket=TAGGED_BUCKET, Key=obj['Key'])['Body'].read()
                tweet = json.loads(content)
                tweets.append(tweet)
            except Exception as e:
                st.sidebar.warning(f"Error loading tweet: {e}")
                continue
        
        return pd.DataFrame(tweets)
    
    except Exception as e:
        st.error(f"Error connecting to S3: {e}")
        return pd.DataFrame()

# Load data
df = load_tweet_data()

if df.empty:
    st.warning("No tweet data available. Make sure the data pipeline is running and S3 bucket is configured.")
    st.info(f"Expected S3 bucket: `{TAGGED_BUCKET}`")
else:
    # Convert timestamp if available
    if 'processed_at' in df.columns:
        df['processed_at'] = pd.to_datetime(df['processed_at'])
    
    # Sidebar controls
    st.sidebar.header("Dashboard Controls")
    
    # Sentiment filter
    sentiment_filter = st.sidebar.multiselect(
        "Filter by Sentiment:",
        options=df['sentiment'].unique() if 'sentiment' in df.columns else [],
        default=df['sentiment'].unique() if 'sentiment' in df.columns else []
    )
    
    if sentiment_filter:
        df_filtered = df[df['sentiment'].isin(sentiment_filter)]
    else:
        df_filtered = df
    
    # Time range filter
    if 'processed_at' in df.columns:
        time_options = {
            "Last Hour": timedelta(hours=1),
            "Last 6 Hours": timedelta(hours=6), 
            "Last Day": timedelta(days=1),
            "All Time": None
        }
        
        time_filter = st.sidebar.selectbox("Time Range:", list(time_options.keys()))
        
        if time_options[time_filter]:
            cutoff_time = datetime.now() - time_options[time_filter]
            df_filtered = df_filtered[df_filtered['processed_at'] >= cutoff_time]
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tweets", len(df_filtered))
    with col2:
        if 'sentiment' in df_filtered.columns:
            positive_pct = (df_filtered['sentiment'] == 'POSITIVE').mean() * 100
            st.metric("Positive %", f"{positive_pct:.1f}%")
    with col3:
        if 'sentiment' in df_filtered.columns:
            negative_pct = (df_filtered['sentiment'] == 'NEGATIVE').mean() * 100
            st.metric("Negative %", f"{negative_pct:.1f}%")
    with col4:
        if 'sentiment' in df_filtered.columns:
            neutral_pct = (df_filtered['sentiment'] == 'NEUTRAL').mean() * 100
            st.metric("Neutral %", f"{neutral_pct:.1f}%")
    
    # Charts in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sentiment Distribution")
        if 'sentiment' in df_filtered.columns and not df_filtered.empty:
            sentiment_counts = df_filtered['sentiment'].value_counts()
            fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index,
                        color_discrete_map={'POSITIVE': '#28a745', 'NEGATIVE': '#dc3545', 'NEUTRAL': '#6c757d'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No sentiment data available")
    
    with col2:
        st.subheader("Sentiment Over Time")
        if 'processed_at' in df_filtered.columns and 'sentiment' in df_filtered.columns and not df_filtered.empty:
            df_filtered['hour'] = df_filtered['processed_at'].dt.floor('H')
            hourly_sentiment = df_filtered.groupby(['hour', 'sentiment']).size().unstack(fill_value=0)
            
            if not hourly_sentiment.empty:
                fig = px.line(hourly_sentiment, title="Sentiment Trends")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough time data for trends")
        else:
            st.info("Time data not available")
    
    # Latest Tweets
    st.subheader("Latest Tweets")
    if not df_filtered.empty:
        display_cols = ['text', 'sentiment']
        if 'processed_at' in df_filtered.columns:
            display_cols.append('processed_at')
        
        latest_tweets = df_filtered[display_cols].tail(10).sort_index(ascending=False)
        st.dataframe(latest_tweets, use_container_width=True)
    else:
        st.info("No tweets to display")
    
    # Word Clouds
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("WordCloud - Positive Tweets")
        if 'sentiment' in df_filtered.columns:
            positive_tweets = df_filtered[df_filtered["sentiment"] == "POSITIVE"]
            if not positive_tweets.empty and 'text' in positive_tweets.columns:
                positive_text = " ".join(positive_tweets['text'].astype(str).values)
                if positive_text.strip():
                    wc = WordCloud(width=400, height=200, background_color='white').generate(positive_text)
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                else:
                    st.info("No positive tweets to generate word cloud")
            else:
                st.info("No positive tweets available")
    
    with col2:
        st.subheader("WordCloud - Negative Tweets") 
        if 'sentiment' in df_filtered.columns:
            negative_tweets = df_filtered[df_filtered["sentiment"] == "NEGATIVE"]
            if not negative_tweets.empty and 'text' in negative_tweets.columns:
                negative_text = " ".join(negative_tweets['text'].astype(str).values)
                if negative_text.strip():
                    wc = WordCloud(width=400, height=200, background_color='white').generate(negative_text)
                    fig, ax = plt.subplots(figsize=(8, 4))
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                else:
                    st.info("No negative tweets to generate word cloud")
            else:
                st.info("No negative tweets available")

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Dashboard refreshes every 60 seconds")
st.sidebar.info(f"Data source: S3 bucket `{TAGGED_BUCKET}`")