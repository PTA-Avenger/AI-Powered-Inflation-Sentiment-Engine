# AI-Powered Inflation Sentiment Engine

A production-grade NLP pipeline that analyzes South African financial news and social media sentiment to gauge public perception of the Rand (ZAR) and inflation. 

## 🎯 Project Overview

This system demonstrates how to:
1. **Scrape** financial data from multiple sources (news APIs, Twitter/X)
2. **Analyze** sentiment using FinBERT financial language model
3. **Store** results in PostgreSQL with structured data models
4. **Serve** sentiment data via a Model Context Protocol (MCP) server
5. **Deploy** as AWS Lambda serverless functions for cost efficiency

## 📋 Architecture

```
┌─────────────────────────────────────────────┐
│         Data Sources                        │
│  ┌──────────────┐      ┌──────────────┐    │
│  │  NewsAPI     │      │  Twitter API │    │
│  └──────────────┘      └──────────────┘    │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  AWS Lambda (Scheduled Trigger)             │
│  - Scrape data                              │
│  - Run sentiment analysis                   │
│  - Store results                            │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  PostgreSQL Database                        │
│  - Articles table                           │
│  - Sentiment analysis results               │
│  - Aggregated metrics                       │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  MCP Server (FastAPI)                       │
│  - Secure LLM database access               │
│  - Query APIs for sentiment data            │
│  - Real-time trending analysis              │
└─────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│  Local/Cloud LLMs                           │
│  - Access sentiment data securely           │
│  - Generate policy insights                 │
│  - Monitor ZAR & inflation trends           │
└─────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone/setup the project
cd "AI-Powered Inflation Sentiment Engine"

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
```

### 2. Configure Credentials

Edit `.env` with your credentials:

```env
# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/inflation_sentiment

# Twitter API v2 (https://developer.twitter.com)
TWITTER_BEARER_TOKEN=your_bearer_token

# NewsAPI (https://newsapi.org)
NEWS_API_KEY=your_news_api_key

# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# MCP Server
MCP_SECRET_KEY=your_secret_key_change_in_production
```

### 3. Setup Database

```bash
# Create PostgreSQL database
createdb inflation_sentiment

# Initialize tables
python -c "from database import init_db; from config import get_settings; init_db(get_settings().database_url)"
```

### 4. Run Locally

**Option A: Full Pipeline**
```bash
python main.py
```

**Option B: MCP Server Only**
```bash
python run_mcp_server.py
# Visit: http://localhost:8000/docs (Swagger UI)
#        http://localhost:8000/docs-mcp (MCP docs)
```

## 📁 Project Structure

```
AI-Powered Inflation Sentiment Engine/
├── config/                    # Configuration management
│   ├── settings.py           # Settings with environment variables
│   └── __init__.py
├── database/                 # Data layer
│   ├── models.py            # SQLAlchemy ORM models
│   ├── repository.py        # Repository pattern for data access
│   └── __init__.py
├── scrapers/                # Data collection
│   ├── news_scraper.py      # Financial news scraper
│   ├── twitter_scraper.py   # Twitter/X data scraper
│   └── __init__.py
├── sentiment/               # NLP analysis
│   ├── analyzer.py          # FinBERT sentiment analysis
│   └── __init__.py
├── aws_lambda/              # Serverless deployment
│   ├── handler.py           # Lambda entry point
│   └── __init__.py
├── mcp_server/              # MCP Protocol implementation
│   ├── sentiment_server.py  # Core MCP server
│   ├── app.py              # FastAPI wrapper for local testing
│   └── __init__.py
├── utils/                   # Utilities
│   ├── logging.py          # Structured logging
│   └── __init__.py
├── tests/                   # Test suite
│   ├── test_sentiment.py    # Sentiment analyzer tests
│   ├── conftest.py         # Pytest configuration
│   └── __init__.py
├── main.py                  # Main pipeline entry point
├── run_mcp_server.py       # MCP server runner
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## 🔧 Key Components

### 1. Scrapers (`scrapers/`)

**NewsArticleScraper**
- Integrates with NewsAPI for major financial publications
- Scrapes South African financial news sites
- Respects robots.txt and rate limits

**TwitterScraper**
- Uses Twitter API v2 for advanced search
- Searches for topics: "ZAR inflation", "rand currency", etc.
- Tracks engagement metrics (likes, retweets, etc.)

### 2. Sentiment Analyzer (`sentiment/`)

**SentimentAnalyzer**
- Uses ProsusAI/FinBERT pre-trained model
- Optimized for financial text
- Returns confidence scores and fine-grained sentiment

**KeywordExtractor**
- Detects ZAR mentions
- Tracks inflation references
- Identifies SARB/monetary policy discussions

### 3. Database (`database/`)

**Models**
- `Article`: Raw scraped articles
- `SentimentAnalysis`: Analyzed sentiment results
- `SentimentAggregate`: Time-series aggregations for dashboards

**Repository Pattern**
- Clean data access layer
- Easy to switch database backends
- Transaction management

### 4. AWS Lambda (`aws_lambda/`)

**Lambda Handler**
- CloudWatch Events trigger on schedule
- Executes full pipeline in Lambda environment
- Logs to CloudWatch
- Returns execution statistics

### 5. MCP Server (`mcp_server/`)

**InflationSentimentMCPServer**
- Secure API key authentication
- Endpoints for sentiment queries
- Trend analysis and aggregations
- Article search and filtering

**API Endpoints**
- `POST /sentiment/summary` - Overall sentiment metrics
- `POST /sentiment/recent` - Recent analyses
- `POST /sentiment/trends` - Time-series trends
- `POST /articles/search` - Search with filters
- `POST /articles/{id}` - Full article details

## 🔐 Security Considerations

### Authentication
- API key authentication for MCP endpoints
- Environment-based secret management
- Never hardcode credentials

### Data Privacy
- Only store aggregated metrics in public dashboards
- Implement row-level security for sensitive analyses
- Use TLS for all communications

### AWS Security
- Use IAM roles for Lambda functions
- Encrypt RDS database
- Store secrets in AWS Secrets Manager
- VPC endpoint for RDS access from Lambda

## 📊 Usage Examples

### Get Sentiment Summary
```python
from config import get_settings
from mcp_server.sentiment_server import InflationSentimentMCPServer

