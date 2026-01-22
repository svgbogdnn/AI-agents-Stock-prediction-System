"""
News fetcher for sentiment analysis.
Fetches news from multiple sources including News API, Polygon, and web scraping.
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

# Import Polygon news as fallback
from tools.polygon_fetcher import get_stock_news as polygon_get_news

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_BASE = "https://newsapi.org/v2"


def get_recent_news(
    ticker: str,
    days: int = 7,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Get recent news articles for a stock from multiple sources.
    
    Args:
        ticker: Stock symbol
        days: Number of days to look back
        limit: Maximum number of articles
    
    Returns:
        List of dicts with article information:
        - title: Article headline
        - description: Article summary
        - source: Publisher name
        - published_date: Publication timestamp
        - url: Link to full article
        - sentiment: (optional) Detected sentiment
    """
    articles = []
    
    # Try News API first (if available)
    if NEWS_API_KEY:
        news_api_articles = _fetch_from_news_api(ticker, days, limit)
        articles.extend(news_api_articles)
    
    # Fallback to Polygon news
    if len(articles) < limit:
        polygon_articles = _fetch_from_polygon(ticker, limit - len(articles))
        articles.extend(polygon_articles)
    
    # If still no articles, try web scraping (Google News)
    if not articles:
        scraped_articles = _fetch_from_google_news(ticker, limit)
        articles.extend(scraped_articles)
    
    # Sort by date (most recent first)
    articles.sort(key=lambda x: x.get("published_date", ""), reverse=True)
    
    return articles[:limit]


def _fetch_from_news_api(ticker: str, days: int, limit: int) -> List[Dict[str, Any]]:
    """Fetch news from News API."""
    try:
        # Calculate date range
        from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        # Search query (ticker + company name variations)
        query = f"{ticker} OR stock OR shares"
        
        url = f"{NEWS_API_BASE}/everything"
        params = {
            "q": query,
            "from": from_date,
            "sortBy": "publishedAt",
            "language": "en",
            "pageSize": limit,
            "apiKey": NEWS_API_KEY
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data.get("status") != "ok":
            return []
        
        articles = []
        for item in data.get("articles", []):
            # Filter out removed articles
            if item.get("title") == "[Removed]":
                continue
            
            articles.append({
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "source": item.get("source", {}).get("name", "Unknown"),
                "published_date": item.get("publishedAt", ""),
                "url": item.get("url", ""),
                "author": item.get("author", ""),
                "content": item.get("content", ""),
                "data_source": "news_api"
            })
        
        return articles
        
    except Exception as e:
        print(f"Error fetching from News API: {e}")
        return []


def _fetch_from_polygon(ticker: str, limit: int) -> List[Dict[str, Any]]:
    """Fetch news from Polygon.io as fallback."""
    try:
        polygon_news = polygon_get_news(ticker, limit=limit)
        
        # Standardize format
        articles = []
        for item in polygon_news:
            if "error" in item:
                continue
            
            articles.append({
                "title": item.get("title", ""),
                "description": item.get("description", ""),
                "source": item.get("source", "Polygon"),
                "published_date": item.get("published_date", ""),
                "url": item.get("article_url", ""),
                "author": item.get("author", ""),
                "keywords": item.get("keywords", []),
                "data_source": "polygon"
            })
        
        return articles
        
    except Exception as e:
        print(f"Error fetching from Polygon: {e}")
        return []


def _fetch_from_google_news(ticker: str, limit: int) -> List[Dict[str, Any]]:
    """
    Scrape Google News as last resort fallback.
    Note: This is a simplified version and may need adjustments.
    """
    try:
        # Google News RSS feed
        url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse RSS (simplified)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, "xml")
        
        items = soup.find_all("item")[:limit]
        
        articles = []
        for item in items:
            title = item.find("title")
            link = item.find("link")
            pub_date = item.find("pubDate")
            source = item.find("source")
            
            articles.append({
                "title": title.text if title else "",
                "description": "",  # RSS doesn't include full description
                "source": source.text if source else "Google News",
                "published_date": pub_date.text if pub_date else "",
                "url": link.text if link else "",
                "data_source": "google_news_rss"
            })
        
        return articles
        
    except Exception as e:
        print(f"Error scraping Google News: {e}")
        return []


