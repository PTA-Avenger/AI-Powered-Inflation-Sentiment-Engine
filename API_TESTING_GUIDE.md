# MCP Server API Testing Guide

Complete guide for testing the Model Context Protocol server endpoints.

## 🚀 Getting Started

### Prerequisites

- MCP Server running: `python run_mcp_server.py`
- Test API key in `.env`: `MCP_SECRET_KEY=your-test-key`
- Optional: Postman or other REST client

### Authentication

All requests require API key authentication:

```bash
# Header format
X-API-Key: your_secret_key

# Or query parameter
?api_key=your_secret_key
```

## 📋 API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Description:** Verify server is running

**cURL:**
```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "inflation-sentiment-server",
  "version": "1.0.0"
}
```

---

### 2. List Resources

**Endpoint:** `GET /resources`

**Description:** List all available MCP resources and endpoints

**cURL:**
```bash
curl http://localhost:8000/resources
```

**Response:**
```json
{
  "resources": [
    {
      "name": "get_sentiment_summary",
      "description": "Get sentiment summary for a time period",
      "params": ["hours", "api_key"]
    },
    ...
  ]
}
```

---

### 3. Get Sentiment Summary

**Endpoint:** `POST /sentiment/summary`

**Description:** Get overall sentiment metrics for a time period

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hours` | integer | 24 | Time window in hours (1-720) |
| `api_key` | string | required | Authentication key |

**cURL:**
```bash
curl -X POST http://localhost:8000/sentiment/summary?hours=24 \
  -H "X-API-Key: your_secret_key"
```

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
  },
  "period_hours": 24,
  "timestamp": "2026-04-17T10:30:00.123456"
}
```

**Python:**
```python
import requests

url = "http://localhost:8000/sentiment/summary"
params = {"hours": 24}
headers = {"X-API-Key": "your_secret_key"}

response = requests.post(url, params=params, headers=headers)
print(response.json())
```

---

### 4. Get Recent Sentiment

**Endpoint:** `POST /sentiment/recent`

**Description:** Get individual sentiment analyses from recent period

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hours` | integer | 24 | Time window in hours |
| `limit` | integer | 100 | Max results to return (1-500) |
| `api_key` | string | required | Authentication key |

**cURL:**
```bash
curl -X POST "http://localhost:8000/sentiment/recent?hours=24&limit=50" \
  -H "X-API-Key: your_secret_key"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "article_id": "article-123",
      "sentiment": "positive",
      "confidence": 0.92,
      "has_zar_mention": true,
      "has_inflation_mention": false,
      "analyzed_at": "2026-04-17T09:00:00"
    },
    {
      "article_id": "article-124",
      "sentiment": "negative",
      "confidence": 0.87,
      "has_zar_mention": true,
      "has_inflation_mention": true,
      "analyzed_at": "2026-04-17T08:30:00"
    }
  ],
  "count": 2,
  "period_hours": 24,
  "timestamp": "2026-04-17T10:30:00"
}
```

---

### 5. Get Sentiment Trends

**Endpoint:** `POST /sentiment/trends`

**Description:** Get sentiment trends over time in buckets

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `hours` | integer | 168 | Time window (1-720) |
| `interval` | string | "6h" | Bucket size: 1h, 6h, 12h, 24h |
| `api_key` | string | required | Authentication key |

**cURL:**
```bash
curl -X POST "http://localhost:8000/sentiment/trends?hours=168&interval=6h" \
  -H "X-API-Key: your_secret_key"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2026-04-17T00:00:00",
      "positive": 15,
      "negative": 8,
      "neutral": 12,
      "total": 35
    },
    {
      "timestamp": "2026-04-17T06:00:00",
      "positive": 18,
      "negative": 5,
      "neutral": 14,
      "total": 37
    }
  ],
  "period_hours": 168,
  "interval": "6h",
  "timestamp": "2026-04-17T10:30:00"
}
```

---

### 6. Search Articles

**Endpoint:** `POST /articles/search`

**Description:** Search articles with filters

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `sentiment` | string | Filter: positive, negative, neutral |
| `has_zar_mention` | boolean | Filter by ZAR mention |
| `has_inflation_mention` | boolean | Filter by inflation mention |
| `hours` | integer | Time window (default: 24) |
| `limit` | integer | Max results (default: 50) |
| `api_key` | string | required |

**Examples:**

All positive articles about ZAR:
```bash
curl -X POST "http://localhost:8000/articles/search?sentiment=positive&has_zar_mention=true&limit=20" \
  -H "X-API-Key: your_secret_key"
