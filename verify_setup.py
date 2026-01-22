#!/usr/bin/env python3
"""
API Keys Verification Script
Tests all API keys and their connectivity
"""

import os
import sys
from dotenv import load_dotenv
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_status(service, status, message):
    """Print a status line."""
    icon = "✅" if status == "OK" else "❌" if status == "FAIL" else "⚠️"
    print(f"{icon} {service:20s} [{status:^6s}] {message}")

def check_env_var(var_name, required=True):
    """Check if an environment variable is set."""
    value = os.getenv(var_name)
    if value:
        # Mask the key for security (show first 8 chars only)
        masked = value[:8] + "..." if len(value) > 8 else "***"
        return True, masked
    else:
        return False, "Not set"

def test_google_api():
    """Test Google Gemini API key."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return False, "API key not set"
    
    try:
        # Test with a simple API call
        url = "https://generativelanguage.googleapis.com/v1beta/models"
        params = {"key": api_key}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            return True, "API key valid and working"
        elif response.status_code == 401:
            return False, "Invalid API key"
        elif response.status_code == 403:
            return False, "API key valid but access forbidden"
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)[:50]}"

def test_polygon_api():
    """Test Polygon.io API key."""
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        return False, "API key not set"
    
    try:
        # Test with ticker endpoint
        url = "https://api.polygon.io/v3/reference/tickers"
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {"limit": 1}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                return True, "API key valid and working"
            else:
                return True, "API key valid (no data returned)"
        elif response.status_code == 401:
            return False, "Invalid API key"
        elif response.status_code == 403:
            return False, "Access forbidden (check subscription)"
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)[:50]}"

def test_fred_api():
    """Test FRED API key."""
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        return False, "API key not set (optional but recommended)"
    
    try:
        # Test with GDP series
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": "GDP",
            "api_key": api_key,
            "file_type": "json",
            "limit": 1,
            "sort_order": "desc"
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("observations"):
                return True, "API key valid and working"
            else:
                return True, "API key valid (no data returned)"
        elif response.status_code == 400:
            error_msg = response.json().get("error_message", "Invalid request")
            if "api_key" in error_msg.lower():
                return False, "Invalid API key"
            else:
                return False, error_msg
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)[:50]}"

def test_news_api():
    """Test NewsAPI.org key (optional)."""
    api_key = os.getenv("NEWS_API_KEY")
    if not api_key:
        return None, "Not set (optional - using Polygon news)"
    
    try:
        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "apiKey": api_key,
            "country": "us",
            "pageSize": 1
        }
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                return True, "API key valid and working"
            else:
                return False, data.get("message", "Unknown error")
        elif response.status_code == 401:
            return False, "Invalid API key"
        else:
            return False, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)[:50]}"

def test_dependencies():
    """Test if required Python packages are installed."""
    required_packages = [
        ("google.adk", "google-adk"),
        ("google.adk.a2a.utils.agent_to_a2a", "google-adk[a2a]"),
        ("pydantic", "pydantic"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("xgboost", "xgboost"),
        ("talib", "ta-lib"),
    ]
    
    results = []
    for module_name, package_name in required_packages:
        try:
            __import__(module_name)
            results.append((package_name, True, "Installed"))
        except ImportError:
            results.append((package_name, False, "Missing"))
    
    return results

def main():
    print_header("🔍 Stock Prediction System - Setup Verification")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    
    # Check .env file exists
    print_header("📁 Environment File")
    if os.path.exists(".env"):
        print_status(".env file", "OK", "Found")
    else:
        print_status(".env file", "FAIL", "Not found! Copy .env.example to .env")
        print("\n❌ CRITICAL: .env file missing!")
        print("Run: cp .env.example .env")
        print("Then edit .env and add your API keys")
        return False
    
    # Check environment variables
    print_header("🔑 Environment Variables")
    
    all_vars = [
        ("GOOGLE_API_KEY", True),
        ("POLYGON_API_KEY", True),
        ("FRED_API_KEY", False),
        ("NEWS_API_KEY", False),
    ]
    
    for var_name, required in all_vars:
        is_set, value = check_env_var(var_name, required)
        if is_set:
            print_status(var_name, "OK", f"Set: {value}")
        elif required:
            print_status(var_name, "FAIL", "REQUIRED but not set")
        else:
            print_status(var_name, "WARN", "Optional - not set")
    
    # Test API connectivity
    print_header("🌐 API Connectivity Tests")
    
    api_tests = [
        ("Google Gemini", test_google_api, True),
        ("Polygon.io", test_polygon_api, True),
        ("FRED", test_fred_api, False),
        ("NewsAPI", test_news_api, False),
    ]
    
    results = []
    for service, test_func, required in api_tests:
        print(f"\nTesting {service}...", end=" ")
        success, message = test_func()
        
        if success is True:
            status = "OK"
        elif success is False:
            status = "FAIL"
        else:
            status = "SKIP"
        
        print_status(service, status, message)
        results.append((service, success, required))
    
    # Test Python dependencies
    print_header("📦 Python Dependencies")
    dep_results = test_dependencies()
    
    for package, installed, message in dep_results:
        status = "OK" if installed else "FAIL"
        print_status(package, status, message)
    
    # Summary
    print_header("📊 Summary")
    
    critical_failures = []
    warnings = []
    
    # Check critical APIs
    for service, success, required in results:
        if required and success is False:
            critical_failures.append(service)
        elif not required and success is False:
            warnings.append(service)
    
    # Check critical dependencies
    for package, installed, _ in dep_results:
        if not installed:
            critical_failures.append(f"Python package: {package}")
    
    if critical_failures:
        print("\n❌ CRITICAL ISSUES FOUND:")
        for issue in critical_failures:
            print(f"   • {issue}")
        print("\n🔧 Fix these issues before running the system!")
        return False
    elif warnings:
        print("\n⚠️  WARNINGS (optional components):")
        for warning in warnings:
            print(f"   • {warning}")
        print("\n✅ System can run, but some features may be limited")
        return True
    else:
        print("\n✅ ALL CHECKS PASSED!")
        print("🚀 Your system is ready to run!")
        print("\nNext steps:")
        print("  1. bash scripts/start_all_agents.sh")
        print("  2. python main.py --ticker GOOGL")
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

