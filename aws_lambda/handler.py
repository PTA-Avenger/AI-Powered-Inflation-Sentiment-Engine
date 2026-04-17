"""
AWS Lambda handler for processing sentiment analysis pipeline.
This function is triggered by CloudWatch Events on a schedule.
"""

import json
import logging
import os
from typing import Dict, Any
from datetime import datetime

from config import get_settings
from database import init_db, get_session_factory, ArticleRepository, SentimentRepository
from scrapers import NewsScraperFactory, TwitterScraperFactory
from sentiment import SentimentProcessor

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize settings
settings = get_settings()

# Initialize database
init_db(settings.database_url)
SessionLocal = get_session_factory(settings.database_url)

# Initialize processors
sentiment_processor = SentimentProcessor(
    model_name=settings.sentiment_model,
    device=settings.device,
)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for sentiment analysis pipeline.
    
    Args:
        event: CloudWatch Events event
        context: Lambda context
        
    Returns:
        Response with processing statistics
    """
    logger.info("Starting sentiment analysis pipeline")
    
    try:
        session = SessionLocal()
        article_repo = ArticleRepository(session)
        sentiment_repo = SentimentRepository(session)
        
        # Step 1: Scrape data from news and Twitter
        logger.info("Step 1: Scraping data sources")
        articles = scrape_data()
        logger.info(f"Scraped {len(articles)} articles")
        
        # Step 2: Store raw articles in database
        logger.info("Step 2: Storing raw articles")
        stored_count = 0
        for article in articles:
            try:
                article_repo.add_article({
                    "id": article["id"],
                    "source": article["source"],
                    "title": article.get("title", ""),
                    "content": article.get("content", ""),
                    "author": article.get("author"),
                    "url": article.get("url"),
                    "published_at": article.get("published_at", datetime.utcnow()),
                })
                stored_count += 1
            except Exception as e:
                logger.warning(f"Could not store article {article.get('id')}: {e}")
        
        logger.info(f"Stored {stored_count} articles")
        
        # Step 3: Get unanalyzed articles
        logger.info("Step 3: Processing sentiment analysis")
        unanalyzed = article_repo.get_unanalyzed(limit=settings.batch_size)
        logger.info(f"Found {len(unanalyzed)} unanalyzed articles")
        
        # Step 4: Analyze sentiment
        analyzed_count = 0
        for article in unanalyzed:
            try:
                result = sentiment_processor.process_article({
                    "title": article.title,
                    "content": article.content,
                })
                
                sentiment_repo.add_analysis({
                    "article_id": article.id,
                    "source": article.source,
                    "sentiment": result["sentiment"],
                    "confidence_score": result["confidence"],
                    "positive_score": result["scores"]["positive"],
                    "negative_score": result["scores"]["negative"],
                    "neutral_score": result["scores"]["neutral"],
                    "keywords": json.dumps(result.get("keywords", {})),
                    "zar_mention": result.get("has_zar_mention", False),
                    "inflation_mention": result.get("has_inflation_mention", False),
                    "model_version": result["model_version"],
                })
                analyzed_count += 1
            except Exception as e:
                logger.error(f"Error analyzing article {article.id}: {e}")
        
        logger.info(f"Analyzed {analyzed_count} articles")
        
        # Step 5: Generate summary statistics
        logger.info("Step 5: Generating summary statistics")
        summary = sentiment_repo.get_sentiment_summary(hours=24)
        
        session.close()
        
        response = {
            "statusCode": 200,
            "body": {
                "message": "Sentiment analysis pipeline completed successfully",
                "scraped": len(articles),
                "stored": stored_count,
                "analyzed": analyzed_count,
                "summary": summary,
                "timestamp": datetime.utcnow().isoformat(),
            }
        }
        
        logger.info(f"Pipeline completed: {json.dumps(response)}")
        return response
    
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        return {
            "statusCode": 500,
            "body": {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
        }


def scrape_data() -> list:
    """Scrape data from all sources."""
    all_articles = []
    
    # Scrape news
    try:
        news_scraper = NewsScraperFactory.create(api_key=settings.news_api_key)
        news_articles = news_scraper.scrape_newsapi()
        all_articles.extend(news_articles)
        logger.info(f"Scraped {len(news_articles)} news articles")
    except Exception as e:
        logger.error(f"Error scraping news: {e}")
    
    # Scrape Twitter
    try:
        twitter_scraper = TwitterScraperFactory.create(
            bearer_token=settings.twitter_bearer_token,
            api_key=settings.twitter_api_key,
            api_secret=settings.twitter_api_secret,
            access_token=settings.twitter_access_token,
            access_token_secret=settings.twitter_access_token_secret,
        )
        twitter_tweets = twitter_scraper.search_topics()
        all_articles.extend(twitter_tweets)
        logger.info(f"Scraped {len(twitter_tweets)} tweets")
    except Exception as e:
        logger.error(f"Error scraping Twitter: {e}")
    
    return all_articles