server = InflationSentimentMCPServer()
summary = server.get_sentiment_summary({
    "hours": 24,
    "api_key": "your_secret_key"
})
print(summary)
```

### Search for Inflation Articles
```python
results = server.search_articles({
    "has_inflation_mention": True,
    "sentiment": "negative",
    "limit": 10,
    "api_key": "your_secret_key"
})
```

### Get Trends Over Time
```python
trends = server.get_sentiment_trends({
    "hours": 168,  # Last 7 days
    "interval": "6h",
    "api_key": "your_secret_key"
})
```

## 🚀 Deployment Guide

### Deploy to AWS Lambda

1. **Package function**
```bash
# Install dependencies in lambda package
pip install -r requirements.txt -t ./lambda_package

# Add source code
cp aws_lambda/handler.py lambda_package/
cp -r config database scrapers sentiment utils lambda_package/

# Zip for Lambda
cd lambda_package && zip -r ../lambda_deployment.zip . && cd ..
```

2. **Create Lambda function**
```bash
aws lambda create-function \
  --function-name inflation-sentiment-engine \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/lambda-execution-role \
  --handler aws_lambda/handler.lambda_handler \
  --zip-file fileb://lambda_deployment.zip \
  --timeout 300 \
  --memory-size 1024
```

3. **Create CloudWatch trigger**
```bash
# Run every 6 hours
aws events put-rule \
  --name inflation-sentiment-schedule \
  --schedule-expression "rate(6 hours)"

aws events put-targets \
  --rule inflation-sentiment-schedule \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:YOUR_ACCOUNT_ID:function:inflation-sentiment-engine"
```

4. **Setup RDS database**
```bash
aws rds create-db-instance \
  --db-instance-identifier inflation-sentiment-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 20
```

5. **Configure VPC**
- Lambda and RDS in same VPC
- Lambda needs security group allowing outbound HTTPS (for APIs)
- RDS security group allows inbound from Lambda security group

### Deploy MCP Server

**Option 1: AWS ECS/Fargate**
```bash
# Create Docker image
docker build -t inflation-sentiment-mcp .
docker tag inflation-sentiment-mcp:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/inflation-sentiment-mcp:latest
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/inflation-sentiment-mcp:latest

# Deploy to ECS
aws ecs create-service --cluster default --service-name sentiment-mcp --task-definition inflation-sentiment-mcp
```

**Option 2: EC2/Docker Compose**
```bash
docker-compose up -d
```

**Option 3: Local Development**
```bash
python run_mcp_server.py
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# With coverage
pytest tests/ --cov=sentiment --cov=database

# Run specific test
pytest tests/test_sentiment.py::TestSentimentAnalyzer::test_positive_sentiment
```

## 📈 Monitoring & Logging

### CloudWatch Metrics
- Articles scraped per run
- Sentiment distribution
- Processing latency
- API errors

### Structured Logging
- JSON format for easy parsing
- Event-based logging
- Correlation IDs for tracing

### Dashboard (Future)
- Real-time sentiment trends
- ZAR vs inflation correlation
- Top trending topics
- Confidence metrics

## 🔄 CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS Lambda

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest tests/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v2
      - run: ./deploy.sh
```

## 📚 API Reference

### MCP Endpoints

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "inflation-sentiment-server",
  "version": "1.0.0"
}
```

#### POST `/sentiment/summary`
Get sentiment summary for time period.

**Query Parameters:**
- `hours` (default: 24): Time window in hours
- `api_key` (required): API authentication key

**Response:**
```json
{
  "success": true,
  "data": {
    "total": 150,
    "positive": 65,
    "negative": 35,
    "neutral": 50,
    "positive_pct": 43.3,
    "negative_pct": 23.3,
    "neutral_pct": 33.3,
    "avg_confidence": 0.87
  }
}
```

#### POST `/sentiment/trends`
Get sentiment trends over time.

**Query Parameters:**
- `hours` (default: 168): Time window
- `interval` (default: "6h"): Bucket interval

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2026-04-17T00:00:00",
      "positive": 10,
      "negative": 5,
      "neutral": 8,
      "total": 23
    }
  ]
}
```

## 🤝 Contributing

1. Create feature branch: `git checkout -b feature/sentiment-improvement`
2. Make changes and test: `pytest tests/`
3. Submit pull request with description

## 📝 License

Designed for South African Reserve Bank (SARB) use case.

## 🆘 Troubleshooting

### Database Connection Error
```
psycopg2.OperationalError: could not connect to server
```
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

### Twitter API Errors
- Verify Bearer Token is valid
- Check API v2 access level (needs elevated access for academic research)
- Rate limits: 450 requests per 15 minutes

### Model Loading Error
- First run downloads FinBERT (~400MB)
- Requires internet connection
- Check disk space

### Memory Issues in Lambda
- Increase Lambda memory (currently 1024 MB)
- Reduce batch size in .env
- Implement pagination for large datasets

**Last Updated:** April 2026  
**Status:** Production Ready  
**Maintained By:** Data Engineering Team
