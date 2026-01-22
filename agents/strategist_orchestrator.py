"""
The Strategist - Orchestrator Agent
Coordinates all specialized agents using RemoteA2aAgent (A2A Protocol).
This is the main entry point for stock analysis requests.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.models.google_llm import Gemini
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from config.agent_prompts import STRATEGIST_ORCHESTRATOR_PROMPT
from config.schemas import PredictionReport

load_dotenv()

retry_config = types.HttpRetryOptions(
    attempts=5,
    exp_base=7,
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504]
)


class StrategistOrchestrator:
    """
    The Strategist orchestrates the entire stock prediction workflow.
    Uses A2A protocol to communicate with remote specialist agents.
    """
    
    def _create_remote_agent(self, base_url: str, name: str) -> RemoteA2aAgent:
        """Helper to create a RemoteA2aAgent using its agent card URL."""
        try:
            # The agent_card parameter can be a URL string pointing to the agent card
            card_url = f"{base_url}/.well-known/agent-card.json"
            
            # Create RemoteA2aAgent with the agent card URL
            return RemoteA2aAgent(name=name, agent_card=card_url)
        except Exception as e:
            logger.error(f"Failed to connect to {name} at {base_url}: {e}")
            raise RuntimeError(f"Agent {name} is not reachable at {base_url}. Make sure all agents are running: bash scripts/start_all_agents.sh")
    
    async def _run_agent_and_get_response(self, agent: RemoteA2aAgent, prompt: str) -> str:
        """Helper to run an agent and collect its final response."""
        from google.adk.agents.invocation_context import InvocationContext
        
        # Create invocation context
        context = InvocationContext()
        
        # Run agent and collect events
        final_response = ""
        async for event in agent.run_async(context):
            # Collect text from response events
            if hasattr(event, 'text') and event.text:
                final_response += event.text
            elif hasattr(event, 'content') and event.content:
                final_response += str(event.content)
        
        return final_response
    
    def __init__(self):
        """Initialize the orchestrator with remote agent connections."""
        
        print("🎯 Initializing The Strategist Orchestrator...")
        print("📡 Connecting to remote agents via A2A protocol...")
        
        # Create remote agent connections (A2A protocol)
        self.fundamental_agent = self._create_remote_agent("http://localhost:8001", "fundamental_analyst")
        print("   ✅ Connected to Fundamental Analyst")
        
        self.technical_agent = self._create_remote_agent("http://localhost:8002", "technical_analyst")
        print("   ✅ Connected to Technical Analyst")
        
        self.sentiment_agent = self._create_remote_agent("http://localhost:8003", "news_sentiment_analyst")
        print("   ✅ Connected to Sentiment Analyst")
        
        self.macro_agent = self._create_remote_agent("http://localhost:8004", "macro_analyst")
        print("   ✅ Connected to Macro Analyst")
        
        self.regulatory_agent = self._create_remote_agent("http://localhost:8005", "regulatory_analyst")
        print("   ✅ Connected to Regulatory Analyst")
        
        self.predictor_agent = self._create_remote_agent("http://localhost:8006", "predictor_agent")
        print("   ✅ Connected to Predictor Agent")
        
        print("✅ All agents connected successfully!\n")
        
        # Session management (Day 3a pattern)
        self.session_service = InMemorySessionService()
        
        print("✅ Strategist initialized with 6 remote A2A agents")
    
    async def analyze_stock_async(
        self,
        ticker: str,
        horizon: str = "next_quarter",
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Async version: Analyze a stock using all specialist agents.
        
        Args:
            ticker: Stock symbol (e.g., 'GOOGL')
            horizon: Prediction horizon ('next_week', 'next_quarter', 'next_year')
            verbose: Whether to return intermediate agent outputs
        
        Returns:
            Dict with final prediction and optionally intermediate results
        """
        start_time = datetime.now()
        
        if verbose:
            print(f"\n🔍 Analyzing {ticker} for {horizon}...")
            print("=" * 60)
        
        # Create session for this analysis
        session_id = f"{ticker}_{start_time.timestamp()}"
        
        try:
            # Step 1: Parallel invocation of all 5 analysis agents
            if verbose:
                print("\n📊 Phase 1: Parallel Analysis by Specialist Agents")
                print("-" * 60)
            
            analysis_tasks = [
                self._call_agent_async("fundamental", ticker, verbose),
                self._call_agent_async("technical", ticker, verbose),
                self._call_agent_async("sentiment", ticker, verbose),
                self._call_agent_async("macro", ticker, verbose),
                self._call_agent_async("regulatory", ticker, verbose)
            ]
            
            # Run all analyses in parallel
            analysis_results = await asyncio.gather(*analysis_tasks, return_exceptions=True)
            
            # Collect results
            fundamental_report = analysis_results[0] if not isinstance(analysis_results[0], Exception) else {"error": str(analysis_results[0])}
            technical_report = analysis_results[1] if not isinstance(analysis_results[1], Exception) else {"error": str(analysis_results[1])}
            sentiment_report = analysis_results[2] if not isinstance(analysis_results[2], Exception) else {"error": str(analysis_results[2])}
            macro_report = analysis_results[3] if not isinstance(analysis_results[3], Exception) else {"error": str(analysis_results[3])}
            regulatory_report = analysis_results[4] if not isinstance(analysis_results[4], Exception) else {"error": str(analysis_results[4])}
            
            # Step 2: Synthesize with Predictor agent
            if verbose:
                print("\n🎯 Phase 2: Synthesis & Prediction")
                print("-" * 60)
            
            prediction_prompt = f"""
            Analyze these 5 specialist reports and generate a final prediction for {ticker}:
            
            Fundamental Report: {json.dumps(fundamental_report)}
            Technical Report: {json.dumps(technical_report)}
            Sentiment Report: {json.dumps(sentiment_report)}
            Macro Report: {json.dumps(macro_report)}
            Regulatory Report: {json.dumps(regulatory_report)}
            
            Use the ml_model_predict tool to generate the final recommendation.
            """
            
            # Call predictor via A2A
            prediction_response_text = await self._run_agent_and_get_response(self.predictor_agent, prediction_prompt)
            
            # Parse prediction
            try:
                prediction = json.loads(prediction_response_text)
            except:
                prediction = {
                    "recommendation": "HOLD",
                    "confidence": 0.0,
                    "risk_level": "HIGH",
                    "rationale": "Could not generate prediction due to parsing error.",
                    "error": "Prediction parsing failed"
                }
            
            # Calculate elapsed time
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # Compile final result
            result = {
                "ticker": ticker,
                "horizon": horizon,
                "prediction": prediction,
                "elapsed_time_seconds": round(elapsed, 2),
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id
            }
            
            if verbose:
                result["intermediate_reports"] = {
                    "fundamental": fundamental_report,
                    "technical": technical_report,
                    "sentiment": sentiment_report,
                    "macro": macro_report,
                    "regulatory": regulatory_report
                }
            
            if verbose:
                print("\n" + "=" * 60)
                print(f"✅ Analysis complete in {elapsed:.2f} seconds")
                print("=" * 60)
            
            return result
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "ticker": ticker,
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_stock(
        self,
        ticker: str,
        horizon: str = "next_quarter",
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Synchronous wrapper for analyze_stock_async.
        
        Args:
            ticker: Stock symbol
            horizon: Prediction horizon
            verbose: Return intermediate outputs
        
        Returns:
            Analysis result dict
        """
        # Run async function in event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.analyze_stock_async(ticker, horizon, verbose)
        )
    
    async def _call_agent_async(
        self,
        agent_type: str,
        ticker: str,
        verbose: bool
    ) -> Dict[str, Any]:
        """Call a specialist agent asynchronously."""
        
        agent_map = {
            "fundamental": (self.fundamental_agent, "Fundamental Analyst"),
            "technical": (self.technical_agent, "Technical Analyst"),
            "sentiment": (self.sentiment_agent, "Sentiment Analyst"),
            "macro": (self.macro_agent, "Macro Analyst"),
            "regulatory": (self.regulatory_agent, "Regulatory Analyst")
        }
        
        agent, name = agent_map.get(agent_type, (None, "Unknown"))
        
        if not agent:
            return {"error": f"Unknown agent type: {agent_type}"}
        
        if verbose:
            print(f"  → Querying {name}...")
        
        try:
            # Create appropriate prompt for each agent type
            prompts = {
                "fundamental": f"Analyze the fundamental financials for {ticker}. Provide directional_signal, confidence_score, and key metrics.",
                "technical": f"Perform technical analysis for {ticker}. Include RSI, MACD, trend, directional_signal, and confidence_score.",
                "sentiment": f"Analyze recent news sentiment for {ticker}. Provide overall sentiment, key events, directional_signal, and confidence_score.",
                "macro": f"Analyze current macro-economic conditions and their impact on stocks like {ticker}. Provide market_regime, directional_signal, and confidence_score.",
                "regulatory": f"Check for regulatory risks and industry trends for {ticker}. Review SEC filings and provide directional_signal and confidence_score."
            }
            
            prompt = prompts.get(agent_type, f"Analyze {ticker}")
            
            # Call agent via A2A
            response_text = await self._run_agent_and_get_response(agent, prompt)
            
            try:
                result = json.loads(response_text)
            except:
                # If not JSON, wrap in dict
                result = {
                    "agent": agent_type,
                    "raw_response": response_text,
                    "directional_signal": 0.0,
                    "confidence_score": 50.0
                }
            
            if verbose:
                print(f"  ✓ {name} complete")
            
            return result
            
        except Exception as e:
            if verbose:
                print(f"  ✗ {name} failed: {str(e)}")
            
            return {
                "error": str(e),
                "agent": agent_type,
                "ticker": ticker
            }


# CLI interface
def main():
    """Command-line interface for The Strategist."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Stock Prediction System - The Strategist")
    parser.add_argument("--ticker", "-t", required=True, help="Stock ticker symbol (e.g., GOOGL)")
    parser.add_argument("--horizon", "-H", default="next_quarter", help="Prediction horizon")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show intermediate outputs")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    strategist = StrategistOrchestrator()
    
    # Run analysis
    result = strategist.analyze_stock(
        ticker=args.ticker.upper(),
        horizon=args.horizon,
        verbose=args.verbose
    )
    
    # Output results
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Pretty print
        print("\n" + "=" * 70)
        print(f"STOCK PREDICTION REPORT: {result.get('ticker')}")
        print("=" * 70)
        
        prediction = result.get("prediction", {})
        
        print(f"\n📊 RECOMMENDATION: {prediction.get('recommendation', 'N/A')}")
        print(f"💪 CONFIDENCE: {prediction.get('confidence', 0)}%")
        print(f"⚠️  RISK LEVEL: {prediction.get('risk_level', 'N/A')}")
        
        if prediction.get('price_target'):
            print(f"🎯 PRICE TARGET: ${prediction['price_target']}")
        
        print(f"\n📝 RATIONALE:")
        print(prediction.get('rationale', 'No rationale available'))
        
        print(f"\n⏱️  Analysis completed in {result.get('elapsed_time_seconds', 0)} seconds")
        print("=" * 70)


if __name__ == "__main__":
    main()

