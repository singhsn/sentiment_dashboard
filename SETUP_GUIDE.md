# Twitter Sentiment Analysis Pipeline - Complete Setup Guide

## 🛠️ **System Requirements & Installation Guide**

This guide will help you set up and run the complete Twitter sentiment analysis pipeline on your system.

## **1. 🖥️ System Requirements**

- **Operating System**: Linux, macOS, or Windows (WSL recommended for Windows)
- **RAM**: Minimum 8GB (16GB recommended for Spark processing)
- **CPU**: 4+ cores recommended for optimal performance
- **Storage**: 5GB for software + additional space for data storage
- **Python**: 3.8 or higher
- **Java**: Java 8 or 11 (required for Spark/Kafka)
- **Network**: Stable internet connection for Twitter API and AWS S3

## **2. ☕ Java Installation**

Java is required for Apache Kafka and Spark:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install openjdk-11-jdk

# macOS (with Homebrew)
brew install openjdk@11

# CentOS/RHEL
sudo yum install java-11-openjdk-devel

# Verify installation
java -version
javac -version
```

Set JAVA_HOME environment variable:
```bash
# Add to ~/.bashrc or ~/.zshrc
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64  # Ubuntu path
# export JAVA_HOME=/usr/local/opt/openjdk@11          # macOS path

# Reload environment
source ~/.bashrc  # or source ~/.zshrc
```

## **3. 🐍 Python Virtual Environment & Dependencies**

### **Step 1: Create Virtual Environment**

It's highly recommended to use a virtual environment to avoid dependency conflicts:

```bash
# Navigate to project directory
cd sentiment_dashboard-main

# Create virtual environment
python3 -m venv twitter_sentiment_env

# Activate virtual environment
# On Linux/macOS:
source twitter_sentiment_env/bin/activate

# On Windows:
# twitter_sentiment_env\Scripts\activate

# Verify virtual environment is active (you should see (twitter_sentiment_env) in your prompt)
which python
```

### **Step 2: Upgrade pip and Install Dependencies**

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install from requirements.txt (recommended)
pip install -r requirements.txt

# Or install individually if needed:
pip install tweepy kafka-python streamlit boto3 wordcloud matplotlib transformers pyspark fastapi uvicorn plotly pandas requests torch numpy scipy scikit-learn awscli
```

### **Step 3: Additional Required Dependencies**

Update your `requirements.txt` to include all necessary packages:

```txt
# Core Twitter & Kafka
tweepy>=4.14.0
kafka-python>=2.0.2

# Web Framework & API
streamlit>=1.28.0
fastapi>=0.104.0
uvicorn>=0.24.0

# AWS Integration
boto3>=1.34.0
awscli>=1.32.0

# Data Processing
pandas>=2.1.0
numpy>=1.24.0
scipy>=1.11.0

# Visualization
plotly>=5.17.0
matplotlib>=3.7.0
wordcloud>=1.9.0

# Machine Learning & NLP
transformers>=4.35.0
torch>=2.1.0
scikit-learn>=1.3.0

# Big Data Processing
pyspark>=3.5.0

# HTTP Requests
requests>=2.31.0

# Additional utilities
python-dotenv>=1.0.0
Pillow>=10.0.0
```

**Key Dependencies Explained:**
- `tweepy`: Twitter API integration
- `kafka-python`: Kafka producer/consumer
- `streamlit`: Interactive dashboard
- `transformers`: NLP sentiment analysis models
- `torch`: PyTorch backend for transformers
- `pyspark`: Big data processing
- `plotly`: Interactive visualizations
- `boto3`: AWS S3 integration
- `awscli`: AWS command line tools
- `python-dotenv`: Environment variable management
- `numpy/pandas`: Data manipulation
- `scikit-learn`: Additional ML utilities

## **4. 🔥 Apache Kafka Setup**

### **Option A: Docker Setup (Recommended - Easiest)**

1. **Install Docker and Docker Compose:**
```bash
# Ubuntu
sudo apt install docker.io docker-compose

# macOS
brew install docker docker-compose

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

2. **Create Kafka Docker Configuration:**
```bash
# Create docker-compose.yml in project root
cat > docker-compose.yml << 'EOF'
version: '3'
services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:latest
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'true'
EOF
```

3. **Start Kafka:**
```bash
# Start Kafka services
docker-compose up -d

# Verify services are running
docker-compose ps

# Create the required topic
docker exec -it $(docker ps -q --filter "ancestor=confluentinc/cp-kafka:latest") \
    kafka-topics --create --topic twitter-stream --bootstrap-server localhost:9092 \
    --partitions 3 --replication-factor 1
