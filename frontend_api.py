#!/usr/bin/env python3
"""
FastAPI server for the frontend to communicate with the Python backend.
This wraps the KaggleOrchestrator and exposes it as a REST API.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import appropriate orchestrator based on deployment environment
if os.getenv("CLOUD_DEPLOYMENT") == "true" or os.getenv("K_SERVICE"):  # K_SERVICE is set by Cloud Run
    from agents.cloud_orchestrator import CloudOrchestrator as Orchestrator
else:
    from agents.kaggle_orchestrator import KaggleOrchestrator as Orchestrator

app = FastAPI(
    title="Stock Prediction API",
    description="Multi-Agent Stock Prediction System with A2A Protocol",
    version="1.0.0"
)

# CORS middleware for Next.js frontend and cloud deployment
allowed_origins = [
    "http://localhost:3001",  # Next.js dev server
    "http://127.0.0.1:3001",
    "https://*.appspot.com",  # App Engine
    "https://*.run.app",  # Cloud Run
]

# Add specific project URL if provided
if project_url := os.getenv("FRONTEND_URL"):
    allowed_origins.append(project_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"https://.*\.(appspot\.com|run\.app)",
)

# Initialize orchestrator lazily to avoid startup failures
orchestrator = None

def get_orchestrator():
    """Get or initialize orchestrator. Lazy initialization for Cloud Run."""
    global orchestrator
    if orchestrator is None:
        try:
            orchestrator = Orchestrator()
        except Exception as e:
            logger.error(f"Failed to initialize orchestrator: {e}")
            # Return a minimal orchestrator that won't crash
            from agents.kaggle_orchestrator import KaggleOrchestrator
            orchestrator = KaggleOrchestrator()
    return orchestrator


class AnalyzeRequest(BaseModel):
    ticker: str
    horizon: str = "next_quarter"


class HealthResponse(BaseModel):
    status: str
    message: str
    agents_status: dict


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Stock Prediction API",
        "status": "running",
        "version": "1.0.0",
        "authors": "svg"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check health of all A2A agents"""
    try:
        orch = get_orchestrator()
        agents_status = orch.check_agents_health()
        all_healthy = all(status == "online" for status in agents_status.values())
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "message": "All agents online" if all_healthy else "Some agents offline",
            "agents_status": agents_status
        }
    except Exception as e:
        # Return degraded status instead of crashing
        return {
            "status": "degraded",
            "message": f"Health check error: {str(e)}",
            "agents_status": {}
        }