def analyze_sentiment(articles: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze overall sentiment from a list of articles.
    
    This is a simplified keyword-based approach.
    In production, would use a model like FinBERT.
    
    Args:
        articles: List of article dicts
    
    Returns:
        Dict with sentiment analysis:
        - overall_sentiment: 'positive', 'negative', or 'neutral'
        - positive_count: Number of positive articles
        - negative_count: Number of negative articles
        - neutral_count: Number of neutral articles
        - sentiment_score: Aggregated score (-1 to 1)
    """
    if not articles:
        return {
            "overall_sentiment": "neutral",
            "sentiment_score": 0.0,
            "article_count": 0
        }
    
    positive_words = [
        "surge", "gain", "rise", "jump", "rally", "outperform", "beat",
        "strong", "growth", "profit", "record", "high", "upgrade", "positive"
    ]
    
    negative_words = [
        "plunge", "drop", "fall", "decline", "loss", "miss", "weak",
        "downgrade", "concern", "risk", "crash", "negative", "lawsuit", "investigation"
    ]
    
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    for article in articles:
        title = article.get("title", "").lower()
        description = article.get("description", "").lower()
        combined_text = title + " " + description
        
        # Count sentiment words
        pos_score = sum(1 for word in positive_words if word in combined_text)
        neg_score = sum(1 for word in negative_words if word in combined_text)
        
        if pos_score > neg_score:
            positive_count += 1
        elif neg_score > pos_score:
            negative_count += 1
        else:
            neutral_count += 1
    
    # Calculate overall sentiment
    total = len(articles)
    sentiment_score = (positive_count - negative_count) / total if total > 0 else 0.0
    
    if sentiment_score > 0.2:
        overall_sentiment = "positive"
    elif sentiment_score < -0.2:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"
    
    return {
        "overall_sentiment": overall_sentiment,
        "sentiment_score": round(sentiment_score, 2),
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "article_count": total,
        "positive_ratio": round(positive_count / total, 2) if total > 0 else 0,
        "timestamp": datetime.now().isoformat()
    }


def detect_key_events(articles: List[Dict[str, Any]]) -> List[str]:
    """
    Detect significant events from news articles.
    
    Args:
        articles: List of article dicts
    
    Returns:
        List of detected event types
    """
    events = set()
    
    event_keywords = {
        "Earnings Report": ["earnings", "quarterly results", "q1", "q2", "q3", "q4", "eps"],
        "M&A Activity": ["merger", "acquisition", "acquires", "m&a", "deal", "takeover"],
        "Product Launch": ["launch", "unveil", "announce", "new product", "release"],
        "Legal Issues": ["lawsuit", "investigation", "sec", "regulatory", "probe"],
        "Executive Change": ["ceo", "cfo", "appoints", "resigns", "executive"],
        "Dividend/Buyback": ["dividend", "buyback", "repurchase", "shareholder return"],
        "Guidance Change": ["guidance", "outlook", "forecast", "projects"],
        "Partnership": ["partnership", "collaboration", "strategic alliance"]
    }
    
    for article in articles:
        text = (article.get("title", "") + " " + article.get("description", "")).lower()
        
        for event_type, keywords in event_keywords.items():
            if any(keyword in text for keyword in keywords):
                events.add(event_type)
    
    return sorted(list(events))


def get_news_with_sentiment(ticker: str, days: int = 7) -> Dict[str, Any]:
    """
    Get news articles with sentiment analysis.
    
    Args:
        ticker: Stock symbol
        days: Days to look back
    
    Returns:
        Dict with articles and sentiment analysis
    """
    articles = get_recent_news(ticker, days=days, limit=20)
    sentiment = analyze_sentiment(articles)
    key_events = detect_key_events(articles)
    
    return {
        "ticker": ticker,
        "articles": articles,
        "sentiment_analysis": sentiment,
        "key_events": key_events,
        "article_count": len(articles),
        "days_analyzed": days,
        "timestamp": datetime.now().isoformat()
    }


# Test function
if __name__ == "__main__":
    ticker = "NVDA"
    
    print(f"Testing news fetcher for {ticker}...\n")
    
    print("1. Fetching recent news:")
    news_data = get_news_with_sentiment(ticker, days=7)
    
    print(f"   Found {news_data['article_count']} articles")
    
    print("\n2. Top 3 headlines:")
    for i, article in enumerate(news_data["articles"][:3], 1):
        print(f"   {i}. {article['title']}")
        print(f"      Source: {article['source']} | {article['published_date'][:10]}")
    
    print("\n3. Sentiment Analysis:")
    sentiment = news_data["sentiment_analysis"]
    print(f"   Overall: {sentiment['overall_sentiment'].upper()}")
    print(f"   Score: {sentiment['sentiment_score']}")
    print(f"   Positive: {sentiment['positive_count']} | Negative: {sentiment['negative_count']} | Neutral: {sentiment['neutral_count']}")
    
    print("\n4. Key Events Detected:")
    if news_data["key_events"]:
        for event in news_data["key_events"]:
            print(f"   - {event}")
    else:
        print("   No major events detected")

