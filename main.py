"""
Main entry point for running the sentiment analysis pipeline locally.
"""

import asyncio
import logging
from datetime import datetime

from config import get_settings
from database import init_db, get_session_factory, ArticleRepository, SentimentRepository
from scrapers import NewsScraperFactory, TwitterScraperFactory
from sentiment import SentimentProcessor
from utils import setup_logging

logger = logging.getLogger(__name__)


async def main():
    """Run sentiment analysis pipeline."""
    setup_logging()
    logger.info("Starting Inflation Sentiment Engine Pipeline")
    
    settings = get_settings()
    
    # Initialize database
    logger.info("Initializing database...")
    init_db(settings.database_url)
    SessionLocal = get_session_factory(settings.database_url)
    
    try:
        # Create session
        session = SessionLocal()
        article_repo = ArticleRepository(session)
        sentiment_repo = SentimentRepository(session)
        
        # Initialize processors
        logger.info("Loading sentiment analyzer...")
        processor = SentimentProcessor(
            model_name=settings.sentiment_model,
            device=settings.device,
        )
        
        # Scrape data
        logger.info("Scraping data sources...")
        all_articles = []
        
        # News scraper
        try:
            news_scraper = NewsScraperFactory.create(api_key=settings.news_api_key)
            news_articles = news_scraper.scrape_newsapi()
            all_articles.extend(news_articles)
            logger.info(f"Scraped {len(news_articles)} news articles")
        except Exception as e:
            logger.error(f"Error scraping news: {e}")
        
        # Twitter scraper
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
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        
        # Store articles
        logger.info("Storing articles in database...")
        for article in all_articles:
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
            except Exception as e:
                logger.debug(f"Could not store article: {e}")
        
        # Analyze sentiment
        logger.info("Analyzing sentiment...")
        unanalyzed = article_repo.get_unanalyzed(limit=settings.batch_size)
        logger.info(f"Analyzing {len(unanalyzed)} unanalyzed articles")
        
        for i, article in enumerate(unanalyzed):
            try:
                result = processor.process_article({
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
                    "keywords": str(result.get("keywords", {})),
                    "zar_mention": result.get("has_zar_mention", False),
                    "inflation_mention": result.get("has_inflation_mention", False),
                    "model_version": result["model_version"],
                })
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Analyzed {i + 1}/{len(unanalyzed)} articles")
            except Exception as e:
                logger.error(f"Error analyzing article {article.id}: {e}")
        
        # Generate summary
        logger.info("Generating summary...")
        summary = sentiment_repo.get_sentiment_summary(hours=24)
        
        logger.info(f"Summary for last 24 hours:")
        logger.info(f"  Total articles: {summary['total']}")
        logger.info(f"  Positive: {summary['positive']} ({summary['positive_pct']:.1f}%)")
        logger.info(f"  Negative: {summary['negative']} ({summary['negative_pct']:.1f}%)")
        logger.info(f"  Neutral: {summary['neutral']} ({summary['neutral_pct']:.1f}%)")
        logger.info(f"  Avg confidence: {summary['avg_confidence']:.2f}")
        
        session.close()
        logger.info("Pipeline completed successfully")
    
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
