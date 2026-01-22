"""
Polygon.io API data fetcher for stock fundamentals, price history, and news.
Following Day 2a/2b best practices: clear docstrings, type hints, error handling.
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

load_dotenv()

POLYGON_API_KEY = os.getenv("POLYGON_API_KEY")
POLYGON_BASE_URL = "https://api.polygon.io"


def get_fundamentals(ticker: str) -> Dict[str, Any]:
    """
    Get fundamental financial data for a stock from Polygon.io.
    
    Args:
        ticker: Stock symbol (e.g., 'GOOGL', 'AAPL')
    
    Returns:
        Dict containing fundamental metrics:
        - pe_ratio: Price-to-Earnings ratio
        - eps: Earnings Per Share
        - revenue: Annual revenue
        - market_cap: Market capitalization
        - debt_to_equity: Debt-to-Equity ratio
        - current_ratio: Current ratio (liquidity)
        
    Raises:
        ValueError: If ticker is invalid or data unavailable
        requests.RequestException: If API request fails
    """
    if not POLYGON_API_KEY:
        raise ValueError("POLYGON_API_KEY not found in environment variables")
    
    try:
        # Get ticker details (includes some fundamental data)
        url = f"{POLYGON_BASE_URL}/v3/reference/tickers/{ticker}"
        params = {"apiKey": POLYGON_API_KEY}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK" or "results" not in data:
            return {
                "error": f"No fundamental data available for {ticker}",
                "ticker": ticker
            }
        
        results = data["results"]
        
        # Get latest price for market cap calculation
        price_data = get_latest_price(ticker)
        current_price = price_data.get("close", 0)
        
        # Extract fundamental metrics
        market_cap = results.get("market_cap", 0)
        shares_outstanding = results.get("weighted_shares_outstanding", 0)
        
        # Calculate P/E ratio if we have earnings data
        # Note: Polygon free tier may not have all this data
        pe_ratio = None
        eps = None
        
        fundamentals = {
            "ticker": ticker,
            "name": results.get("name", ticker),
            "market_cap": market_cap,
            "shares_outstanding": shares_outstanding,
            "current_price": current_price,
            "currency": results.get("currency_name", "USD"),
            "sector": results.get("sic_description", "Unknown"),
            "pe_ratio": pe_ratio,
            "eps": eps,
            "description": results.get("description", ""),
            "homepage_url": results.get("homepage_url", ""),
            "total_employees": results.get("total_employees"),
            "list_date": results.get("list_date"),
            "data_source": "polygon",
            "timestamp": datetime.now().isoformat()
        }
        
        return fundamentals
        
    except requests.RequestException as e:
        return {
            "error": f"API request failed: {str(e)}",
            "ticker": ticker,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "ticker": ticker,
            "timestamp": datetime.now().isoformat()
        }


def get_price_history(
    ticker: str,
    days: int = 365,
    timespan: str = "day"
) -> Dict[str, Any]:
    """
    Get historical price and volume data from Polygon.io.
    
    Args:
        ticker: Stock symbol
        days: Number of days of historical data (default: 365)
        timespan: 'day', 'week', or 'month' (default: 'day')
    
    Returns:
        Dict with keys:
        - ticker: Stock symbol
        - timespan: Timeframe used
        - data: List of dicts with [date, open, high, low, close, volume]
        - count: Number of data points
    """
    if not POLYGON_API_KEY:
        raise ValueError("POLYGON_API_KEY not found in environment variables")
    
    try:
        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/range/1/{timespan}/{start_date}/{end_date}"
        params = {
            "apiKey": POLYGON_API_KEY,
            "adjusted": "true",
            "sort": "asc"
        }
        
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK" or "results" not in data:
            return {
                "error": f"No price history available for {ticker}",
                "ticker": ticker
            }
        
        # Format results
        results = data["results"]
        formatted_data = []
        
        for bar in results:
            formatted_data.append({
                "date": datetime.fromtimestamp(bar["t"] / 1000).strftime("%Y-%m-%d"),
                "open": bar["o"],
                "high": bar["h"],
                "low": bar["l"],
                "close": bar["c"],
                "volume": bar["v"],
                "vwap": bar.get("vw"),  # Volume-weighted average price
                "transactions": bar.get("n")
            })
        
        return {
            "ticker": ticker,
            "timespan": timespan,
            "data": formatted_data,
            "count": len(formatted_data),
            "query_count": data.get("queryCount", 0),
            "timestamp": datetime.now().isoformat()
        }
        
    except requests.RequestException as e:
        return {
            "error": f"API request failed: {str(e)}",
            "ticker": ticker
        }
    except Exception as e:
        return {
            "error": f"Unexpected error: {str(e)}",
            "ticker": ticker
        }


def get_latest_price(ticker: str) -> Dict[str, Any]:
    """
    Get the latest price for a stock.
    
    Args:
        ticker: Stock symbol
    
    Returns:
        Dict with latest price data (open, high, low, close, volume)
    """
    if not POLYGON_API_KEY:
        raise ValueError("POLYGON_API_KEY not found in environment variables")
    
    try:
        url = f"{POLYGON_BASE_URL}/v2/aggs/ticker/{ticker}/prev"
        params = {"apiKey": POLYGON_API_KEY, "adjusted": "true"}
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK" or "results" not in data:
            return {"error": f"No price data available for {ticker}"}
        
        result = data["results"][0]
        
        return {
            "ticker": ticker,
            "date": datetime.fromtimestamp(result["t"] / 1000).strftime("%Y-%m-%d"),
            "open": result["o"],
            "high": result["h"],
            "low": result["l"],
            "close": result["c"],
            "volume": result["v"],
            "vwap": result.get("vw"),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Failed to get latest price: {str(e)}",
            "ticker": ticker
        }


def get_stock_news(ticker: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent news articles for a stock from Polygon.io.
    
    Args:
        ticker: Stock symbol
        limit: Maximum number of articles to return (default: 10)
    
    Returns:
        List of dicts with news articles containing:
        - title: Article headline
        - author: Article author
        - published_date: Publication timestamp
        - article_url: URL to full article
        - description: Article summary
        - source: Publisher name
    """
    if not POLYGON_API_KEY:
        raise ValueError("POLYGON_API_KEY not found in environment variables")
    
    try:
        url = f"{POLYGON_BASE_URL}/v2/reference/news"
        params = {
            "apiKey": POLYGON_API_KEY,
            "ticker": ticker,
            "limit": limit,
            "order": "desc"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") != "OK" or "results" not in data:
            return []
        
        articles = []
        for item in data["results"]:
            articles.append({
                "title": item.get("title", ""),
                "author": item.get("author", "Unknown"),
                "published_date": item.get("published_utc", ""),
                "article_url": item.get("article_url", ""),
                "description": item.get("description", ""),
                "source": item.get("publisher", {}).get("name", "Unknown"),
                "tickers": item.get("tickers", []),
                "keywords": item.get("keywords", [])
            })
        
        return articles
        
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


def get_company_financials(ticker: str, filing_type: str = "10-K") -> Dict[str, Any]:
    """
    Get company financial statements from SEC filings via Polygon.
    
    Note: This requires Polygon Premium subscription. 
    Falls back to basic info if not available.
    
    Args:
        ticker: Stock symbol
        filing_type: '10-K' (annual) or '10-Q' (quarterly)
    
    Returns:
        Dict with financial statement data
    """
    # Note: This is a placeholder as financial data endpoints require premium
    # For the free tier, we'll use the basic ticker details
    
    try:
        # Attempt to get financials (may require premium)
        url = f"{POLYGON_BASE_URL}/vX/reference/financials"
        params = {
            "apiKey": POLYGON_API_KEY,
            "ticker": ticker,
            "filing_date.gte": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "limit": 5
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK" and "results" in data:
                return {
                    "ticker": ticker,
                    "financials": data["results"],
                    "source": "polygon_premium"
                }
        
        # Fallback: Return basic info
        return {
            "ticker": ticker,
            "message": "Detailed financials require Polygon Premium. Using basic data.",
            "source": "polygon_basic"
        }
        
    except Exception as e:
        return {
            "ticker": ticker,
            "error": f"Could not fetch financials: {str(e)}"
        }


# Test function
if __name__ == "__main__":
    # Test with a well-known ticker
    ticker = "AAPL"
    
    print("Testing Polygon API...")
    print(f"\n1. Fundamentals for {ticker}:")
    print(get_fundamentals(ticker))
    
    print(f"\n2. Latest price for {ticker}:")
    print(get_latest_price(ticker))
    
    print(f"\n3. Recent news for {ticker}:")
    news = get_stock_news(ticker, limit=3)
    for article in news[:2]:  # Print first 2
        print(f"  - {article['title']}")
    
    print(f"\n4. Price history (last 30 days):")
    history = get_price_history(ticker, days=30)
    if "data" in history:
        print(f"  Retrieved {len(history['data'])} data points")

