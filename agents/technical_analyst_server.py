"""
Technical Analyst Agent - A2A Server (Port 8002)
Analyzes price patterns, technical indicators, and market momentum.
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types

from config.agent_prompts import TECHNICAL_ANALYST_PROMPT
from tools import technical_indicators, polygon_fetcher

load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# Define tools for technical analysis
def get_technical_indicators(ticker: str, days: int = 365) -> str:
    """
    Calculate comprehensive technical indicators for a stock.
    
    Args:
        ticker: Stock symbol
        days: Number of days of historical data (default: 365)
    
    Returns:
        JSON string with RSI, MACD, moving averages, Bollinger Bands, etc.
    """
    import json
    indicators = technical_indicators.calculate_indicators(ticker, days=days)
    return json.dumps(indicators, indent=2)


def get_price_history(ticker: str, days: int = 180) -> str:
    """
    Get historical price and volume data.
    
    Args:
        ticker: Stock symbol
        days: Number of days of historical data (default: 180)
    
    Returns:
        JSON string with price history
    """
    import json
    history = polygon_fetcher.get_price_history(ticker, days=days)
    return json.dumps(history, indent=2)


def get_support_resistance(ticker: str) -> str:
    """
    Identify key support and resistance levels.
    
    Args:
        ticker: Stock symbol
    
    Returns:
        JSON string with support and resistance levels
    """
    import json
    levels = technical_indicators.get_support_resistance(ticker)
    return json.dumps(levels, indent=2)


# Create the Technical Analyst Agent
technical_analyst = LlmAgent(
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config, generation_config={
        "response_mime_type": "application/json",
        "temperature": 0.3
    }),
    name="technical_analyst",
    description="Expert technical analyst specializing in price action, chart patterns, and momentum indicators. Analyzes RSI, MACD, moving averages, and trend identification.",
    instruction=TECHNICAL_ANALYST_PROMPT,
    tools=[get_technical_indicators, get_price_history, get_support_resistance]
)

# Expose agent via A2A protocol
app = to_a2a(technical_analyst, port=8002)

print("✅ Technical Analyst Agent initialized")
print("   Model: gemini-2.0-flash-exp")
print("   Tools: get_technical_indicators, get_price_history, get_support_resistance")
print("   Port: 8002")
print("   Ready to serve via A2A protocol...")

if __name__ == "__main__":
    import uvicorn
    
    print("\n🚀 Starting Technical Analyst A2A server on port 8002...")
    print("   Agent card: http://localhost:8002/.well-known/agent-card.json")
    
    uvicorn.run(app, host="0.0.0.0", port=8002, log_level="info")

