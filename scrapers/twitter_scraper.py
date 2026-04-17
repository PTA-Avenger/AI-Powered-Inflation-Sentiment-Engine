"""
Twitter (X) API scraper for sentiment data collection.
Requires Twitter API v2 credentials.
"""

import tweepy
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TwitterScraper:
    """Scrapes tweets from Twitter API v2."""
    
    def __init__(
        self,
        bearer_token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
    ):
        """
        Initialize Twitter scraper.
        
        Args:
            bearer_token: Twitter API v2 Bearer Token
            api_key: Twitter API v1.1 API Key
            api_secret: Twitter API v1.1 API Secret
            access_token: Twitter API v1.1 Access Token
            access_token_secret: Twitter API v1.1 Access Token Secret
        """
        self.bearer_token = bearer_token
        
        # Initialize v2 client for advanced search
        if bearer_token:
            self.client_v2 = tweepy.Client(bearer_token=bearer_token)
            logger.info("Twitter API v2 client initialized")
        else:
            self.client_v2 = None
            logger.warning("Twitter API v2 Bearer Token not provided")
        
        # Initialize v1.1 client for additional features
        if api_key and api_secret and access_token and access_token_secret:
            auth = tweepy.OAuthHandler(api_key, api_secret)
            auth.set_access_token(access_token, access_token_secret)
            self.api_v1 = tweepy.API(auth)
            logger.info("Twitter API v1.1 client initialized")
        else:
            self.api_v1 = None
            logger.warning("Twitter API v1.1 credentials incomplete")
    
    def search_tweets(
        self,
        query: str = "ZAR OR rand OR inflation -is:retweet",
        max_results: int = 100,
        hours_back: int = 24,
    ) -> List[Dict]:
        """
        Search tweets using Twitter API v2.
        
        Args:
            query: Search query
            max_results: Maximum tweets to return (up to 100 per request)
            hours_back: Search tweets from last N hours
            
        Returns:
            List of tweet data
        """
        if not self.client_v2:
            logger.error("Twitter API v2 client not initialized")
            return []
        
        tweets = []
        start_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        try:
            # Search tweets with advanced query
            response = self.client_v2.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),
                start_time=start_time,
                tweet_fields=["created_at", "author_id", "public_metrics"],
                user_fields=["username", "verified"],
                expansions=["author_id"],
            )
            
            if not response.data:
                logger.info("No tweets found for query")
                return []
            
            # Build user map
            user_map = {user.id: user for user in response.includes["users"]}
            
            # Process tweets
            for tweet in response.data:
                user = user_map.get(tweet.author_id)
                tweets.append({
                    "id": str(tweet.id),
                    "content": tweet.text,
                    "author": user.username if user else "unknown",
                    "created_at": tweet.created_at,
                    "likes": tweet.public_metrics.get("like_count", 0),
                    "retweets": tweet.public_metrics.get("retweet_count", 0),
                    "replies": tweet.public_metrics.get("reply_count", 0),
                    "quotes": tweet.public_metrics.get("quote_count", 0),
                    "url": f"https://twitter.com/{user.username if user else 'unknown'}/status/{tweet.id}",
                    "source": "twitter",
                })
            
            logger.info(f"Scraped {len(tweets)} tweets")
            return tweets
        
        except Exception as e:
            logger.error(f"Error searching tweets: {e}")
            return []
    
    def search_topics(
        self,
        topics: Optional[List[str]] = None,
        max_results: int = 50,
        hours_back: int = 24,
    ) -> List[Dict]:
        """
        Search tweets for specific topics related to ZAR and inflation.
        
        Args:
            topics: List of topics to search
            max_results: Max tweets per topic
            hours_back: Hours to look back
            
        Returns:
            Combined list of tweets
        """
        if topics is None:
            topics = [
                "ZAR inflation",
                "South African rand",
                "SARB monetary policy",
                "inflation expectations",
                "rand currency",
            ]
        
        all_tweets = []
        for topic in topics:
            logger.info(f"Searching for tweets about: {topic}")
            tweets = self.search_tweets(topic, max_results, hours_back)
            all_tweets.extend(tweets)
        
        return all_tweets
    
    def get_trending_topics(self) -> List[Dict]:
        """
        Get trending topics in South Africa.
        Note: Requires elevated access level in Twitter API.
        
        Returns:
            List of trending topics
        """
        if not self.api_v1:
            logger.error("Twitter API v1.1 not initialized")
            return []
        
        try:
            trends = self.api_v1.get_place_trends(id=1)  # 1 = Worldwide
            return trends
        except Exception as e:
            logger.error(f"Error fetching trends: {e}")
            return []


class TwitterScraperFactory:
    """Factory for creating Twitter scrapers."""
    
    @staticmethod
    def create(
        bearer_token: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
    ) -> TwitterScraper:
        """Create Twitter scraper instance."""
        return TwitterScraper(
            bearer_token=bearer_token,
            api_key=api_key,
            api_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )
