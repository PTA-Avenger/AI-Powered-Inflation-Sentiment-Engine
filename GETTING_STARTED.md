# Getting Started Guide

Quick guide to get the Inflation Sentiment Engine running in 5 minutes.

## 🚀 Prerequisites

- Python 3.11+
- PostgreSQL 12+ (or Docker for PostgreSQL)
- Git

## 📦 Installation

### 1. Clone & Setup

```bash
cd "AI-Powered Inflation Sentiment Engine"

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Or (macOS/Linux)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Minimum required: DATABASE_URL
```

### 3. Setup Database (Option A: Docker)

```bash
# Start PostgreSQL in Docker
docker run --name sentiment-db \
  -e POSTGRES_PASSWORD=changeme \
  -e POSTGRES_DB=inflation_sentiment \
  -p 5432:5432 \
  -d postgres:15

# Update .env with database connection
# DATABASE_URL=postgresql://postgres:changeme@localhost:5432/inflation_sentiment
```

### 3. Setup Database (Option B: Local PostgreSQL)

```bash
# Create database
createdb inflation_sentiment

# Set connection string in .env
# DATABASE_URL=postgresql://user:password@localhost:5432/inflation_sentiment
```

### 4. Initialize Database

```bash
python -c "from database import init_db; from config import get_settings; init_db(get_settings().database_url)"
```

## 🎯 Quick Test

### Test 1: Sentiment Analysis

```bash
python -c "
from sentiment import SentimentAnalyzer

analyzer = SentimentAnalyzer(device='cpu')
result = analyzer.analyze('The South African Rand is strengthening significantly.')
print('Sentiment:', result['sentiment'])
print('Confidence:', result['confidence'])
print('Scores:', result['scores'])
"
```

### Test 2: Full Pipeline (Demo)

```python
# demo.py
from config import get_settings
from database import init_db, get_session_factory, ArticleRepository, SentimentRepository
from sentiment import SentimentProcessor

# Initialize
settings = get_settings()
init_db(settings.database_url)
SessionLocal = get_session_factory(settings.database_url)

# Create session
session = SessionLocal()
article_repo = ArticleRepository(session)
sentiment_repo = SentimentRepository(session)

# Initialize processor
processor = SentimentProcessor(device=settings.device)

# Process sample articles
sample_articles = [
    {
        "id": "article1",
        "source": "news",
        "title": "ZAR Strengthens Against Dollar",
        "content": "The South African Rand has strengthened 2% against the US Dollar today..."
    },
    {
        "id": "article2",
        "source": "twitter",
        "title": "Inflation Concerns Rising",
        "content": "Market participants express concerns about rising inflation expectations..."
    }
]

# Store articles
for article in sample_articles:
    try:
        article_repo.add_article(article)
    except:
        pass  # Skip if already exists

# Analyze
for article in article_repo.get_unanalyzed(limit=10):
    result = processor.process_article({
        "title": article.title,
        "content": article.content
    })
    
    sentiment_repo.add_analysis({
        "article_id": article.id,
        "source": article.source,
        "sentiment": result["sentiment"],
        "confidence_score": result["confidence"],
        "positive_score": result["scores"]["positive"],
        "negative_score": result["scores"]["negative"],
        "neutral_score": result["scores"]["neutral"],
        "keywords": str(result.get("keywords", {})),
        "zar_mention": result.get("has_zar_mention", False),
        "inflation_mention": result.get("has_inflation_mention", False),
        "model_version": result["model_version"],
    })

# Get summary
summary = sentiment_repo.get_sentiment_summary()
print("Summary:", summary)

session.close()
```

Run it:
```bash
python demo.py
```

### Test 3: MCP Server

```bash
# Start MCP server
python run_mcp_server.py

# In another terminal, test API
curl -X POST http://localhost:8000/sentiment/summary \
  -H "api-key: your_secret_key"
```

## 🔧 Configuration Options

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/inflation_sentiment

# Model
SENTIMENT_MODEL=ProsusAI/finbert
DEVICE=cpu  # or cuda for GPU