```

### **Option B: Manual Kafka Installation**

```bash
# Download Kafka
wget https://downloads.apache.org/kafka/2.13-3.6.0/kafka_2.13-3.6.0.tgz
tar -xzf kafka_2.13-3.6.0.tgz
cd kafka_2.13-3.6.0

# Start Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties &

# Start Kafka (in new terminal)
bin/kafka-server-start.sh config/server.properties &

# Create topic
bin/kafka-topics.sh --create --topic twitter-stream --bootstrap-server localhost:9092 \
    --partitions 3 --replication-factor 1

# Verify topic creation
bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

## **5. ⚡ Apache Spark Setup**

### **Option A: Download Pre-built Spark**
```bash
# Download Spark
cd ~
wget https://downloads.apache.org/spark/spark-3.5.0/spark-3.5.0-bin-hadoop3.tgz
tar -xzf spark-3.5.0-bin-hadoop3.tgz

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export SPARK_HOME=~/spark-3.5.0-bin-hadoop3
export PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin

# Reload environment
source ~/.bashrc
```

### **Option B: Using PySpark (Simpler)**
```bash
# PySpark is already included in requirements.txt
pip install pyspark

# Verify installation
python -c "import pyspark; print(pyspark.__version__)"
```

## **6. ☁️ AWS S3 Setup**