```

Negative inflation articles:
```bash
curl -X POST "http://localhost:8000/articles/search?sentiment=negative&has_inflation_mention=true" \
  -H "X-API-Key: your_secret_key"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "article_id": "article-456",
      "sentiment": "positive",
      "confidence": 0.89,
      "zar_mention": true,
      "inflation_mention": false,
      "positive_score": 0.92,
      "negative_score": 0.02,
      "analyzed_at": "2026-04-17T09:15:00"
    }
  ],
  "count": 1,
  "filters": {
    "sentiment": "positive",
    "has_zar_mention": true,
    "has_inflation_mention": null
  },
  "timestamp": "2026-04-17T10:30:00"
}
```

---

### 7. Get Article Details

**Endpoint:** `POST /articles/{article_id}`

**Description:** Get full details of a specific article

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `article_id` | string | Article ID |

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `api_key` | string | required |

**cURL:**
```bash
curl -X POST "http://localhost:8000/articles/article-123" \
  -H "X-API-Key: your_secret_key"
```

**Response:**
```json
{
  "success": true,
  "article": {
    "id": "article-123",
    "source": "news",
    "title": "South African Rand Strengthens",
    "content": "The rand has strengthened 2% today...",
    "author": "Finance24",
    "url": "https://fin24.com/article-123",
    "published_at": "2026-04-17T08:00:00"
  },
  "sentiment_analysis": {
    "sentiment": "positive",
    "confidence": 0.92,
    "positive_score": 0.92,
    "negative_score": 0.02,
    "neutral_score": 0.06,
    "zar_mention": true,
    "inflation_mention": false,
    "keywords": {
      "zar_keywords": ["rand", "strengthens"],
      "inflation_keywords": [],
      "policy_keywords": []
    },
    "analyzed_at": "2026-04-17T09:00:00"
  }
}
```

---

## 🧪 Testing Workflow

### Complete Workflow Example

```bash
#!/bin/bash

API_KEY="your_secret_key"
BASE_URL="http://localhost:8000"
HEADERS="X-API-Key: $API_KEY"

echo "1. Check health..."
curl $BASE_URL/health

echo -e "\n2. Get summary..."
curl -X POST "$BASE_URL/sentiment/summary?hours=24" -H "$HEADERS"

echo -e "\n3. Get trends..."
curl -X POST "$BASE_URL/sentiment/trends?hours=168&interval=6h" -H "$HEADERS"

echo -e "\n4. Search negative articles..."
curl -X POST "$BASE_URL/articles/search?sentiment=negative&limit=5" -H "$HEADERS"
```

### Postman Collection

```json
{
  "info": {
    "name": "Inflation Sentiment MCP API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/health"
      }
    },
    {
      "name": "Sentiment Summary",
      "request": {
        "method": "POST",
        "header": [{"key": "X-API-Key", "value": "{{api_key}}"}],
        "url": "http://localhost:8000/sentiment/summary?hours=24"
      }
    }
  ]
}
```

## 🔍 Common Test Scenarios

### Scenario 1: Monitor ZAR Sentiment

```bash
# Get positive ZAR articles
curl -X POST "http://localhost:8000/articles/search?sentiment=positive&has_zar_mention=true&limit=10" \
  -H "X-API-Key: your_secret_key" | jq '.data[] | {id: .article_id, confidence: .confidence}'
```

### Scenario 2: Track Inflation Expectations

```bash
# Get recent inflation mentions with trends
curl -X POST "http://localhost:8000/sentiment/trends?hours=168&interval=6h" \
  -H "X-API-Key: your_secret_key" | jq '.data[] | {time: .timestamp, total: .total, positive_pct: (.positive/.total*100)}'
```

### Scenario 3: Sentiment Shift Detection

```python
import requests
import json
from datetime import datetime

API_KEY = "your_secret_key"
BASE_URL = "http://localhost:8000"
HEADERS = {"X-API-Key": API_KEY}

# Get summary for last 24 hours
current = requests.post(
    f"{BASE_URL}/sentiment/summary?hours=24",
    headers=HEADERS
).json()["data"]

# Get summary for 24-48 hours ago
previous = requests.post(
    f"{BASE_URL}/sentiment/summary?hours=48",
    headers=HEADERS
).json()["data"]

print(f"Current sentiment: {current['positive']} positive, {current['negative']} negative")
print(f"Sentiment shift: {current['positive'] - previous['positive']:+d} positive")
```

## ⚠️ Error Handling

### 401 Unauthorized
```json
{
  "error": "Unauthorized",
  "code": 401
}
```
**Solution:** Check API key header

### 404 Not Found
```json
{
  "error": "Article not found",
  "code": 404
}
```
**Solution:** Verify article ID exists

### 500 Server Error
```json
{
  "error": "Database connection failed",
  "code": 500
}
```
**Solution:** Check server logs, verify database is running

## 📊 Performance Testing

```bash
# Test with load (using Apache Bench)
ab -n 1000 -c 10 -H "X-API-Key: your_secret_key" \
  -p '{}' -T 'application/json' \
  http://localhost:8000/sentiment/summary?hours=24
```

---

Ready to test! Start the server and begin querying. 🚀
