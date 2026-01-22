"""
Macro-Economic Analyst Agent - A2A Server (Port 8004)
Analyzes broader economic conditions and their impact on stocks.
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.models.google_llm import Gemini
from google.genai import types

from config.agent_prompts import MACRO_ANALYST_PROMPT
from tools import fred_fetcher

load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)

# Define tools for macro-economic analysis
def get_macro_indicators() -> str:
    """
    Get key macro-economic indicators for market analysis.
    
    Returns:
        JSON string with GDP growth, inflation, unemployment, Fed rates, Treasury yields
    """
    import json
    indicators = fred_fetcher.get_macro_indicators()
    return json.dumps(indicators, indent=2)


def get_gdp_data() -> str:
    """
    Get GDP growth data.
    
    Returns:
        JSON string with GDP data and trends
    """
    import json
    gdp = fred_fetcher.get_gdp_data()
    return json.dumps(gdp, indent=2)


def get_inflation_data() -> str:
    """
    Get inflation data (CPI).
    
    Returns:
        JSON string with inflation rates and trends
    """
    import json
    inflation = fred_fetcher.get_inflation_data()
    return json.dumps(inflation, indent=2)


def get_fed_rate() -> str:
    """
    Get Federal Funds Rate.
    
    Returns:
        JSON string with current Fed rate and trend
    """
    import json
    fed_rate = fred_fetcher.get_fed_rate()
    return json.dumps(fed_rate, indent=2)


def get_treasury_yields() -> str:
    """
    Get Treasury yields for different maturities.
    
    Returns:
        JSON string with 2Y, 10Y, and 30Y Treasury yields
    """
    import json
    yields = {
        "2_year": fred_fetcher.get_treasury_yield("2"),
        "10_year": fred_fetcher.get_treasury_yield("10"),
        "30_year": fred_fetcher.get_treasury_yield("30")
    }
    return json.dumps(yields, indent=2)


# Create the Macro Analyst Agent
macro_analyst = LlmAgent(
    model=Gemini(model="gemini-2.0-flash-exp", retry_options=retry_config, generation_config={
        "response_mime_type": "application/json",
        "temperature": 0.3
    }),
    name="macro_analyst",
    description="Expert macro-economic analyst specializing in how broader economic conditions affect stock markets. Analyzes GDP, inflation, interest rates, and market regimes.",
    instruction=MACRO_ANALYST_PROMPT,
    tools=[
        get_macro_indicators,
        get_gdp_data,
        get_inflation_data,
        get_fed_rate,
        get_treasury_yields
    ]
)

# Expose agent via A2A protocol
app = to_a2a(macro_analyst, port=8004)

print("✅ Macro Analyst Agent initialized")
print("   Model: gemini-2.0-flash-exp")
print("   Tools: get_macro_indicators, get_gdp_data, get_inflation_data, get_fed_rate, get_treasury_yields")
print("   Port: 8004")
print("   Ready to serve via A2A protocol...")

if __name__ == "__main__":
    import uvicorn
    
    print("\n🚀 Starting Macro Analyst A2A server on port 8004...")
    print("   Agent card: http://localhost:8004/.well-known/agent-card.json")
    
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="info")

