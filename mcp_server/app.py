"""
FastAPI server for local development and testing of MCP sentiment database.
In production, this would integrate with the official MCP server.
"""

from fastapi import FastAPI, HTTPException, Header, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging

from config import get_settings
from .sentiment_server import InflationSentimentMCPServer

logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize FastAPI app
app = FastAPI(
    title="Inflation Sentiment Engine - MCP Server",
    description="Secure LLM access to sentiment database",
    version="1.0.0",
)

# Initialize MCP server
mcp_server = InflationSentimentMCPServer()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": mcp_server.name,
        "version": mcp_server.version,
    }


@app.get("/resources")
async def list_resources():
    """List available MCP resources."""
    return mcp_server.list_resources()


@app.post("/sentiment/summary")
async def get_sentiment_summary(
    hours: int = Query(24, ge=1, le=720),
    api_key: str = Header(...),
):
    """Get sentiment summary for a time period."""
    result = mcp_server.get_sentiment_summary({"hours": hours, "api_key": api_key})
    if "error" in result:
        raise HTTPException(status_code=result.get("code", 500), detail=result["error"])
    return result


@app.post("/sentiment/recent")
async def get_recent_sentiment(
    hours: int = Query(24, ge=1, le=720),
    limit: int = Query(100, ge=1, le=500),
    api_key: str = Header(...),
):
    """Get recent sentiment analyses."""
    result = mcp_server.get_recent_sentiment({
        "hours": hours,
        "limit": limit,
        "api_key": api_key,
    })
    if "error" in result:
        raise HTTPException(status_code=result.get("code", 500), detail=result["error"])
    return result


@app.post("/sentiment/trends")
async def get_sentiment_trends(
    hours: int = Query(168, ge=1, le=720),
    interval: str = Query("6h"),
    api_key: str = Header(...),
):
    """Get sentiment trends over time."""
    result = mcp_server.get_sentiment_trends({
        "hours": hours,
        "interval": interval,
        "api_key": api_key,
    })
    if "error" in result:
        raise HTTPException(status_code=result.get("code", 500), detail=result["error"])
    return result


@app.post("/articles/search")
async def search_articles(
    sentiment: Optional[str] = Query(None),
    has_zar_mention: Optional[bool] = Query(None),
    has_inflation_mention: Optional[bool] = Query(None),
    hours: int = Query(24, ge=1, le=720),
    limit: int = Query(50, ge=1, le=500),
    api_key: str = Header(...),
):
    """Search articles by sentiment and keywords."""
    params = {
        "sentiment": sentiment,
        "has_zar_mention": has_zar_mention,
        "has_inflation_mention": has_inflation_mention,
        "hours": hours,
        "limit": limit,
        "api_key": api_key,
    }
    result = mcp_server.search_articles(params)
    if "error" in result:
        raise HTTPException(status_code=result.get("code", 500), detail=result["error"])
    return result


@app.post("/articles/{article_id}")
async def get_article_details(
    article_id: str,
    api_key: str = Header(...),
):
    """Get full details of a specific article."""
    result = mcp_server.get_article_details({"article_id": article_id, "api_key": api_key})
    if "error" in result:
        raise HTTPException(status_code=result.get("code", 500), detail=result["error"])
    return result


@app.get("/docs-mcp")
async def mcp_documentation():
    """MCP server documentation."""
    return {
        "name": mcp_server.name,
        "version": mcp_server.version,
        "description": "Model Context Protocol server for inflation sentiment database",
        "authentication": "Bearer token in X-API-Key header",
        "endpoints": mcp_server.list_resources(),
        "base_url": f"http://{settings.mcp_host}:{settings.mcp_port}",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.mcp_host,
        port=settings.mcp_port,
        log_level=settings.log_level.lower(),
    )
