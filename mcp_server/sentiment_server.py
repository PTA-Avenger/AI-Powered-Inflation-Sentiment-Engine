"""
Model Context Protocol (MCP) Server for secure LLM access to sentiment database.
This allows local LLMs to query sentiment data securely.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from functools import wraps

from config import get_settings
from database import get_session_factory, SentimentRepository, ArticleRepository

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize database
SessionLocal = get_session_factory(settings.database_url)


def require_auth(secret_key: str):
    """Decorator for MCP endpoint authentication."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, params: Dict[str, Any], **kwargs):
            # Extract API key from params
            api_key = params.pop("api_key", None)
            if api_key != settings.mcp_secret_key:
                return {
                    "error": "Unauthorized",
                    "code": 401,
                }
            return func(self, params, **kwargs)
        return wrapper
    return decorator


class InflationSentimentMCPServer:
    """
    MCP Server for querying inflation sentiment data.
    Provides secure interfaces for LLMs to access sentiment database.
    """
    
    def __init__(self):
        """Initialize MCP server."""
        self.name = "inflation-sentiment-server"
        self.version = "1.0.0"
        logger.info(f"Initialized {self.name} v{self.version}")
    
    @require_auth(settings.mcp_secret_key)
    def get_sentiment_summary(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get sentiment summary for a time period.
        
        Args:
            params: {
                "hours": int (default: 24),
                "api_key": str (required for auth)
            }
            
        Returns:
            Sentiment summary statistics
        """
        hours = params.get("hours", 24)
        
        try:
            session = SessionLocal()
            repo = SentimentRepository(session)
            summary = repo.get_sentiment_summary(hours=hours)
            session.close()
            
            return {
                "success": True,
                "data": summary,
                "period_hours": hours,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting sentiment summary: {e}")
            return {
                "error": str(e),
                "code": 500,
            }
    
    @require_auth(settings.mcp_secret_key)
    def get_recent_sentiment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get recent sentiment analyses.
        
        Args:
            params: {
                "hours": int (default: 24),
                "limit": int (default: 100),
                "api_key": str (required for auth)
            }
            
        Returns:
            List of recent sentiment analyses
        """
        hours = params.get("hours", 24)
        limit = params.get("limit", 100)
        
        try:
            session = SessionLocal()
            repo = SentimentRepository(session)
            results = repo.get_recent_sentiment(hours=hours)
            session.close()
            
            # Format for LLM consumption
            formatted = []
            for result in results[:limit]:
                formatted.append({
                    "article_id": result.article_id,
                    "sentiment": result.sentiment,
                    "confidence": result.confidence_score,
                    "has_zar_mention": result.zar_mention,
                    "has_inflation_mention": result.inflation_mention,
                    "analyzed_at": result.analyzed_at.isoformat(),
                })
            
            return {
                "success": True,
                "data": formatted,
                "count": len(formatted),
                "period_hours": hours,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting recent sentiment: {e}")
            return {
                "error": str(e),
                "code": 500,
            }
    
    @require_auth(settings.mcp_secret_key)
    def get_sentiment_trends(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get sentiment trends over time.
        
        Args:
            params: {
                "hours": int (default: 168 for 1 week),
                "interval": str (default: "6h" for 6-hour buckets),
                "api_key": str (required for auth)
            }
            
        Returns:
            Sentiment trends data
        """
        hours = params.get("hours", 168)
        interval = params.get("interval", "6h")
        
        try:
            session = SessionLocal()
            repo = SentimentRepository(session)
            recent = repo.get_recent_sentiment(hours=hours)
            session.close()
            
            # Bucket by time interval
            trends = self._bucket_by_interval(recent, interval)
            
            return {
                "success": True,
                "data": trends,
                "period_hours": hours,
                "interval": interval,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting sentiment trends: {e}")
            return {
                "error": str(e),
                "code": 500,
            }
    
    @require_auth(settings.mcp_secret_key)
    def search_articles(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search articles by sentiment and keywords.
        
        Args:
            params: {
                "sentiment": str (optional: positive, negative, neutral),
                "has_zar_mention": bool (optional),
                "has_inflation_mention": bool (optional),
                "hours": int (default: 24),
                "limit": int (default: 50),
                "api_key": str (required for auth)
            }
            
        Returns:
            List of matching articles
        """
        sentiment_filter = params.get("sentiment")
        zar_filter = params.get("has_zar_mention")
        inflation_filter = params.get("has_inflation_mention")
        hours = params.get("hours", 24)
        limit = params.get("limit", 50)
        
        try:
            session = SessionLocal()
            sentiment_repo = SentimentRepository(session)
            recent = sentiment_repo.get_recent_sentiment(hours=hours)
            
            # Apply filters
            results = recent
            if sentiment_filter:
                results = [r for r in results if r.sentiment == sentiment_filter]
            if zar_filter is not None:
                results = [r for r in results if r.zar_mention == zar_filter]
            if inflation_filter is not None:
                results = [r for r in results if r.inflation_mention == inflation_filter]
            
            session.close()
            
            formatted = []
            for result in results[:limit]:
                formatted.append({
                    "article_id": result.article_id,
                    "sentiment": result.sentiment,
                    "confidence": result.confidence_score,
                    "zar_mention": result.zar_mention,
                    "inflation_mention": result.inflation_mention,
                    "positive_score": result.positive_score,
                    "negative_score": result.negative_score,
                    "analyzed_at": result.analyzed_at.isoformat(),
                })
            
            return {
                "success": True,
                "data": formatted,
                "count": len(formatted),
                "filters": {
                    "sentiment": sentiment_filter,
                    "has_zar_mention": zar_filter,
                    "has_inflation_mention": inflation_filter,
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error searching articles: {e}")
            return {
                "error": str(e),
                "code": 500,
            }
    
    @require_auth(settings.mcp_secret_key)
    def get_article_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get full details of a specific article.
        
        Args:
            params: {
                "article_id": str,
                "api_key": str (required for auth)
            }
            
        Returns:
            Full article details with sentiment analysis
        """
        article_id = params.get("article_id")
        if not article_id:
            return {"error": "article_id is required", "code": 400}
        
        try:
            session = SessionLocal()
            article_repo = ArticleRepository(session)
            sentiment_repo = SentimentRepository(session)
            
            article = article_repo.get_by_id(article_id)
            sentiment = sentiment_repo.get_by_article_id(article_id)
            session.close()
            
            if not article:
                return {"error": "Article not found", "code": 404}
            
            result = {
                "success": True,
                "article": {
                    "id": article.id,
                    "source": article.source,
                    "title": article.title,
                    "content": article.content,
                    "author": article.author,
                    "url": article.url,
                    "published_at": article.published_at.isoformat(),
                },
            }
            
            if sentiment:
                result["sentiment_analysis"] = {
                    "sentiment": sentiment.sentiment,
                    "confidence": sentiment.confidence_score,
                    "positive_score": sentiment.positive_score,
                    "negative_score": sentiment.negative_score,
                    "neutral_score": sentiment.neutral_score,
                    "zar_mention": sentiment.zar_mention,
                    "inflation_mention": sentiment.inflation_mention,
                    "keywords": json.loads(sentiment.keywords) if sentiment.keywords else {},
                    "analyzed_at": sentiment.analyzed_at.isoformat(),
                }
            
            return result
        except Exception as e:
            logger.error(f"Error getting article details: {e}")
            return {
                "error": str(e),
                "code": 500,
            }
    
    def _bucket_by_interval(self, results: list, interval: str) -> List[Dict]:
        """
        Bucket results by time interval.
        
        Args:
            results: List of sentiment results
            interval: Time interval (e.g., "1h", "6h", "24h")
            
        Returns:
            Bucketed results
        """
        # Parse interval
        hours_map = {"1h": 1, "6h": 6, "12h": 12, "24h": 24}
        bucket_hours = hours_map.get(interval, 6)
        
        buckets = {}
        for result in results:
            # Round time to nearest bucket
            bucket_time = result.analyzed_at.replace(
                hour=(result.analyzed_at.hour // bucket_hours) * bucket_hours,
                minute=0,
                second=0,
                microsecond=0
            )
            
            key = bucket_time.isoformat()
            if key not in buckets:
                buckets[key] = {
                    "timestamp": key,
                    "positive": 0,
                    "negative": 0,
                    "neutral": 0,
                    "total": 0,
                }
            
            if result.sentiment == "positive":
                buckets[key]["positive"] += 1
            elif result.sentiment == "negative":
                buckets[key]["negative"] += 1
            else:
                buckets[key]["neutral"] += 1
            
            buckets[key]["total"] += 1
        
        return sorted(buckets.values(), key=lambda x: x["timestamp"])
    
    def list_resources(self) -> Dict[str, Any]:
        """List available MCP resources/endpoints."""
        return {
            "resources": [
                {
                    "name": "get_sentiment_summary",
                    "description": "Get sentiment summary for a time period",
                    "params": ["hours", "api_key"],
                },
                {
                    "name": "get_recent_sentiment",
                    "description": "Get recent sentiment analyses",
                    "params": ["hours", "limit", "api_key"],
                },
                {
                    "name": "get_sentiment_trends",
                    "description": "Get sentiment trends over time",
                    "params": ["hours", "interval", "api_key"],
                },
                {
                    "name": "search_articles",
                    "description": "Search articles by sentiment and keywords",
                    "params": ["sentiment", "has_zar_mention", "has_inflation_mention", "hours", "limit", "api_key"],
                },
                {
                    "name": "get_article_details",
                    "description": "Get full details of a specific article",
                    "params": ["article_id", "api_key"],
                },
            ]
        }
