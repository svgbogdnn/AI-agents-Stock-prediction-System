"""
FRED (Federal Reserve Economic Data) API fetcher for macro-economic indicators.
Fetches GDP, inflation, unemployment, Fed rates, VIX, Treasury yields, etc.
"""

import os
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")
FRED_BASE_URL = "https://api.stlouisfed.org/fred"


def get_macro_indicators() -> Dict[str, Any]:
    """
    Get key macro-economic indicators for market analysis.
    
    Returns:
        Dict containing:
        - gdp_growth: GDP growth rate (annual %)
        - inflation_rate: CPI inflation rate (annual %)
        - unemployment_rate: Unemployment rate (%)
        - fed_funds_rate: Federal Funds Rate (%)
        - ten_year_treasury: 10-Year Treasury Yield (%)
        - indicators: Dict of all raw indicator values
    """
    indicators = {}
    
    try:
        # Key FRED series IDs
        series = {
            "gdp_growth": "A191RL1Q225SBEA",  # Real GDP growth rate
            "inflation_cpi": "CPIAUCSL",  # Consumer Price Index
            "unemployment": "UNRATE",  # Unemployment rate
            "fed_funds_rate": "DFF",  # Federal Funds Rate
            "ten_year_treasury": "DGS10",  # 10-Year Treasury Yield
            "vix": None,  # VIX not in FRED, will handle separately
        }
        
        # Fetch each series
        for key, series_id in series.items():
            if series_id:
                value = _get_latest_value(series_id)
                indicators[key] = value
        
        # Calculate inflation rate (YoY change in CPI)
        if indicators.get("inflation_cpi"):
            inflation_rate = _calculate_inflation_rate("CPIAUCSL")
            indicators["inflation_rate"] = inflation_rate
        
        # Add market context
        indicators["market_regime"] = _determine_market_regime(indicators)
        indicators["timestamp"] = datetime.now().isoformat()
        
        return indicators
        
    except Exception as e:
        return {
            "error": f"Error fetching macro indicators: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }


def get_gdp_data() -> Dict[str, Any]:
    """Get GDP data including growth rate."""
    try:
        series_id = "A191RL1Q225SBEA"  # Real GDP growth rate
        
        data = _get_series_observations(series_id, limit=4)  # Last 4 quarters
        
        if not data:
            return {"error": "Could not fetch GDP data"}
        
        latest = data[-1]
        
        return {
            "series_id": series_id,
            "latest_value": latest["value"],
            "latest_date": latest["date"],
            "recent_values": data,
            "series_name": "Real GDP Growth Rate",
            "units": "Percent Change from Year Ago",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Error fetching GDP data: {str(e)}"}


def get_inflation_data() -> Dict[str, Any]:
    """Get inflation data (CPI)."""
    try:
        series_id = "CPIAUCSL"  # Consumer Price Index
        
        data = _get_series_observations(series_id, limit=12)  # Last 12 months
        
        if not data or len(data) < 12:
            return {"error": "Insufficient data for inflation calculation"}
        
        # Calculate YoY inflation rate
        current_cpi = float(data[-1]["value"])
        year_ago_cpi = float(data[0]["value"])
        inflation_rate = ((current_cpi - year_ago_cpi) / year_ago_cpi) * 100
        
        return {
            "series_id": series_id,
            "latest_cpi": current_cpi,
            "latest_date": data[-1]["date"],
            "inflation_rate_yoy": round(inflation_rate, 2),
            "series_name": "Consumer Price Index",
            "recent_values": data[-6:],  # Last 6 months
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Error fetching inflation data: {str(e)}"}


def get_fed_rate() -> Dict[str, Any]:
    """Get Federal Funds Rate."""
    try:
        series_id = "DFF"  # Daily Federal Funds Rate
        
        data = _get_series_observations(series_id, limit=30)  # Last 30 days
        
        if not data:
            return {"error": "Could not fetch Fed Funds Rate"}
        
        latest = data[-1]
        
        return {
            "series_id": series_id,
            "current_rate": latest["value"],
            "latest_date": latest["date"],
            "series_name": "Federal Funds Effective Rate",
            "units": "Percent",
            "recent_trend": _calculate_trend([float(d["value"]) for d in data]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Error fetching Fed rate: {str(e)}"}


def get_treasury_yield(maturity: str = "10") -> Dict[str, Any]:
    """
    Get Treasury yield for specified maturity.
    
    Args:
        maturity: '3' (3-month), '2' (2-year), '10' (10-year), '30' (30-year)
    
    Returns:
        Dict with treasury yield data
    """
    try:
        series_map = {
            "3": "DGS3MO",   # 3-Month
            "2": "DGS2",     # 2-Year
            "10": "DGS10",   # 10-Year
            "30": "DGS30"    # 30-Year
        }
        
        series_id = series_map.get(maturity, "DGS10")
        
        data = _get_series_observations(series_id, limit=30)
        
        if not data:
            return {"error": f"Could not fetch {maturity}-year Treasury yield"}
        
        # Filter out missing values (represented as ".")
        valid_data = [d for d in data if d["value"] != "."]
        
        if not valid_data:
            return {"error": "No valid Treasury yield data"}
        
        latest = valid_data[-1]
        
        return {
            "series_id": series_id,
            "maturity": f"{maturity}-Year",
            "current_yield": latest["value"],
            "latest_date": latest["date"],
            "series_name": f"{maturity}-Year Treasury Constant Maturity Rate",
            "units": "Percent",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Error fetching Treasury yield: {str(e)}"}


def get_unemployment_rate() -> Dict[str, Any]:
    """Get unemployment rate."""
    try:
        series_id = "UNRATE"  # Unemployment Rate
        
        data = _get_series_observations(series_id, limit=12)
        
        if not data:
            return {"error": "Could not fetch unemployment rate"}
        
        latest = data[-1]
        
        return {
            "series_id": series_id,
            "current_rate": latest["value"],
            "latest_date": latest["date"],
            "series_name": "Unemployment Rate",
            "units": "Percent",
            "recent_trend": _calculate_trend([float(d["value"]) for d in data]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"error": f"Error fetching unemployment rate: {str(e)}"}


def _get_latest_value(series_id: str) -> Optional[float]:
    """Get the latest value for a FRED series."""
    try:
        observations = _get_series_observations(series_id, limit=1)
        if observations:
            value_str = observations[-1]["value"]
            if value_str != ".":
                return float(value_str)
        return None
    except:
        return None


def _get_series_observations(
    series_id: str,
    limit: int = 100
) -> List[Dict[str, str]]:
    """
    Fetch observations for a FRED series.
    
    Args:
        series_id: FRED series ID
        limit: Number of most recent observations
    
    Returns:
        List of dicts with 'date' and 'value'
    """
    if not FRED_API_KEY:
        # Return mock data if no API key (for testing)
        return _get_mock_data(series_id)
    
    try:
        url = f"{FRED_BASE_URL}/series/observations"
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        observations = data.get("observations", [])
        
        # Reverse to get chronological order
        observations.reverse()
        
        return observations
        
    except Exception as e:
        print(f"Error fetching FRED series {series_id}: {e}")
        return []


def _calculate_inflation_rate(series_id: str) -> Optional[float]:
    """Calculate YoY inflation rate from CPI data."""
    try:
        data = _get_series_observations(series_id, limit=13)  # 13 months
        
        if len(data) < 13:
            return None
        
        current_cpi = float(data[-1]["value"])
        year_ago_cpi = float(data[0]["value"])
        
        inflation_rate = ((current_cpi - year_ago_cpi) / year_ago_cpi) * 100
        
        return round(inflation_rate, 2)
        
    except:
        return None


def _calculate_trend(values: List[float]) -> str:
    """Determine trend direction from a list of values."""
    if len(values) < 2:
        return "stable"
    
    recent_avg = sum(values[-3:]) / len(values[-3:])
    older_avg = sum(values[:3]) / len(values[:3])
    
    change_pct = ((recent_avg - older_avg) / older_avg) * 100
    
    if change_pct > 2:
        return "rising"
    elif change_pct < -2:
        return "falling"
    else:
        return "stable"


def _determine_market_regime(indicators: Dict[str, Any]) -> str:
    """
    Determine overall market regime based on macro indicators.
    
    Returns:
        'expansion', 'contraction', or 'uncertain'
    """
    try:
        gdp = indicators.get("gdp_growth")
        unemployment = indicators.get("unemployment")
        inflation = indicators.get("inflation_rate")
        
        # Simple rule-based classification
        if gdp and unemployment:
            gdp_val = float(gdp) if gdp else 0
            unemp_val = float(unemployment) if unemployment else 5
            
            if gdp_val > 2 and unemp_val < 5:
                return "expansion"
            elif gdp_val < 0 or unemp_val > 7:
                return "contraction"
        
        return "uncertain"
        
    except:
        return "uncertain"


def _get_mock_data(series_id: str) -> List[Dict[str, str]]:
    """Return mock data when FRED API key is not available."""
    # This allows the system to work for demo purposes
    mock_values = {
        "A191RL1Q225SBEA": "2.5",  # GDP growth
        "CPIAUCSL": "310.5",  # CPI
        "UNRATE": "3.8",  # Unemployment
        "DFF": "5.33",  # Fed Funds Rate
        "DGS10": "4.25",  # 10-Year Treasury
    }
    
    value = mock_values.get(series_id, "0")
    today = datetime.now().strftime("%Y-%m-%d")
    
    return [{"date": today, "value": value}]


# Test function
if __name__ == "__main__":
    print("Testing FRED API fetcher...\n")
    
    print("1. Macro Indicators:")
    macro = get_macro_indicators()
    for key, value in macro.items():
        if key not in ["timestamp", "error"]:
            print(f"  {key}: {value}")
    
    print("\n2. GDP Data:")
    gdp = get_gdp_data()
    if "latest_value" in gdp:
        print(f"  Latest GDP Growth: {gdp['latest_value']}% ({gdp['latest_date']})")
    
    print("\n3. Inflation Data:")
    inflation = get_inflation_data()
    if "inflation_rate_yoy" in inflation:
        print(f"  YoY Inflation: {inflation['inflation_rate_yoy']}%")
    
    print("\n4. Fed Funds Rate:")
    fed_rate = get_fed_rate()
    if "current_rate" in fed_rate:
        print(f"  Current Rate: {fed_rate['current_rate']}% (Trend: {fed_rate.get('recent_trend')})")
    
    print("\n5. Treasury Yields:")
    for maturity in ["2", "10", "30"]:
        treasury = get_treasury_yield(maturity)
        if "current_yield" in treasury:
            print(f"  {maturity}-Year: {treasury['current_yield']}%")

