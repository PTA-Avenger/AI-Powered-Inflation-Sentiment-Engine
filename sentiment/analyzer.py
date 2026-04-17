"""
Sentiment analysis module using FinBERT for financial text analysis.
"""

from typing import Dict, List, Tuple
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Financial sentiment analyzer using FinBERT."""
    
    def __init__(self, model_name: str = "ProsusAI/finbert", device: str = "cpu"):
        """Initialize sentiment analyzer with FinBERT model."""
        self.device = device
        self.model_name = model_name
        
        logger.info(f"Loading FinBERT model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(device)
        self.model.eval()
        
        # FinBERT labels
        self.label_map = {0: "positive", 1: "negative", 2: "neutral"}
        logger.info("FinBERT model loaded successfully")
    
    def analyze(self, text: str, max_length: int = 512) -> Dict:
        """
        Analyze sentiment of financial text.
        
        Args:
            text: Input text to analyze
            max_length: Maximum token length
            
        Returns:
            Dictionary with sentiment scores and classification
        """
        # Truncate text if necessary
        text = text[:2000]  # FinBERT expects shorter texts
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=max_length,
            padding=True
        ).to(self.device)
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=1)[0].cpu().numpy()
            predicted_class = torch.argmax(logits, dim=1)[0].item()
        
        sentiment = self.label_map[predicted_class]
        
        return {
            "sentiment": sentiment,
            "confidence": float(probs[predicted_class]),
            "scores": {
                "positive": float(probs[0]),
                "negative": float(probs[1]),
                "neutral": float(probs[2]),
            },
            "model_version": self.model_name,
        }
    
    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """Analyze sentiment for multiple texts efficiently."""
        results = []
        for text in texts:
            results.append(self.analyze(text))
        return results


class KeywordExtractor:
    """Extract relevant keywords related to ZAR, inflation, and monetary policy."""
    
    # Keywords related to ZAR and currency
    ZAR_KEYWORDS = {
        "zar", "rand", "south african rand", "currency",
        "exchange rate", "forex", "fx", "currency depreciation",
        "zar weakening", "zar strengthening", "rand weakness"
    }
    
    # Keywords related to inflation
    INFLATION_KEYWORDS = {
        "inflation", "inflation rate", "cpi", "consumer price index",
        "price increase", "inflation target", "inflation expectations",
        "deflation", "price pressure", "cost of living"
    }
    
    # Keywords related to SARB and monetary policy
    MONETARY_POLICY_KEYWORDS = {
        "sarb", "reserve bank", "central bank", "monetary policy",
        "interest rate", "repo rate", "prime rate", "rate hike",
        "rate cut", "mpc", "monetary policy committee", "forward guidance"
    }
    
    @classmethod
    def extract(cls, text: str) -> Dict[str, List[str]]:
        """
        Extract keywords from text.
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with keyword categories and found keywords
        """
        text_lower = text.lower()
        
        return {
            "zar_keywords": [kw for kw in cls.ZAR_KEYWORDS if kw in text_lower],
            "inflation_keywords": [kw for kw in cls.INFLATION_KEYWORDS if kw in text_lower],
            "policy_keywords": [kw for kw in cls.MONETARY_POLICY_KEYWORDS if kw in text_lower],
        }
    
    @classmethod
    def has_zar_mention(cls, text: str) -> bool:
        """Check if text mentions ZAR or currency."""
        return any(kw in text.lower() for kw in cls.ZAR_KEYWORDS)
    
    @classmethod
    def has_inflation_mention(cls, text: str) -> bool:
        """Check if text mentions inflation."""
        return any(kw in text.lower() for kw in cls.INFLATION_KEYWORDS)


class SentimentProcessor:
    """Process articles through sentiment analysis pipeline."""
    
    def __init__(self, model_name: str = "ProsusAI/finbert", device: str = "cpu"):
        """Initialize sentiment processor."""
        self.analyzer = SentimentAnalyzer(model_name, device)
        self.keyword_extractor = KeywordExtractor()
    
    def process_article(self, article: Dict) -> Dict:
        """
        Process article: analyze sentiment and extract keywords.
        
        Args:
            article: Article data with 'title' and 'content'
            
        Returns:
            Enriched article data with sentiment analysis
        """
        # Combine title and content for analysis
        text = f"{article.get('title', '')}. {article.get('content', '')}"
        
        # Analyze sentiment
        sentiment_result = self.analyzer.analyze(text)
        
        # Extract keywords
        keywords = self.keyword_extractor.extract(text)
        
        return {
            **sentiment_result,
            "keywords": keywords,
            "has_zar_mention": self.keyword_extractor.has_zar_mention(text),
            "has_inflation_mention": self.keyword_extractor.has_inflation_mention(text),
        }
    
    def process_batch(self, articles: List[Dict]) -> List[Dict]:
        """Process multiple articles."""
        results = []
        for article in articles:
            try:
                result = self.process_article(article)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing article: {e}")
                results.append({"error": str(e)})
        return results
