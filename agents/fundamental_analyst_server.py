"""
Fundamental Analyst Agent - A2A Server (Port 8001)
Analyzes company financials, valuation metrics, and earnings.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types

from config.agent_prompts import FUNDAMENTAL_ANALYST_PROMPT
from tools import polygon_fetcher, sec_edgar_fetcher

load_dotenv()

# Configure retry options (from Day 5 lab pattern)
retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# Define tools for fundamental analysis
def get_fundamentals(ticker: str) -> str:
    """
    Get fundamental financial data for a stock.
    
    Args:
        ticker: Stock symbol (e.g., 'GOOGL', 'AAPL')
    
    Returns:
        JSON string with fundamental metrics
    """
    import json
    result = polygon_fetcher.get_fundamentals(ticker)
    return json.dumps(result, indent=2)


def get_sec_filings(ticker: str, filing_type: str = "10-K") -> str:
    """
    Get recent SEC filings for a company.
    
    Args:
        ticker: Stock symbol
        filing_type: '10-K' (annual) or '10-Q' (quarterly)
    
    Returns:
        JSON string with filing information
    """
    import json
    filings = sec_edgar_fetcher.get_recent_filings(ticker, filing_type, count=2)
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


# Create the Fundamental Analyst Agent
fundamental_analyst = LlmAgent(
    model=Gemini(
        model="gemini-2.0-flash-exp", 
        retry_options=retry_config,
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.3
        }
    ),
    name="fundamental_analyst",
    description="Expert fundamental analyst specializing in company valuation and financial statement analysis. Analyzes balance sheets, income statements, cash flows, and valuation metrics.",
    instruction=FUNDAMENTAL_ANALYST_PROMPT,
    tools=[get_fundamentals, get_sec_filings, get_risk_factors]
)

# Expose agent via A2A protocol
app = to_a2a(fundamental_analyst, port=8001)

print("✅ Fundamental Analyst Agent initialized")
print("   Model: gemini-2.0-flash-exp")
print("   Tools: get_fundamentals, get_sec_filings, get_risk_factors")
print("   Port: 8001")
print("   Ready to serve via A2A protocol...")

# Run the A2A server
if __name__ == "__main__":
    import uvicorn
    
    print("\n🚀 Starting Fundamental Analyst A2A server on port 8001...")
    print("   Agent card: http://localhost:8001/.well-known/agent-card.json")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")