@app.post("/agent-explanation")
async def generate_agent_explanation(request: dict):
    """
    Generate human-readable explanation of what an agent's output means using Gemini.
    
    Args:
        agent_id: ID of the agent (fundamental, technical, sentiment, macro, regulatory, predictor)
        agent_report: The agent's analysis report
        ticker: Stock ticker symbol
    
    Returns:
        Plain-English explanation of what the agent's data means
    """
    try:
        import requests
        import os
        import json
        
        agent_id = request.get('agent_id', '')
        agent_report = request.get('agent_report', {})
        ticker = request.get('ticker', 'Unknown')
        
        agent_names = {
            'fundamental': 'Fundamental Analyst',
            'technical': 'Technical Analyst',
            'sentiment': 'Sentiment Analyst',
            'macro': 'Macro Analyst',
            'regulatory': 'Regulatory Analyst',
            'predictor': 'Predictor Agent'
        }
        
        agent_name = agent_names.get(agent_id, agent_id)
        
        print(f"\n🧠 Generating explanation for {agent_name} ({ticker})...")
        
        # Format the agent report for the prompt
        report_text = json.dumps(agent_report, indent=2)
        
        # Create Gemini prompt
        prompt = f"""You are a financial education expert. Explain what this {agent_name} output means in simple, human-readable terms.

Stock: {ticker}
Agent: {agent_name}

Agent Output:
{report_text}

Please explain:
1. What does the directional signal ({agent_report.get('directional_signal', 0)}) mean in plain English?
2. What does the confidence score ({agent_report.get('confidence_score', 0)}%) tell us?
3. What do the key metrics/data points mean and why are they important?
4. What does the summary/analysis tell us about the stock?
5. How should an investor interpret this agent's findings?

Write in clear, conversational language. Avoid jargon. Use analogies when helpful. Keep it concise (2-3 paragraphs). Focus on what matters to an investor.
"""
        
        # Call Gemini REST API
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
            
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        explanation = result['candidates'][0]['content']['parts'][0]['text']
        
        print(f"✅ Generated explanation ({len(explanation)} characters)\n")
        
        return {
            "explanation": explanation,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "ticker": ticker,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"❌ Error generating agent explanation: {error_msg}")
        print(traceback.format_exc())
        
        # Fallback: Generate a simple explanation from the data
        signal = agent_report.get('directional_signal', 0)
        confidence = agent_report.get('confidence_score', 0)
        summary = agent_report.get('summary', '')
        
        if signal > 0.3:
            signal_meaning = "strongly bullish (positive outlook)"
        elif signal > 0:
            signal_meaning = "slightly bullish (cautiously positive)"
        elif signal < -0.3:
            signal_meaning = "strongly bearish (negative outlook)"
        elif signal < 0:
            signal_meaning = "slightly bearish (cautiously negative)"
        else:
            signal_meaning = "neutral (no strong directional bias)"
        
        confidence_level = 'high certainty' if confidence > 70 else 'moderate certainty' if confidence > 50 else 'low certainty'
        signal_direction = 'positive' if signal > 0 else 'negative' if signal < 0 else 'neutral'
        
        fallback_explanation = f"""The {agent_name} indicates a {signal_meaning} signal of {signal:.3f} with {confidence}% confidence. 

This means the agent's analysis suggests {signal_direction} factors for {ticker}. The confidence level of {confidence}% indicates {confidence_level} in this assessment.

{f'Summary: {summary}' if summary else 'Review the key metrics and data sources above for more details.'}"""
        
        return {
            "explanation": fallback_explanation,
            "agent_id": agent_id,
            "agent_name": agent_name,
            "ticker": ticker,
            "generated_at": datetime.now().isoformat(),
            "fallback": True,
            "error": error_msg if "GOOGLE_API_KEY" in error_msg else None
        }


