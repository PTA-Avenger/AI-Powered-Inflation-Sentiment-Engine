"""
News scraper for financial news from South African and international sources.
"""

import requests
import logging
from typing import List, Optional, Dict
from datetime import datetime
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)


class NewsArticleScraper:
    """Scrapes financial news articles."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize news scraper.
        
        Args:
            api_key: NewsAPI API key (optional, for NewsAPI source)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    def scrape_newsapi(self, query: str = "ZAR inflation", hours: int = 24) -> List[Dict]:
        """
        Scrape from NewsAPI (requires API key).
        
        Args:
            query: Search query
            hours: Look back hours
            
        Returns:
            List of articles
        """
        if not self.api_key:
            logger.warning("NewsAPI key not provided, skipping NewsAPI scraping")
            return []
        
        url = "https://newsapi.org/v2/everything"
        
        # South African financial news sources
        sources = "news24,businesstech,fin24,moneyweb,iol-business"
        
        params = {
            "q": query,
            "sources": sources,
            "sortBy": "publishedAt",
            "language": "en",
            "apiKey": self.api_key,
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                articles.append({
                    "id": article.get("url"),  # Use URL as ID
                    "title": article.get("title", ""),
                    "content": article.get("content", ""),
                    "author": article.get("author", ""),
                    "url": article.get("url", ""),
                    "published_at": datetime.fromisoformat(
                        article.get("publishedAt", "").replace("Z", "+00:00")
                    ),
                    "source": "news",
                })
            
            logger.info(f"Scraped {len(articles)} articles from NewsAPI")
            return articles
        
        except Exception as e:
            logger.error(f"Error scraping NewsAPI: {e}")
            return []
    
    def scrape_financial_websites(self) -> List[Dict]:
        """
        Scrape from major South African financial news sites.
        
        Returns:
            List of articles
        """
        articles = []
        
        # List of South African financial news sites
        sites = [
            {
                "url": "https://www.news24.com/fin24",
                "name": "Fin24",
                "article_selector": "article",
                "title_selector": "h2",
                "content_selector": "p",
            },
            {
                "url": "https://businesstech.co.za",
                "name": "BusinessTech",
                "article_selector": "article",
                "title_selector": "h2",
                "content_selector": "p",
            },
        ]
        
        for site in sites:
            try:
                response = self.session.get(site["url"], timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Extract articles (basic implementation)
                site_articles = soup.find_all(site["article_selector"])[:10]
                
                for article_elem in site_articles:
                    try:
                        title_elem = article_elem.find(site["title_selector"])
                        content_elem = article_elem.find(site["content_selector"])
                        
                        if title_elem and content_elem:
                            articles.append({
                                "id": f"{site['name']}-{len(articles)}",
                                "title": title_elem.get_text(strip=True),
                                "content": content_elem.get_text(strip=True),
                                "author": site["name"],
                                "url": site["url"],
                                "published_at": datetime.utcnow(),
                                "source": "news",
                            })
                    except Exception as e:
                        logger.debug(f"Error parsing article from {site['name']}: {e}")
                
                logger.info(f"Scraped {len(site_articles)} articles from {site['name']}")
                time.sleep(2)  # Be respectful to servers
            
            except Exception as e:
                logger.error(f"Error scraping {site['name']}: {e}")
        
        return articles


class NewsScraperFactory:
    """Factory for creating news scrapers."""
    
    @staticmethod
    def create(api_key: Optional[str] = None) -> NewsArticleScraper:
        """Create news scraper instance."""
        return NewsArticleScraper(api_key)
