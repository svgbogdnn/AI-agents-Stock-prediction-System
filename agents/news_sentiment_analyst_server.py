"""
News & Sentiment Analyst Agent - A2A Server (Port 8003)
Analyzes news articles, social sentiment, and event impact.
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types

from config.agent_prompts import SENTIMENT_ANALYST_PROMPT
from tools import news_fetcher

load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# Define tools for sentiment analysis
def get_recent_news(ticker: str, days: int = 7) -> str:
    """
    Get recent news articles for a stock.
    
    Args:
        ticker: Stock symbol
        days: Number of days to look back (default: 7)
    
    Returns:
        JSON string with news articles
    """
    import json
    articles = news_fetcher.get_recent_news(ticker, days=days, limit=20)
    return json.dumps(articles, indent=2)


def analyze_news_sentiment(ticker: str, days: int = 7) -> str:
    """
    Get news articles with sentiment analysis.
    
    Args:
        ticker: Stock symbol
        days: Days to look back (default: 7)
    
    Returns:
        JSON string with articles, sentiment scores, and key events
    """
    import json
    sentiment_data = news_fetcher.get_news_with_sentiment(ticker, days=days)
    return json.dumps(sentiment_data, indent=2)


def detect_key_events(ticker: str) -> str:
    """
    Detect significant events from recent news.
    
    Args:
        ticker: Stock symbol
    
    Returns:
        JSON string with detected events
    """
    import json
    articles = news_fetcher.get_recent_news(ticker, days=14, limit=30)
    events = news_fetcher.detect_key_events(articles)
    return json.dumps({"ticker": ticker, "key_events": events}, indent=2)


# Create the Sentiment Analyst Agent
sentiment_analyst = LlmAgent(
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config, generation_config={
        "response_mime_type": "application/json",
        "temperature": 0.4  # Slightly higher for nuanced sentiment interpretation
    }),
    name="sentiment_analyst",
    description="Expert sentiment analyst specializing in news analysis and event detection. Analyzes market sentiment, identifies key events, and assesses their impact on stock prices.",
    instruction=SENTIMENT_ANALYST_PROMPT,
    tools=[get_recent_news, analyze_news_sentiment, detect_key_events]
)

# Expose agent via A2A protocol
app = to_a2a(sentiment_analyst, port=8003)

print("✅ Sentiment Analyst Agent initialized")
print("   Model: gemini-2.0-flash-exp")
print("   Tools: get_recent_news, analyze_news_sentiment, detect_key_events")
print("   Port: 8003")
print("   Ready to serve via A2A protocol...")

if __name__ == "__main__":
    import uvicorn
    
    print("\n🚀 Starting Sentiment Analyst A2A server on port 8003...")
    print("   Agent card: http://localhost:8003/.well-known/agent-card.json")
    
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")

