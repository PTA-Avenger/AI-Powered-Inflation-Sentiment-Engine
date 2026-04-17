"""
Database models for sentiment data storage.
Uses SQLAlchemy ORM for PostgreSQL.
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from sqlalchemy import (
    Column, String, Float, DateTime, Integer, Text, 
    Boolean, Index, create_engine, Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class SentimentScoreEnum(str, Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class SourceEnum(str, Enum):
    """Data source type."""
    TWITTER = "twitter"
    NEWS = "news"
    COMBINED = "combined"


class Article(Base):
    """Article/tweet model for raw collected data."""
    __tablename__ = "articles"
    
    id = Column(String(255), primary_key=True)  # Unique ID from source
    source = Column(SQLEnum(SourceEnum), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(255), nullable=True)
    url = Column(String(2048), unique=True, nullable=True)
    published_at = Column(DateTime, nullable=False, index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)
    language = Column(String(10), default="en")
    
    __table_args__ = (
        Index("idx_source_published", "source", "published_at"),
        Index("idx_source_scraped", "source", "scraped_at"),
    )


class SentimentAnalysis(Base):
    """Sentiment analysis results."""
    __tablename__ = "sentiment_analysis"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    article_id = Column(String(255), nullable=False, unique=True, index=True)
    source = Column(SQLEnum(SourceEnum), nullable=False, index=True)
    
    # Sentiment scores
    sentiment = Column(SQLEnum(SentimentScoreEnum), nullable=False, index=True)
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    
    # Fine-grained scores
    positive_score = Column(Float, nullable=False)
    negative_score = Column(Float, nullable=False)
    neutral_score = Column(Float, nullable=False)
    
    # Keywords and entities
    keywords = Column(Text, nullable=True)  # JSON array as string
    zar_mention = Column(Boolean, default=False, index=True)
    inflation_mention = Column(Boolean, default=False, index=True)
    
    # Metadata
    model_version = Column(String(50), nullable=False)
    analyzed_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index("idx_sentiment_analyzed", "sentiment", "analyzed_at"),
        Index("idx_inflation_zar", "inflation_mention", "zar_mention"),
    )


class SentimentAggregate(Base):
    """Aggregated sentiment metrics (for performance)."""
    __tablename__ = "sentiment_aggregate"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Time period
    period_date = Column(DateTime, nullable=False, unique=True, index=True)
    period_type = Column(String(20), default="daily")  # daily, hourly, weekly
    
    # Aggregates
    total_articles = Column(Integer, default=0)
    positive_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    
    # Averages
    avg_confidence = Column(Float, nullable=True)
    avg_positive_score = Column(Float, nullable=True)
    avg_negative_score = Column(Float, nullable=True)
    
    # Sentiment indicators
    sentiment_index = Column(Float, nullable=True)  # -1.0 to 1.0
    zar_mentions = Column(Integer, default=0)
    inflation_mentions = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db(database_url: str) -> None:
    """Initialize database and create tables."""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)


def get_session_factory(database_url: str):
    """Create SQLAlchemy session factory."""
    engine = create_engine(
        database_url,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True
    )
    return sessionmaker(bind=engine)
