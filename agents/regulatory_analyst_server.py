"""
Industry & Regulatory Analyst Agent - A2A Server (Port 8005)
Analyzes industry trends, regulatory risks, and legal issues.
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types

from config.agent_prompts import REGULATORY_ANALYST_PROMPT
from tools import sec_edgar_fetcher, news_fetcher

load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# Define tools for regulatory analysis
def get_sec_filings(ticker: str, filing_type: str = "10-K") -> str:
    """
    Get recent SEC filings for a company.
    
    Args:
        ticker: Stock symbol
        filing_type: '10-K' (annual), '10-Q' (quarterly), or '8-K' (current events)
    
    Returns:
        JSON string with filing information
    """
    import json
    filings = sec_edgar_fetcher.get_recent_filings(ticker, filing_type, count=3)
    return json.dumps(filings, indent=2)


def get_risk_factors(ticker: str) -> str:
    """
    Extract risk factors from the most recent 10-K filing.
    
    Args:
        ticker: Stock symbol
    
    Returns:
        JSON string with risk factors
    """
    import json
    risks = sec_edgar_fetcher.get_risk_factors(ticker)
    return json.dumps(risks, indent=2)


def check_8k_filings(ticker: str, days: int = 90) -> str:
    """
    Check for significant 8-K filings (material events).
    
    Args:
        ticker: Stock symbol
        days: Number of days to look back (default: 90)
    
    Returns:
        JSON string with recent 8-K filings and event types
    """
    import json
    filings_8k = sec_edgar_fetcher.check_recent_8k_filings(ticker, days=days)
    return json.dumps(filings_8k, indent=2)


def get_industry_news(ticker: str) -> str:
    """
    Get industry-related news for context.
    
    Args:
        ticker: Stock symbol
    
    Returns:
        JSON string with industry news
    """
    import json
    # Get broader industry news
    articles = news_fetcher.get_recent_news(ticker, days=30, limit=15)
    return json.dumps({"ticker": ticker, "industry_news": articles}, indent=2)


# Create the Regulatory Analyst Agent
regulatory_analyst = LlmAgent(
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config, generation_config={
        "response_mime_type": "application/json",
        "temperature": 0.3
    }),
    name="regulatory_analyst",
    description="Expert industry and regulatory analyst specializing in legal risks, compliance, and sector trends. Monitors SEC filings, litigation, regulatory changes, and industry dynamics.",
    instruction=REGULATORY_ANALYST_PROMPT,
    tools=[
        get_sec_filings,
        get_risk_factors,
        check_8k_filings,
        get_industry_news
    ]
)

# Expose agent via A2A protocol
app = to_a2a(regulatory_analyst, port=8005)

print("✅ Regulatory Analyst Agent initialized")
print("   Model: gemini-2.0-flash-exp")
print("   Tools: get_sec_filings, get_risk_factors, check_8k_filings, get_industry_news")
print("   Port: 8005")
print("   Ready to serve via A2A protocol...")

if __name__ == "__main__":
    import uvicorn
    
    print("\n🚀 Starting Regulatory Analyst A2A server on port 8005...")
    print("   Agent card: http://localhost:8005/.well-known/agent-card.json")
    
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")