### **Create S3 Bucket:**
1. Go to [AWS S3 Console](https://s3.console.aws.amazon.com/)
2. Click "Create bucket"
3. Choose a unique name: `your-username-tagged-tweets` (e.g., `sachchida-tagged-tweets`)
4. Select your preferred region
5. Keep default settings and create bucket

### **Configure AWS Credentials:**
```bash
# Install AWS CLI
pip install awscli

# Configure credentials (you'll need AWS Access Key ID and Secret)
aws configure
# Enter when prompted:
# - AWS Access Key ID: [Your Access Key]
# - AWS Secret Access Key: [Your Secret Key]
# - Default region name: [e.g., us-east-1]
# - Default output format: json

# Test S3 access
aws s3 ls
```

**Getting AWS Credentials:**
1. Go to [AWS IAM Console](https://console.aws.amazon.com/iam/)
2. Create a new user with "Programmatic access"
3. Attach policy: `AmazonS3FullAccess`
4. Download the credentials CSV file

## **7. 🐦 Twitter API Setup**

### **Get Twitter Bearer Token:**
1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Sign up for a developer account if needed
3. Create a new app or use existing one
4. Go to "Keys and tokens" tab
5. Generate/copy the "Bearer Token"
6. Save this token securely

### **Twitter API Access Levels:**
- **Essential (Free)**: 500K tweets/month, good for testing
- **Elevated**: Higher limits, better for production
- **Academic Research**: Highest limits for research

## **8. 🔧 Environment Configuration**

Set up environment variables for secure configuration. You have two options:

### **Option A: Using .env File (Recommended)**

Create a `.env` file in your project root (this will be automatically loaded by `python-dotenv`):

```bash
# Create .env file in project directory
cat > .env << 'EOF'
# Twitter Sentiment Pipeline Configuration
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
TAGGED_TWEETS_BUCKET=your-s3-bucket-name

# Optional: Spark configuration
SPARK_LOCAL_IP=127.0.0.1
PYSPARK_PYTHON=python3

# AWS Configuration (optional if using aws configure)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
EOF

# Add .env to .gitignore to keep secrets safe
echo ".env" >> .gitignore
echo "twitter_sentiment_env/" >> .gitignore
```

### **Option B: System Environment Variables**

```bash
# Add to ~/.bashrc or ~/.zshrc
cat >> ~/.bashrc << 'EOF'

# Twitter Sentiment Pipeline Configuration
export TWITTER_BEARER_TOKEN="your_twitter_bearer_token_here"
export TAGGED_TWEETS_BUCKET="your-s3-bucket-name"

# Optional: Spark configuration
export SPARK_LOCAL_IP="127.0.0.1"
export PYSPARK_PYTHON=python3

EOF

# Reload environment
source ~/.bashrc

# Verify environment variables
echo $TWITTER_BEARER_TOKEN
echo $TAGGED_TWEETS_BUCKET
```

### **Environment Variable Template**

For your reference, here are all the environment variables you can configure:

```bash
# Required
TWITTER_BEARER_TOKEN=your_twitter_bearer_token_here
TAGGED_TWEETS_BUCKET=your-s3-bucket-name

# Optional AWS (if not using aws configure)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1

# Optional Spark tuning
SPARK_EXECUTOR_MEMORY=4g
SPARK_DRIVER_MEMORY=2g
SPARK_LOCAL_IP=127.0.0.1
PYSPARK_PYTHON=python3

# Optional Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

**Security Note:** Never commit real API keys to version control. Always use environment variables or `.env` files that are gitignored.

### **Environment Loading in Python Scripts**

If you're using the `.env` file option, add this code at the top of your Python scripts:

```python
# Add to the top of Python scripts to load .env file
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Now you can use os.getenv() as usual
TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
TAGGED_TWEETS_BUCKET = os.getenv('TAGGED_TWEETS_BUCKET')
```

The existing code already uses `os.getenv()`, so adding `load_dotenv()` at the top will automatically load your `.env` file.

## **9. 🧪 Testing the Complete Pipeline**

### **Step 1: Verify Infrastructure**
```bash
# Activate virtual environment first
source twitter_sentiment_env/bin/activate  # Linux/macOS
# twitter_sentiment_env\Scripts\activate   # Windows

# Test Kafka
docker-compose ps  # Should show kafka and zookeeper running

# Test AWS S3 access
aws s3 ls s3://$TAGGED_TWEETS_BUCKET

# Test Python dependencies
python -c "import tweepy, kafka, transformers, pyspark, torch; print('All imports successful')"
```

### **Step 2: Start the Pipeline Components**

Open 4 terminal windows/tabs:

#### **Terminal 1: Data Ingestion**
```bash
cd sentiment_dashboard-main

# Activate virtual environment
source twitter_sentiment_env/bin/activate  # Linux/macOS
# twitter_sentiment_env\Scripts\activate   # Windows

# Start data ingestion
python 1_data_ingestion/periodic_stream.py

# Expected output:
# Starting periodic Twitter data collection...
# API Status: 200
# Found X tweets
```

#### **Terminal 2: Sentiment Processing**
```bash
cd sentiment_dashboard-main

# Activate virtual environment
source twitter_sentiment_env/bin/activate  # Linux/macOS
# twitter_sentiment_env\Scripts\activate   # Windows

# Option A: Using spark-submit (if Spark installed)
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 2_stream_processing/spark_sentiment_processor.py

# Option B: Using Python directly (if using PySpark) - Recommended
python 2_stream_processing/spark_sentiment_processor.py

# Expected output:
# Starting Twitter sentiment analysis stream...
# Uploaded tweet with sentiment: POSITIVE/NEGATIVE/NEUTRAL
```

#### **Terminal 3: Dashboard**
```bash
cd sentiment_dashboard-main

# Activate virtual environment
source twitter_sentiment_env/bin/activate  # Linux/macOS
# twitter_sentiment_env\Scripts\activate   # Windows

# Start dashboard
streamlit run 5_visualization/app.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

#### **Terminal 4: API (Optional)**
```bash
cd sentiment_dashboard-main

# Activate virtual environment
source twitter_sentiment_env/bin/activate  # Linux/macOS
# twitter_sentiment_env\Scripts\activate   # Windows

# Start API server
uvicorn 4_api_layer.api:app --reload

# Expected output:
# INFO: Uvicorn running on http://127.0.0.1:8000
```

### **Step 3: Verify Data Flow**

1. **Check Kafka topics:**
```bash
docker exec -it $(docker ps -q --filter "ancestor=confluentinc/cp-kafka:latest") \
    kafka-console-consumer --topic twitter-stream --bootstrap-server localhost:9092 --from-beginning
```

2. **Check S3 bucket:**
```bash
aws s3 ls s3://$TAGGED_TWEETS_BUCKET/tagged/ --recursive
```

3. **Open Dashboard:**
   - Go to `http://localhost:8501`
   - Should see sentiment metrics and charts

## **10. 🔍 Troubleshooting**

### **Common Issues and Solutions:**

#### **Java Issues:**
```bash
# Error: JAVA_HOME not set
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Error: Java version incompatible
java -version  # Should be 8 or 11
```

#### **Kafka Issues:**
```bash
# Error: Connection refused to localhost:9092
docker-compose ps  # Check if kafka is running
docker-compose logs kafka  # Check kafka logs

# Error: Topic doesn't exist
docker exec -it kafka-container kafka-topics --list --bootstrap-server localhost:9092
```

#### **AWS/S3 Issues:**
```bash
# Error: Unable to locate credentials
aws configure list
aws s3 ls  # Test basic access

# Error: Access denied
# Check IAM permissions - user needs S3 access
```

#### **Python/Dependencies Issues:**
```bash
# Error: Module not found
pip install -r requirements.txt
python -c "import problematic_module"

# Error: Memory issues with transformers
# Increase system RAM or reduce batch size in spark_sentiment_processor.py
```

#### **Twitter API Issues:**
```bash
# Error: 401 Unauthorized
# Check if bearer token is correct and active

# Error: 429 Rate limit exceeded
# Wait 15 minutes or upgrade Twitter API plan
```

### **Performance Optimization:**

```bash
# Increase Spark memory (if you have enough RAM)
export SPARK_EXECUTOR_MEMORY=6g
export SPARK_DRIVER_MEMORY=4g

# Monitor system resources
htop  # Check CPU/RAM usage
docker stats  # Check Docker container resources
```

## **11. 📋 Quick Setup Script**

Save this as `setup.sh` for automated setup:

```bash
#!/bin/bash
set -e

echo "🚀 Setting up Twitter Sentiment Analysis Pipeline..."

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv twitter_sentiment_env

# Activate virtual environment
echo "📝 Activating virtual environment..."
source twitter_sentiment_env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create .gitignore if it doesn't exist
echo "📄 Setting up .gitignore..."
if [ ! -f .gitignore ]; then
    touch .gitignore
fi

# Add entries to .gitignore
grep -qxF ".env" .gitignore || echo ".env" >> .gitignore
grep -qxF "twitter_sentiment_env/" .gitignore || echo "twitter_sentiment_env/" >> .gitignore

# Setup Kafka with Docker
echo "🔥 Setting up Kafka..."
docker-compose up -d

# Wait for Kafka to start
echo "⏳ Waiting for Kafka to initialize..."
sleep 30

# Create Kafka topic
echo "📝 Creating Kafka topic..."
docker exec -it $(docker ps -q --filter "ancestor=confluentinc/cp-kafka:latest") \
    kafka-topics --create --topic twitter-stream --bootstrap-server localhost:9092 \
    --partitions 3 --replication-factor 1 --if-not-exists

echo "✅ Setup complete!"
echo ""
echo "🔧 Don't forget to:"
echo "1. Create .env file with your credentials:"
echo "   TWITTER_BEARER_TOKEN=your_token"
echo "   TAGGED_TWEETS_BUCKET=your_bucket"
echo "2. Configure AWS credentials: aws configure"
echo "3. Create S3 bucket in AWS console"
echo ""
echo "🚀 Start the pipeline (remember to activate venv first):"
echo "   source twitter_sentiment_env/bin/activate"
echo "   Terminal 1: python 1_data_ingestion/periodic_stream.py"
echo "   Terminal 2: python 2_stream_processing/spark_sentiment_processor.py"
echo "   Terminal 3: streamlit run 5_visualization/app.py"
```

Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

## **12. 📊 Resource Requirements Summary**

| Component | CPU | RAM | Storage | Network |
|-----------|-----|-----|---------|---------|
| Kafka | 1 core | 2GB | 1GB | Minimal |
| Spark | 2-4 cores | 4-8GB | 1GB | Minimal |
| Transformers Model | 1-2 cores | 2-4GB | 2GB | Download only |
| Dashboard | 1 core | 1GB | Minimal | S3 access |
| **Total Recommended** | **4+ cores** | **8-16GB** | **5GB** | **Stable internet** |

## **13. 🎯 Success Indicators**

Your pipeline is working correctly when you see:

1. ✅ **Data Ingestion**: "Found X tweets" messages in terminal 1
2. ✅ **Sentiment Processing**: "Uploaded tweet with sentiment: POSITIVE/NEGATIVE/NEUTRAL" in terminal 2
3. ✅ **S3 Storage**: Files appearing in your S3 bucket under `tagged/YYYY/MM/DD/`
4. ✅ **Dashboard**: Real-time metrics and charts at `http://localhost:8501`
5. ✅ **API**: JSON responses at `http://localhost:8000/sentiment/`

## **14. 🔄 Daily Operations**

### **Starting the Pipeline:**
```bash
# Start infrastructure
docker-compose up -d

# Start pipeline components (in separate terminals)
python 1_data_ingestion/periodic_stream.py &
python 2_stream_processing/spark_sentiment_processor.py &
streamlit run 5_visualization/app.py

# Monitor logs
tail -f /tmp/spark-checkpoint/  # Spark logs
docker-compose logs -f kafka    # Kafka logs
```

### **Stopping the Pipeline:**
```bash
# Stop Python processes
pkill -f "periodic_stream.py"
pkill -f "spark_sentiment_processor.py"
pkill -f "streamlit"

# Stop infrastructure
docker-compose down
```

### **Monitoring:**
```bash
# Check S3 usage
aws s3 ls s3://$TAGGED_TWEETS_BUCKET/tagged/ --recursive --summarize

# Check Kafka topics
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Monitor system resources
htop
docker stats
```

**🎉 You're now ready to run a complete real-time Twitter sentiment analysis pipeline!** 