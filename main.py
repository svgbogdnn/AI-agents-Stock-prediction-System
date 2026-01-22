#!/usr/bin/env python3
"""
Stock Prediction System - Main Entry Point
Uses The Strategist orchestrator to analyze stocks via A2A protocol.
"""

import sys
import argparse
import json
from agents.kaggle_orchestrator import KaggleOrchestrator as StrategistOrchestrator


def main():
    """Main CLI interface."""
    
    parser = argparse.ArgumentParser(
        description="Stock Prediction System - Multi-Agent A2A Architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a stock
  python main.py --ticker GOOGL
  
  # Analyze with verbose output
  python main.py --ticker AAPL --verbose
  
  # Get JSON output
  python main.py --ticker TSLA --json
  
  # Specify prediction horizon
  python main.py --ticker NVDA --horizon next_year

For more information, see README.md
        """
    )
    
    parser.add_argument(
        "--ticker", "-t",
        required=True,
        help="Stock ticker symbol (e.g., GOOGL, AAPL, TSLA)"
    )
    
    parser.add_argument(
        "--horizon", "-H",
        default="next_quarter",
        choices=["next_week", "next_month", "next_quarter", "next_year"],
        help="Prediction time horizon (default: next_quarter)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed intermediate outputs from all agents"
    )
    
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results as JSON (for programmatic use)"
    )
    
    args = parser.parse_args()
    
    # Validate ticker format
    ticker = args.ticker.upper().strip()
    if not ticker.isalnum() or len(ticker) > 5:
        print(f"❌ Error: Invalid ticker symbol '{ticker}'")
        print("   Ticker should be 1-5 alphanumeric characters (e.g., GOOGL, AAPL)")
        sys.exit(1)
    
    try:
        # Initialize orchestrator
        if not args.json:
            print("\n" + "=" * 70)
            print("STOCK PREDICTION SYSTEM - Multi-Agent A2A Architecture")
            print("=" * 70)
            print(f"\n🎯 Initializing analysis for: {ticker}")
            print(f"📅 Prediction horizon: {args.horizon}")
            print("\n" + "-" * 70)
        
        strategist = StrategistOrchestrator()
        
        # Run analysis
        result = strategist.analyze_stock(
            ticker=ticker,
            horizon=args.horizon,
            verbose=args.verbose
        )
        
        # Check for errors
        if "error" in result:
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"\n❌ Analysis failed: {result['error']}")
            sys.exit(1)
        
        # Output results
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            display_results(result, args.verbose)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        sys.exit(130)
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("\nTroubleshooting:")
            print("  1. Make sure all agents are running: bash scripts/start_all_agents.sh")
            print("  2. Check your .env file has valid API keys")
            print("  3. Verify network connectivity")
        sys.exit(1)


def display_results(result: dict, verbose: bool):
    """Display results in human-readable format."""
    
    # Handle both nested and flat prediction formats
    prediction = result.get("prediction", result)
    
    print("\n" + "=" * 70)
    print(f"📊 STOCK PREDICTION REPORT: {result.get('ticker')}")
    print("=" * 70)
    
    # Main prediction
    recommendation = prediction.get("recommendation", "N/A")
    confidence = prediction.get("confidence", 0)
    risk_level = prediction.get("risk_level", "N/A")
    
    # Color coding for recommendation
    rec_symbol = {
        "BUY": "🟢 BUY",
        "HOLD": "🟡 HOLD",
        "SELL": "🔴 SELL"
    }.get(recommendation, recommendation)
    
    print(f"\n{'RECOMMENDATION:':<20} {rec_symbol}")
    print(f"{'CONFIDENCE:':<20} {confidence}%")
    print(f"{'RISK LEVEL:':<20} {risk_level}")
    
    if prediction.get("price_target"):
        print(f"{'PRICE TARGET:':<20} ${prediction['price_target']:.2f}")
    
    # Rationale
    print(f"\n{'=' * 70}")
    print("📝 ANALYSIS RATIONALE")
    print("=" * 70)
    print(prediction.get("rationale", "No rationale available"))
    
    # Contributing factors
    if "contributing_factors" in prediction:
        print(f"\n{'=' * 70}")
        print("⚖️  CONTRIBUTING FACTORS")
        print("=" * 70)
        
        factors = prediction["contributing_factors"]
        for factor, weight in sorted(factors.items(), key=lambda x: x[1], reverse=True):
            bar_length = int(weight * 50)
            bar = "█" * bar_length
            print(f"  {factor:<15} {weight:>6.1%} {bar}")
    
    # Individual scores
    if any(key in prediction for key in ["fundamental_score", "technical_score", "sentiment_score", "macro_score", "regulatory_score"]):
        print(f"\n{'=' * 70}")
        print("📊 INDIVIDUAL ANALYST SCORES")
        print("=" * 70)
        
        scores = {
            "Fundamental": prediction.get("fundamental_score"),
            "Technical": prediction.get("technical_score"),
            "Sentiment": prediction.get("sentiment_score"),
            "Macro-Economic": prediction.get("macro_score"),
            "Regulatory": prediction.get("regulatory_score")
        }
        
        for name, score in scores.items():
            if score is not None:
                # Signal ranges from -1 to 1
                normalized = (score + 1) / 2  # Convert to 0-1 range
                bar_length = int(normalized * 40)
                bar = "█" * bar_length
                signal_label = "Bullish" if score > 0.2 else "Bearish" if score < -0.2 else "Neutral"
                print(f"  {name:<18} {score:>5.2f} ({signal_label:<8}) {bar}")
    
    # Timing info
    print(f"\n{'=' * 70}")
    elapsed = result.get("elapsed_time_seconds", 0)
    timestamp = result.get("timestamp", "")
    print(f"⏱️  Analysis completed in {elapsed:.2f} seconds")
    print(f"🕐 Timestamp: {timestamp}")
    print("=" * 70)
    
    # Show intermediate reports if verbose
    if verbose and "intermediate_reports" in result:
        print("\n" + "=" * 70)
        print("🔍 DETAILED INTERMEDIATE REPORTS")
        print("=" * 70)
        
        reports = result["intermediate_reports"]
        for agent_name, report in reports.items():
            print(f"\n{agent_name.upper()} ANALYST:")
            print("-" * 70)
            print(json.dumps(report, indent=2))
    
    print("\n")


if __name__ == "__main__":
    main()

