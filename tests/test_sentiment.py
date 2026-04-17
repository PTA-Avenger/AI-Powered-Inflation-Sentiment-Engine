"""
Tests for sentiment analyzer module.
"""

import pytest
from sentiment import SentimentAnalyzer, KeywordExtractor, SentimentProcessor


class TestSentimentAnalyzer:
    """Test sentiment analysis."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return SentimentAnalyzer(device="cpu")
    
    def test_positive_sentiment(self, analyzer):
        """Test positive sentiment detection."""
        text = "The South African Rand is strengthening. Inflation is under control."
        result = analyzer.analyze(text)
        
        assert "sentiment" in result
        assert "confidence" in result
        assert "scores" in result
        assert result["confidence"] > 0
    
    def test_negative_sentiment(self, analyzer):
        """Test negative sentiment detection."""
        text = "The Rand is collapsing. Inflation is spiraling out of control."
        result = analyzer.analyze(text)
        
        assert "sentiment" in result
        assert result["confidence"] > 0
    
    def test_batch_analysis(self, analyzer):
        """Test batch analysis."""
        texts = [
            "Positive news for ZAR",
            "Negative pressure on inflation",
            "Neutral market conditions",
        ]
        results = analyzer.analyze_batch(texts)
        
        assert len(results) == len(texts)
        for result in results:
            assert "sentiment" in result


class TestKeywordExtractor:
    """Test keyword extraction."""
    
    def test_zar_keyword_extraction(self):
        """Test ZAR keyword detection."""
        text = "The South African Rand weakened against the dollar today."
        result = KeywordExtractor.extract(text)
        
        assert len(result["zar_keywords"]) > 0
    
    def test_inflation_keyword_extraction(self):
        """Test inflation keyword detection."""
        text = "Consumer price index increased due to inflation pressures."
        result = KeywordExtractor.extract(text)
        
        assert len(result["inflation_keywords"]) > 0
    
    def test_has_zar_mention(self):
        """Test ZAR mention detection."""
        assert KeywordExtractor.has_zar_mention("The rand is strong")
        assert not KeywordExtractor.has_zar_mention("The dollar is strong")
    
    def test_has_inflation_mention(self):
        """Test inflation mention detection."""
        assert KeywordExtractor.has_inflation_mention("Inflation is rising")
        assert not KeywordExtractor.has_inflation_mention("Growth is rising")


class TestSentimentProcessor:
    """Test sentiment processor."""
    
    @pytest.fixture
    def processor(self):
        """Create processor instance."""
        return SentimentProcessor(device="cpu")
    
    def test_process_article(self, processor):
        """Test article processing."""
        article = {
            "title": "ZAR strengthens amid inflation control",
            "content": "The South African Rand has strengthened significantly...",
        }
        result = processor.process_article(article)
        
        assert "sentiment" in result
        assert "keywords" in result
        assert "has_zar_mention" in result
        assert "has_inflation_mention" in result
    
    def test_batch_processing(self, processor):
        """Test batch processing."""
        articles = [
            {
                "title": "ZAR news",
                "content": "Content about rand",
            },
            {
                "title": "Inflation report",
                "content": "Content about inflation",
            },
        ]
        results = processor.process_batch(articles)
        
        assert len(results) == len(articles)
