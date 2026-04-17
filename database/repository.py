"""Database repository layer for data access."""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from .models import Article, SentimentAnalysis, SentimentAggregate, SourceEnum


class ArticleRepository:
    """Repository for article management."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def add_article(self, article_data: dict) -> Article:
        """Add a new article."""
        article = Article(**article_data)
        self.session.add(article)
        self.session.commit()
        return article
    
    def get_by_id(self, article_id: str) -> Optional[Article]:
        """Get article by ID."""
        return self.session.query(Article).filter(Article.id == article_id).first()
    
    def get_recent(self, hours: int = 24, source: Optional[SourceEnum] = None) -> List[Article]:
        """Get recent articles."""
        query = self.session.query(Article)
        if source:
            query = query.filter(Article.source == source)
        
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return query.filter(Article.published_at >= cutoff).order_by(desc(Article.published_at)).all()
    
    def get_unanalyzed(self, limit: int = 100) -> List[Article]:
        """Get articles that haven't been analyzed yet."""
        analyzed_ids = self.session.query(SentimentAnalysis.article_id).all()
        analyzed_ids = {id[0] for id in analyzed_ids}
        
        articles = self.session.query(Article).all()
        return [a for a in articles if a.id not in analyzed_ids][:limit]


class SentimentRepository:
    """Repository for sentiment analysis results."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def add_analysis(self, analysis_data: dict) -> SentimentAnalysis:
        """Add sentiment analysis result."""
        analysis = SentimentAnalysis(**analysis_data)
        self.session.add(analysis)
        self.session.commit()
        return analysis
    
    def get_by_article_id(self, article_id: str) -> Optional[SentimentAnalysis]:
        """Get sentiment analysis by article ID."""
        return self.session.query(SentimentAnalysis).filter(
            SentimentAnalysis.article_id == article_id
        ).first()
    
    def get_recent_sentiment(self, hours: int = 24) -> List[SentimentAnalysis]:
        """Get recent sentiment analyses."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return self.session.query(SentimentAnalysis).filter(
            SentimentAnalysis.analyzed_at >= cutoff
        ).order_by(desc(SentimentAnalysis.analyzed_at)).all()
    
    def get_sentiment_summary(self, hours: int = 24) -> dict:
        """Get sentiment summary statistics."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = self.session.query(SentimentAnalysis).filter(
            SentimentAnalysis.analyzed_at >= cutoff
        )
        
        results = query.all()
        if not results:
            return {"total": 0, "positive": 0, "negative": 0, "neutral": 0}
        
        total = len(results)
        positive = sum(1 for r in results if r.sentiment == "positive")
        negative = sum(1 for r in results if r.sentiment == "negative")
        neutral = sum(1 for r in results if r.sentiment == "neutral")
        
        return {
            "total": total,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "positive_pct": (positive / total * 100) if total > 0 else 0,
            "negative_pct": (negative / total * 100) if total > 0 else 0,
            "neutral_pct": (neutral / total * 100) if total > 0 else 0,
            "avg_confidence": sum(r.confidence_score for r in results) / total if total > 0 else 0,
        }


class AggregateRepository:
    """Repository for aggregated sentiment metrics."""
    
    def __init__(self, session: Session):
        self.session = session
    
    def add_aggregate(self, aggregate_data: dict) -> SentimentAggregate:
        """Add aggregated sentiment metrics."""
        aggregate = SentimentAggregate(**aggregate_data)
        self.session.add(aggregate)
        self.session.commit()
        return aggregate
    
    def get_by_date(self, period_date: datetime) -> Optional[SentimentAggregate]:
        """Get aggregate for specific date."""
        return self.session.query(SentimentAggregate).filter(
            func.date(SentimentAggregate.period_date) == period_date.date()
        ).first()
    
    def get_recent_aggregates(self, days: int = 30) -> List[SentimentAggregate]:
        """Get aggregates for recent period."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        return self.session.query(SentimentAggregate).filter(
            SentimentAggregate.period_date >= cutoff
        ).order_by(desc(SentimentAggregate.period_date)).all()
