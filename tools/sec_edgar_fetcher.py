"""
SEC EDGAR data fetcher for company filings (10-K, 10-Q, 8-K).
Scrapes and parses SEC filings for risk factors, MD&A, and key metrics.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re
import time


SEC_EDGAR_BASE = "https://www.sec.gov"
HEADERS = {
    "User-Agent": "Stock Prediction System academic@university.edu",  # SEC requires user agent
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}


def get_recent_filings(ticker: str, filing_type: str = "10-K", count: int = 3) -> List[Dict[str, Any]]:
    """
    Get recent SEC filings for a company.
    
    Args:
        ticker: Stock symbol
        filing_type: '10-K' (annual), '10-Q' (quarterly), or '8-K' (current events)
        count: Number of recent filings to retrieve
    
    Returns:
        List of dicts with filing information:
        - filing_date: Date of filing
        - filing_type: Type of filing
        - document_url: Link to full document
        - summary: Brief summary (if available)
    """
    try:
        # Search for company CIK (Central Index Key)
        cik = _get_cik_for_ticker(ticker)
        if not cik:
            return [{"error": f"Could not find CIK for ticker {ticker}"}]
        
        # Get company filings
        url = f"{SEC_EDGAR_BASE}/cgi-bin/browse-edgar"
        params = {
            "action": "getcompany",
            "CIK": cik,
            "type": filing_type,
            "dateb": "",
            "owner": "exclude",
            "count": count,
            "output": "atom"
        }
        
        response = requests.get(url, params=params, headers=HEADERS, timeout=10)
        response.raise_for_status()
        time.sleep(0.1)  # Be respectful to SEC servers
        
        # Parse XML/Atom feed
        soup = BeautifulSoup(response.content, "xml")
        entries = soup.find_all("entry")
        
        filings = []
        for entry in entries[:count]:
            filing_date = entry.find("filing-date").text if entry.find("filing-date") else "Unknown"
            filing_href = entry.find("filing-href").text if entry.find("filing-href") else ""
            summary = entry.find("summary").text if entry.find("summary") else ""
            
            filings.append({
                "filing_date": filing_date,
                "filing_type": filing_type,
                "document_url": filing_href,
                "summary": summary.strip(),
                "ticker": ticker,
                "cik": cik
            })
        
        return filings
        
    except Exception as e:
        return [{"error": f"Error fetching filings: {str(e)}", "ticker": ticker}]


def get_risk_factors(ticker: str) -> Dict[str, Any]:
    """
    Extract risk factors from the most recent 10-K filing.
    
    Args:
        ticker: Stock symbol
    
    Returns:
        Dict with risk factors and metadata
    """
    try:
        # Get most recent 10-K
        filings = get_recent_filings(ticker, filing_type="10-K", count=1)
        
        if not filings or "error" in filings[0]:
            return {
                "error": "Could not fetch 10-K filing",
                "ticker": ticker
            }
        
        filing = filings[0]
        document_url = filing.get("document_url", "")
        
        if not document_url:
            return {"error": "No document URL found"}
        
        # Fetch the filing document
        response = requests.get(document_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        time.sleep(0.1)
        
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        
        # Try to find "Risk Factors" section
        risk_section = _extract_section(text, "Risk Factors", max_chars=5000)
        
        return {
            "ticker": ticker,
            "filing_date": filing.get("filing_date"),
            "filing_type": "10-K",
            "risk_factors": risk_section,
            "document_url": document_url,
            "has_risks": bool(risk_section),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Error extracting risk factors: {str(e)}",
            "ticker": ticker
        }


def get_mda_section(ticker: str) -> Dict[str, Any]:
    """
    Extract Management Discussion & Analysis (MD&A) from most recent 10-K.
    
    Args:
        ticker: Stock symbol
    
    Returns:
        Dict with MD&A text and metadata
    """
    try:
        filings = get_recent_filings(ticker, filing_type="10-K", count=1)
        
        if not filings or "error" in filings[0]:
            return {"error": "Could not fetch 10-K filing"}
        
        filing = filings[0]
        document_url = filing.get("document_url", "")
        
        if not document_url:
            return {"error": "No document URL found"}
        
        response = requests.get(document_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        time.sleep(0.1)
        
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()
        
        # Extract MD&A section
        mda_section = _extract_section(
            text,
            "Management's Discussion and Analysis",
            max_chars=8000
        )
        
        return {
            "ticker": ticker,
            "filing_date": filing.get("filing_date"),
            "mda": mda_section,
            "document_url": document_url,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Error extracting MD&A: {str(e)}",
            "ticker": ticker
        }


def check_recent_8k_filings(ticker: str, days: int = 90) -> Dict[str, Any]:
    """
    Check for significant 8-K filings (material events) in recent period.
    
    Args:
        ticker: Stock symbol
        days: Number of days to look back
    
    Returns:
        Dict with recent 8-K filings and event types
    """
    try:
        filings = get_recent_filings(ticker, filing_type="8-K", count=10)
        
        if not filings or (filings and "error" in filings[0]):
            return {"error": "Could not fetch 8-K filings"}
        
        # Filter to recent filings
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        recent_filings = []
        
        for filing in filings:
            filing_date = filing.get("filing_date", "")
            if filing_date >= cutoff_date:
                # Classify the event type based on summary
                summary = filing.get("summary", "").lower()
                event_type = _classify_8k_event(summary)
                
                filing["event_type"] = event_type
                recent_filings.append(filing)
        
        return {
            "ticker": ticker,
            "recent_8k_count": len(recent_filings),
            "filings": recent_filings,
            "days_lookback": days,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "error": f"Error checking 8-K filings: {str(e)}",
            "ticker": ticker
        }


def _get_cik_for_ticker(ticker: str) -> Optional[str]:
    """
    Convert stock ticker to SEC CIK number.
    Uses SEC's company tickers JSON mapping.
    """
    try:
        # SEC provides a JSON mapping of tickers to CIKs
        url = "https://www.sec.gov/files/company_tickers.json"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Search for ticker
        ticker_upper = ticker.upper()
        for entry in data.values():
            if entry.get("ticker") == ticker_upper:
                # CIK needs to be zero-padded to 10 digits
                cik = str(entry.get("cik_str")).zfill(10)
                return cik
        
        return None
        
    except Exception as e:
        print(f"Error getting CIK: {e}")
        return None


def _extract_section(text: str, section_name: str, max_chars: int = 10000) -> str:
    """
    Extract a specific section from SEC filing text.
    
    Args:
        text: Full filing text
        section_name: Section to extract (e.g., "Risk Factors")
        max_chars: Maximum characters to return
    
    Returns:
        Extracted section text
    """
    # Try to find the section heading
    pattern = rf"(?i)(item\s+\d+[a-z]?\.?\s+)?{re.escape(section_name)}"
    match = re.search(pattern, text)
    
    if not match:
        return f"Could not locate '{section_name}' section"
    
    # Extract text starting from the match
    start_idx = match.end()
    
    # Find the next major section (usually starts with "Item")
    next_section = re.search(r"\n\s*Item\s+\d+", text[start_idx:start_idx + max_chars * 2])
    
    if next_section:
        end_idx = start_idx + next_section.start()
    else:
        end_idx = start_idx + max_chars
    
    section_text = text[start_idx:end_idx]
    
    # Clean up the text
    section_text = re.sub(r'\s+', ' ', section_text)  # Remove extra whitespace
    section_text = section_text.strip()
    
    # Truncate if too long
    if len(section_text) > max_chars:
        section_text = section_text[:max_chars] + "..."
    
    return section_text


def _classify_8k_event(summary: str) -> str:
    """
    Classify the type of event reported in an 8-K filing.
    
    Returns:
        Event type classification
    """
    summary_lower = summary.lower()
    
    if any(word in summary_lower for word in ["merger", "acquisition", "m&a"]):
        return "M&A"
    elif any(word in summary_lower for word in ["earnings", "results", "financial"]):
        return "Earnings"
    elif any(word in summary_lower for word in ["ceo", "cfo", "executive", "officer"]):
        return "Management Change"
    elif any(word in summary_lower for word in ["contract", "agreement", "deal"]):
        return "Material Agreement"
    elif any(word in summary_lower for word in ["lawsuit", "litigation", "settlement"]):
        return "Legal"
    elif any(word in summary_lower for word in ["dividend", "repurchase", "buyback"]):
        return "Capital Allocation"
    else:
        return "Other Material Event"


# Test function
if __name__ == "__main__":
    ticker = "AAPL"
    
    print(f"Testing SEC EDGAR fetcher for {ticker}...\n")
    
    print("1. Recent 10-K filings:")
    filings = get_recent_filings(ticker, "10-K", count=2)
    for filing in filings:
        if "error" not in filing:
            print(f"  - {filing['filing_date']}: {filing['document_url'][:80]}...")
    
    print("\n2. Recent 8-K filings:")
    eight_k = check_recent_8k_filings(ticker, days=90)
    if "recent_8k_count" in eight_k:
        print(f"  Found {eight_k['recent_8k_count']} recent 8-K filings")
        for filing in eight_k["filings"][:3]:
            print(f"  - {filing['filing_date']}: {filing['event_type']}")
    
    print("\n3. Risk factors (truncated):")
    risks = get_risk_factors(ticker)
    if "risk_factors" in risks and risks["risk_factors"]:
        print(f"  {risks['risk_factors'][:200]}...")