@app.post("/investor-advice")
async def generate_investor_advice(request: dict):
    """
    Generate plain-English investor advice from analysis results using Gemini.
    
    Args:
        analysis: Complete analysis result from orchestrator
    
    Returns:
        Investor-friendly advice and recommendations
    """
    try:
        import requests
        import os
        
        analysis = request.get('analysis', {})
        ticker = analysis.get('ticker', 'Unknown')
        recommendation = analysis.get('recommendation', 'HOLD')
        confidence = analysis.get('confidence', 0)
        risk_level = analysis.get('risk_level', 'MEDIUM')
        rationale = analysis.get('rationale', '')
        
        print(f"\n🧠 Generating investor advice for {ticker}...")
        
        # Create Gemini prompt
        prompt = f"""You are an experienced investment advisor. Based on the multi-agent AI analysis below, provide clear, actionable advice for a retail investor.

Analysis Results for {ticker}:
- Recommendation: {recommendation}
- Confidence: {confidence}%
- Risk Level: {risk_level}

Detailed Analysis:
{rationale}

Please provide:
1. A clear summary of what this means for an investor
2. Key risks and opportunities
3. Practical next steps
4. Important considerations

Write in plain English, avoiding jargon. Be balanced and mention both positives and negatives. Keep it concise (3-4 paragraphs).
"""
        
        # Call Gemini REST API directly (v1beta with models/ prefix)
        api_key = os.environ.get("GOOGLE_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        advice = result['candidates'][0]['content']['parts'][0]['text']
        
        print(f"✅ Generated {len(advice)} characters of advice\n")
        
        return {
            "advice": advice,
            "ticker": ticker,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error generating investor advice with Gemini: {str(e)}")
        print(f"📝 Generating intelligent analysis based on agent data...\n")
        
        # Extract detailed data from analysis reports
        reports = analysis.get('analysis_reports', {})
        
        # Analyze each agent's contribution
        fund_data = reports.get('fundamental', {})
        tech_data = reports.get('technical', {})
        sent_data = reports.get('sentiment', {})
        macro_data = reports.get('macro', {})
        reg_data = reports.get('regulatory', {})
        
        # Build intelligent, data-driven insights
        
        # 1. Summarize what the recommendation means
        if recommendation == 'BUY':
            action_summary = f"Our multi-agent system identifies {ticker} as a **buying opportunity**. The analysis shows {confidence:.1f}% confidence, indicating that multiple factors align positively."
        elif recommendation == 'SELL':
            action_summary = f"Our multi-agent system suggests **reducing exposure** to {ticker}. With {confidence:.1f}% confidence, several risk factors have been identified."
        else:
            action_summary = f"Our multi-agent system recommends a **wait-and-see approach** for {ticker}. At {confidence:.1f}% confidence, the analysis shows mixed signals that warrant patience."
        
        # 2. Analyze the strongest signals
        signals = {
            'Fundamental': fund_data.get('directional_signal', 0),
            'Technical': tech_data.get('directional_signal', 0),
            'Sentiment': sent_data.get('directional_signal', 0),
            'Macro': macro_data.get('directional_signal', 0),
            'Regulatory': reg_data.get('directional_signal', 0)
        }
        
        positive_agents = [name for name, sig in signals.items() if sig > 0.2]
        negative_agents = [name for name, sig in signals.items() if sig < -0.2]
        neutral_agents = [name for name, sig in signals.items() if -0.2 <= sig <= 0.2]
        
        # 3. Build signal analysis
        if positive_agents:
            positive_text = f"**Positive indicators** from {', '.join(positive_agents)} analysis suggest potential upside."
        else:
            positive_text = ""
            
        if negative_agents:
            negative_text = f"**Caution flags** from {', '.join(negative_agents)} analysis indicate downside risks."
        else:
            negative_text = ""
            
        if neutral_agents:
            neutral_text = f"{', '.join(neutral_agents)} analysis shows neutral positioning."
        else:
            neutral_text = ""
        
        signal_summary = ' '.join(filter(None, [positive_text, negative_text, neutral_text]))
        
        # 4. Extract key metrics for context
        fund_metrics = fund_data.get('key_metrics', {})
        tech_metrics = tech_data.get('key_metrics', {})
        macro_metrics = macro_data.get('key_metrics', {})
        
        # 5. Generate specific insights based on actual data
        insights = []
        
        # Fundamental insights
        if fund_data.get('directional_signal', 0) > 0.3:
            insights.append(f"- **Strong fundamentals**: {fund_data.get('summary', 'Positive financial indicators')}")
        elif fund_data.get('directional_signal', 0) < -0.3:
            insights.append(f"- **Fundamental concerns**: {fund_data.get('summary', 'Valuation or financial challenges')}")
        
        # Technical insights
        if tech_data.get('directional_signal', 0) > 0.3:
            insights.append(f"- **Bullish technicals**: {tech_data.get('summary', 'Positive momentum indicators')}")
        elif tech_data.get('directional_signal', 0) < -0.3:
            insights.append(f"- **Bearish technicals**: {tech_data.get('summary', 'Negative price action')}")
        
        # Sentiment insights
        news_count = sent_data.get('key_metrics', {}).get('news_count', 0)
        if news_count > 0:
            sentiment_tone = sent_data.get('key_metrics', {}).get('sentiment', 'neutral')
            insights.append(f"- **Market sentiment**: {news_count} recent articles show {sentiment_tone} tone")
        
        # Macro insights
        if macro_data.get('directional_signal', 0) != 0:
            regime = macro_metrics.get('market_regime', 'neutral')
            fed_rate = macro_metrics.get('fed_funds_rate', 'N/A')
            insights.append(f"- **Economic environment**: {regime.title()} regime with Fed rate at {fed_rate}")
        
        # Risk assessment
        risk_factors = []
        if risk_level == 'HIGH':
            risk_factors.append("High volatility expected")
            if confidence < 60:
                risk_factors.append("Lower confidence in prediction")
        elif risk_level == 'MEDIUM':
            risk_factors.append("Moderate risk from mixed signals")
        else:
            risk_factors.append("Relatively stable outlook")
        
        risk_text = "- " + "\n- ".join(risk_factors)
        
        # 6. Practical recommendations based on recommendation type
        if recommendation == 'BUY':
            next_steps = """1. Consider establishing a position sized according to your portfolio allocation strategy
2. Monitor the positive factors identified (especially """ + ', '.join(positive_agents[:2]) + """) for any changes
3. Set stop-loss levels based on technical support zones
4. Review quarterly earnings and news for confirmation of the thesis"""
        elif recommendation == 'SELL':
            next_steps = """1. Evaluate your current position and consider reducing exposure gradually
2. Watch for any improvement in """ + ', '.join(negative_agents[:2]) + """ indicators
3. Consider tax implications before executing trades
4. Maintain vigilance on news that could change the outlook"""
        else:
            next_steps = """1. Place {ticker} on your watchlist for future opportunities
2. Wait for clearer signals from """ + ', '.join(neutral_agents[:2]) + """ analysis
3. Monitor upcoming earnings reports and macroeconomic developments
4. Re-evaluate if confidence exceeds 75% or new catalysts emerge"""
        
        # Build final advice
        advice = f"""Based on our comprehensive 5-agent analysis system for {ticker}, here's what this means for investors:

## What This Means for You

{action_summary} {signal_summary}

## Key Insights from Agent Analysis

{chr(10).join(insights) if insights else '- Analysis shows balanced positioning across multiple factors'}

## Risk Assessment

{risk_text}

## Practical Next Steps

{next_steps}

## Important Considerations

**Diversification**: {ticker} should represent an appropriate portion of a diversified portfolio, not a concentrated bet.

**Time Horizon**: A {risk_level} risk profile means you should align this with your investment timeline and liquidity needs.

**Ongoing Monitoring**: Market conditions change. Revisit this analysis if major news, earnings, or economic shifts occur.

*This analysis synthesizes real-time data from Polygon (market data), FRED (macro indicators), NewsAPI (sentiment), and SEC filings (regulatory) through our A2A multi-agent architecture.*"""
        
        return {
            "advice": advice,
            "ticker": ticker,
            "generated_at": datetime.now().isoformat()
        }


@app.post("/analyze")
async def analyze_stock(request: AnalyzeRequest):
    """
    Analyze a stock using the multi-agent system.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'GOOGL')
        horizon: Analysis time horizon (default: 'next_quarter')
    
    Returns:
        Complete analysis with recommendation, confidence, and agent reports
    """
    try:
        print(f"\n{'='*70}")
        print(f"API Request: Analyzing {request.ticker}")
        print(f"{'='*70}\n")
        
        # Call orchestrator
        orch = get_orchestrator()
        result = orch.analyze_stock(
            ticker=request.ticker.upper(),
            horizon=request.horizon,
            verbose=False
        )
        
        print(f"\n✅ Analysis complete for {request.ticker}")
        print(f"   Recommendation: {result['recommendation']}")
        print(f"   Confidence: {result['confidence']:.1f}%\n")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error analyzing {request.ticker}: {str(e)}\n")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze {request.ticker}: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*70)
    print("🚀 Starting Stock Prediction API")
    print("="*70)
    print("\n📡 Endpoints:")
    print("   GET  /         - Service info")
    print("   GET  /health   - Health check")
    print("   POST /analyze  - Analyze stock")
    print("\n🌐 Frontend: http://localhost:3001")
    print("🔧 Backend:  http://localhost:8000")
    print("📖 Docs:     http://localhost:8000/docs")
    print("\n⚠️  Make sure all A2A agents are running:")
    print("   ./scripts/start_all_agents.sh")
    print("\n" + "="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

