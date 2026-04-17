# 📖 Project Index - AI-Powered Inflation Sentiment Engine

Welcome! Here's your navigation guide to this comprehensive NLP project.

## 🎯 Where to Start?

### New to this project?
👉 **Start here:** [GETTING_STARTED.md](GETTING_STARTED.md) (5-minute quick start)

### Want the full story?
👉 **Read this:** [README.md](README.md) (Complete architecture & features)

### Ready to deploy?
👉 **Follow this:** [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) (Step-by-step AWS setup)

### Want to test the API?
👉 **See this:** [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) (API examples)

### What was built?
👉 **Check this:** [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md) (Implementation summary)

---

## 📁 Project Structure Guide

```
🏗️ ARCHITECTURE
├── scrapers/               → Data collection (News + Twitter)
├── sentiment/              → NLP analysis (FinBERT)
├── database/               → Data storage (PostgreSQL)
├── aws_lambda/             → Serverless processing
├── mcp_server/             → LLM access API
├── config/                 → Configuration management
└── utils/                  → Helper utilities

📚 DOCUMENTATION
├── README.md               → Full documentation
├── GETTING_STARTED.md      → Quick start (5 min)
├── AWS_DEPLOYMENT.md       → AWS deployment guide
├── API_TESTING_GUIDE.md    → API testing examples
└── PROJECT_COMPLETION.md   → What was built

🔧 CONFIGURATION
├── requirements.txt        → Python dependencies
├── .env.example           → Environment template
├── setup.py               → Package installation
├── Makefile               → Common commands
├── Dockerfile             → Container image
└── docker-compose.yml     → Full stack compose

✅ QUALITY
├── tests/                 → Test suite
└── logs/                  → Application logs (created at runtime)
```

---

## 🚀 Quick Commands

```bash
# Setup (first time)
make setup

# Run full pipeline
make run

# Run MCP server
make run-mcp

# Run with Docker
make docker

# Run tests
make test

# See all commands
make help
```

---

## 📊 What This Project Does

**Input:** 
- Financial news from NewsAPI
- Real-time tweets about ZAR and inflation
- Data automatically scraped every 6 hours

**Process:**
1. Scrape data from news and Twitter APIs
2. Analyze sentiment using FinBERT (financial language model)
3. Store results in PostgreSQL database
4. Extract keywords (ZAR mentions, inflation keywords, etc.)
5. Calculate confidence scores and aggregations

**Output:**
- REST API for querying sentiment data
- Real-time trends and summaries
- Time-series analytics
- Secure LLM access via MCP protocol

---

## 🔐 Security Notes

✅ All credentials in `.env` (never in code)
✅ API key authentication for all endpoints
✅ Database encryption-ready
✅ VPC integration for AWS
✅ No sensitive data in logs
✅ Environment-based secrets

---

## 💡 Key Features

| Feature | Location | Details |
|---------|----------|---------|
| **News Scraper** | `scrapers/news_scraper.py` | NewsAPI + custom scraping |
| **Twitter Scraper** | `scrapers/twitter_scraper.py` | Twitter API v2 integration |
| **Sentiment Analysis** | `sentiment/analyzer.py` | FinBERT model |
| **Keyword Extraction** | `sentiment/analyzer.py` | ZAR + inflation detection |
| **Database** | `database/` | PostgreSQL with 3 tables |
| **Lambda Handler** | `aws_lambda/handler.py` | Serverless processing |
| **MCP Server** | `mcp_server/sentiment_server.py` | Secure API for LLMs |
| **Web API** | `mcp_server/app.py` | FastAPI wrapper |

---

## 📈 API Quick Reference

### Authentication
All requests need: `-H "X-API-Key: your_secret_key"`

### Endpoints
```
GET  /health                    → Server status
POST /sentiment/summary         → Overall metrics
POST /sentiment/recent          → Recent analyses  
POST /sentiment/trends          → Time-series trends
POST /articles/search           → Search articles
POST /articles/{article_id}     → Article details
GET  /resources                 → List all endpoints
```

### Example
```bash
curl -X POST http://localhost:8000/sentiment/summary?hours=24 \
  -H "X-API-Key: your_secret_key"
```

---

## 🎓 Learning Path

**Beginner (30 min):**
1. Read [GETTING_STARTED.md](GETTING_STARTED.md)
2. Run setup: `make setup`
3. Start MCP server: `python run_mcp_server.py`
4. Visit http://localhost:8000/docs

**Intermediate (2 hours):**
1. Read [README.md](README.md) architecture section
2. Explore source code: start with `sentiment/analyzer.py`
3. Run tests: `make test`
4. Try [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) examples

**Advanced (4+ hours):**
1. Read [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)
2. Configure AWS credentials
3. Deploy Lambda function
4. Set up CloudWatch monitoring
5. Connect local LLM to MCP server

---

## 🔧 Troubleshooting Quick Links

| Issue | Solution |
|-------|----------|
| Import errors | Run `pip install -r requirements.txt` |
| Database won't connect | Start PostgreSQL: `make docker` |
| Port 8000 in use | Change in `.env`: `MCP_PORT=8001` |
| Model not downloading | Check disk space (~400MB) |
| API key rejected | Verify `MCP_SECRET_KEY` in `.env` |
| Twitter errors | Check bearer token validity |

---

## 🎯 Next Actions

### For Developers
```bash
make setup              # Setup environment
python main.py         # Run pipeline
make run-mcp          # Start MCP server
pytest tests/         # Run tests
```

### For DevOps/Cloud Team
1. Review [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md)
2. Set up AWS credentials
3. Run deployment commands
4. Configure monitoring

### For Data Scientists
1. Check `sentiment/analyzer.py` for FinBERT usage
2. Review keyword extraction logic
3. Explore database schema in `database/models.py`
4. Analyze aggregations in `database/repository.py`

---

## 📞 Documentation Map

**Quick Start**
- [GETTING_STARTED.md](GETTING_STARTED.md) - 5 min setup

**Comprehensive**
- [README.md](README.md) - Full documentation
- [PROJECT_COMPLETION.md](PROJECT_COMPLETION.md) - What was built

**Technical**
- [AWS_DEPLOYMENT.md](AWS_DEPLOYMENT.md) - AWS deployment
- [API_TESTING_GUIDE.md](API_TESTING_GUIDE.md) - API usage

**Code**
- `config/settings.py` - Configuration
- `scrapers/` - Data collection
- `sentiment/` - NLP analysis
- `database/` - Data models
- `mcp_server/` - API server

---

## ✨ Key Highlights

✅ **Production-Ready** - Error handling, logging, security
✅ **Fully Documented** - 5 guides, code comments, type hints
✅ **Cloud-Native** - AWS Lambda, RDS, CloudWatch ready
✅ **Modular Design** - Easy to extend and maintain
✅ **Test Coverage** - Tests included for core components
✅ **Secure by Default** - API keys, environment secrets, no hardcoding

---

## 🚀 Ready to Go!

Everything is ready for immediate use:
- ✅ Scrapers implemented and tested
- ✅ Sentiment analysis with FinBERT
- ✅ Database schema designed
- ✅ API server ready
- ✅ Lambda handler prepared
- ✅ Documentation complete

**Start with [GETTING_STARTED.md](GETTING_STARTED.md) 👈**

---

**Last Updated:** April 17, 2026
**Status:** ✅ Production Ready
**For:** SARB Monetary Policy Support

Need help? Check the relevant documentation above or explore the well-commented source code.

Happy analyzing! 🎉