# MCP Server
MCP_PORT=8000
MCP_SECRET_KEY=your-secret-key

# Scraping
SCRAPE_INTERVAL_HOURS=6
BATCH_SIZE=50
```

## 📊 API Usage Examples

### Python

```python
from mcp_server.sentiment_server import InflationSentimentMCPServer

server = InflationSentimentMCPServer()

# Get summary
summary = server.get_sentiment_summary({
    "hours": 24,
    "api_key": "your_secret_key"
})
print(summary)
```

### cURL

```bash
# Get sentiment summary
curl -X POST http://localhost:8000/sentiment/summary?hours=24 \
  -H "api-key: your_secret_key"

# Search articles
curl -X POST "http://localhost:8000/articles/search?sentiment=positive&has_zar_mention=true" \
  -H "api-key: your_secret_key"

# Get trends
curl -X POST "http://localhost:8000/sentiment/trends?hours=168&interval=6h" \
  -H "api-key: your_secret_key"
```

### Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"
API_KEY = "your_secret_key"
HEADERS = {"api-key": API_KEY}

# Get summary
response = requests.post(
    f"{BASE_URL}/sentiment/summary",
    params={"hours": 24},
    headers=HEADERS
)
print(response.json())
```

## 🔐 Security Setup

### 1. Change Default Credentials

```env
# In .env, change these:
MCP_SECRET_KEY=your-new-secure-random-key-here
```

### 2. Production Setup

For production deployment:

```bash
# Generate strong secret
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Store in .env
MCP_SECRET_KEY=<generated_key>
```

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov

# Run specific test
pytest tests/test_sentiment.py::TestSentimentAnalyzer::test_positive_sentiment -v
```

## 📈 Next Steps

1. **Add API Credentials**
   - Get Twitter API v2 Bearer Token: https://developer.twitter.com
   - Get NewsAPI Key: https://newsapi.org

2. **Configure Scrapers** (in `.env`)
   ```env
   TWITTER_BEARER_TOKEN=your_bearer_token
   NEWS_API_KEY=your_news_api_key
   ```

3. **Run Full Pipeline**
   ```bash
   python main.py
   ```

4. **Deploy to AWS**
   - See [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)

5. **Connect Local LLM**
   - Use MCP Server URLs to provide sentiment data to Claude or other LLMs
   - Example: "What is the sentiment toward the Rand?" → LLM queries MCP Server

## 🆘 Troubleshooting

### Model Download Issues

FinBERT downloads on first use (~400MB):
```bash
# Pre-download model
python -c "from transformers import AutoModel; AutoModel.from_pretrained('ProsusAI/finbert')"
```

### Database Errors

```bash
# Check database connection
psql -h localhost -U postgres -d inflation_sentiment

# Reset database
dropdb inflation_sentiment
createdb inflation_sentiment
python -c "from database import init_db; from config import get_settings; init_db(get_settings().database_url)"
```

### Port Already in Use

```bash
# Change MCP port in .env
MCP_PORT=8001

# Or kill process on port 8000
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :8000
kill -9 <PID>
```

## 📚 Additional Resources

- [Full README](README.md) - Complete documentation
- [AWS Deployment](AWS_DEPLOYMENT.md) - Cloud deployment guide
- [MCP Server Docs](mcp_server/sentiment_server.py) - API documentation
- [Database Models](database/models.py) - Data schema

## 💬 Quick Questions

**Q: Can I use GPU?**
A: Yes, set `DEVICE=cuda` in .env (requires GPU and PyTorch CUDA support)

**Q: How much data do I need?**
A: System works with any amount. Start with hundreds of articles for meaningful trends.

**Q: Can I use different sentiment model?**
A: Yes, change `SENTIMENT_MODEL` in .env to any HuggingFace model

**Q: How often does pipeline run?**
A: By default every 6 hours (configurable via `SCRAPE_INTERVAL_HOURS`)

---

Ready to go! Start with `python demo.py` or `python run_mcp_server.py` 🚀
