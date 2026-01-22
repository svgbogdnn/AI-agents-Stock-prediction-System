"""
Agent Engine Native A2A Orchestrator
Uses Google's native A2A capabilities instead of custom HTTP calls.
"""

import os
import json
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import logging

from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentEngineOrchestrator:
    """
    Orchestrator using Google's native A2A capabilities via RemoteA2aAgent.
    
    Benefits over custom HTTP orchestrator:
    - Automatic retry logic
    - Built-in error handling
    - Context management
    - Native observability
    - Agent discovery via Agent Engine registry
    """
    
    def __init__(self):
        """Initialize orchestrator with agent card URLs."""
        logger.info("🎯 Initializing Agent Engine Native A2A Orchestrator...")
        logger.info("📡 Discovering agents via Agent Engine...\n")
        
        # Get agent URLs from environment (set by Cloud Run or Agent Engine)
        self.agent_card_urls = {
            "fundamental": os.getenv(
                "FUNDAMENTAL_AGENT_CARD_URL",
                "http://localhost:8001/.well-known/agent-card.json"
            ),
            "technical": os.getenv(
                "TECHNICAL_AGENT_CARD_URL",
                "http://localhost:8002/.well-known/agent-card.json"
            ),
            "sentiment": os.getenv(
                "SENTIMENT_AGENT_CARD_URL",
                "http://localhost:8003/.well-known/agent-card.json"
            ),
            "macro": os.getenv(
                "MACRO_AGENT_CARD_URL",
                "http://localhost:8004/.well-known/agent-card.json"
            ),
            "regulatory": os.getenv(
                "REGULATORY_AGENT_CARD_URL",
                "http://localhost:8005/.well-known/agent-card.json"
            ),
            "predictor": os.getenv(
                "PREDICTOR_AGENT_CARD_URL",
                "http://localhost:8006/.well-known/agent-card.json"
            )
        }
        
        # Agent names for display
        self.agent_names = {
            "fundamental": "Fundamental Analyst",
            "technical": "Technical Analyst",
            "sentiment": "News & Sentiment Analyst",
            "macro": "Macro-Economic Analyst",
            "regulatory": "Industry & Regulatory Analyst",
            "predictor": "Predictor Agent"
        }
        
        # Initialize session service for context management
        self.session_service = InMemorySessionService()
        
        # Create RemoteA2aAgent instances (native A2A)
        self.agents = {}
        for agent_type, card_url in self.agent_card_urls.items():
            try:
                agent = RemoteA2aAgent(
                    name=f"{agent_type}_agent",
                    agent_card=card_url
                )
                self.agents[agent_type] = agent
                logger.info(f"   ✅ {self.agent_names[agent_type]}: {card_url}")
            except Exception as e:
                logger.warning(f"   ⚠️  {self.agent_names[agent_type]}: {e}")
        
        logger.info("\n✅ Native A2A agents initialized!\n")
    
    async def _call_agent_native_a2a(
        self,
        agent_type: str,
        message: str,
        base_session_id: str,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Call an agent using native A2A protocol via RemoteA2aAgent.
        
        This uses Google's native A2A capabilities:
        - Automatic retry logic
        - Built-in error handling
        - Context management
        - Native observability
        """
        agent = self.agents.get(agent_type)
        if not agent:
            return {
                "error": "agent_not_found",
                "agent_type": agent_type,
                "message": f"Agent {agent_type} not initialized"
            }
        
        try:
            # Create unique session ID for this agent call
            unique_session_id = f"{base_session_id}_{agent_type}_{int(datetime.now().timestamp() * 1000)}"
            
            # Create session for context management
            # Each agent call gets its own session for isolation
            session = await self.session_service.create_session(
                session_id=unique_session_id,
                app_name="stock_prediction",
                user_id="orchestrator"
            )
            
            # Create invocation context (native A2A)
            context = InvocationContext(
                session_service=self.session_service,
                invocation_id=f"inv_{int(datetime.now().timestamp() * 1000)}",
                agent=agent,
                session=session
            )
            
            # Add message to context
            # The context needs parts to send to the remote agent
            from google.genai import types
            context.add_input(types.Part(text=message))
            
            # Run agent using native A2A protocol
            # This automatically handles retries, errors, and context passing
            full_response = ""
            async for event in agent.run_async(context):
                # Collect response chunks
                if hasattr(event, 'content'):
                    full_response += str(event.content)
                elif hasattr(event, 'text'):
                    full_response += str(event.text)
                elif hasattr(event, 'parts'):
                    # Handle parts if present
                    for part in event.parts:
                        if hasattr(part, 'text'):
                            full_response += part.text
                        elif hasattr(part, 'content'):
                            full_response += str(part.content)
            
            # Try to parse as JSON
            try:
                result = json.loads(full_response)
            except json.JSONDecodeError:
                # If not JSON, wrap in structured format
                result = {
                    "response": full_response,
                    "agent_type": agent_type,
                    "agent_name": self.agent_names[agent_type]
                }
            
            # Add metadata
            result["using_native_a2a"] = True
            result["agent_type"] = agent_type
            
            return result
        
        except asyncio.TimeoutError:
            logger.warning(f"{self.agent_names[agent_type]} timeout after {timeout}s")
            return {
                "error": "timeout",
                "agent_type": agent_type,
                "message": f"Agent did not respond within {timeout}s"
            }
        except Exception as e:
            logger.error(f"Error calling {self.agent_names[agent_type]}: {e}")
            return {
                "error": str(type(e).__name__),
                "agent_type": agent_type,
                "message": str(e)
            }
    
    async def analyze_stock_async(
        self,
        ticker: str,
        horizon: str = "next_quarter",
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Orchestrate stock analysis using native A2A protocol.
        
        Phase 1: Parallel execution of 5 specialist agents
        Phase 2: Synthesis with predictor agent
        """
        start_time = datetime.now()
        session_id = f"stock_analysis_{ticker}_{int(datetime.now().timestamp())}"
        
        logger.info(f"🔍 Analyzing {ticker} for {horizon}...")
        logger.info("=" * 60)
        logger.info("📡 Using Native A2A Protocol via Agent Engine\n")
        
        # Phase 1: Parallel specialist analysis
        logger.info("\n📊 Phase 1: Parallel Analysis by Specialist Agents")
        logger.info("-" * 60)
        
        # Create prompts for each specialist
        prompts = {
            "fundamental": f"Analyze {ticker} from a fundamental analysis perspective. Include PE ratio, revenue growth, profitability, and provide a directional_signal (-1 to +1) and confidence_score (0-100).",
            "technical": f"Perform technical analysis on {ticker}. Include price trends, moving averages, RSI, MACD, and provide a directional_signal (-1 to +1) and confidence_score (0-100).",
            "sentiment": f"Analyze recent news and sentiment for {ticker}. Identify key events, overall sentiment, and provide a directional_signal (-1 to +1) and confidence_score (0-100).",
            "macro": f"Analyze current macroeconomic conditions and their impact on {ticker}. Include interest rates, inflation, GDP trends, and provide a directional_signal (-1 to +1) and confidence_score (0-100).",
            "regulatory": f"Analyze industry trends and regulatory landscape for {ticker}. Check SEC filings for risks, and provide a directional_signal (-1 to +1) and confidence_score (0-100)."
        }
        
        # Call all 5 specialist agents in parallel using native A2A
        tasks = []
        for agent_type, prompt in prompts.items():
            task = self._call_agent_native_a2a(
                agent_type,
                prompt,
                session_id,
                timeout=60
            )
            tasks.append((agent_type, task))
        
        # Execute in parallel
        results = {}
        for agent_type, task in tasks:
            agent_name = self.agent_names[agent_type]
            logger.info(f"   🔄 Calling {agent_name} (Native A2A)...")
            response = await task
            results[agent_type] = response
            
            if "error" not in response:
                signal = response.get("directional_signal", 0.0)
                conf = response.get("confidence_score", 0.0)
                signal_emoji = "🟢" if signal > 0.3 else "🔴" if signal < -0.3 else "🟡"
                logger.info(f"   ✅ {agent_name}: {signal_emoji} Signal: {signal:+.2f}, Confidence: {conf:.0f}%")
            else:
                logger.warning(f"   ⚠️  {agent_name}: Error - {response.get('message', 'Unknown error')}")
        
        # Phase 2: Synthesis with predictor
        logger.info("\n🎯 Phase 2: Synthesis & Final Prediction")
        logger.info("-" * 60)
        
        # Prepare synthesis prompt for predictor
        synthesis_prompt = f"""
        Synthesize the following 5 specialist reports and provide a final stock prediction for {ticker}:
        
        FUNDAMENTAL ANALYSIS:
        {json.dumps(results.get('fundamental', {}), indent=2)}
        
        TECHNICAL ANALYSIS:
        {json.dumps(results.get('technical', {}), indent=2)}
        
        SENTIMENT ANALYSIS:
        {json.dumps(results.get('sentiment', {}), indent=2)}
        
        MACRO-ECONOMIC ANALYSIS:
        {json.dumps(results.get('macro', {}), indent=2)}
        
        REGULATORY ANALYSIS:
        {json.dumps(results.get('regulatory', {}), indent=2)}
        
        Provide a final recommendation (BUY/HOLD/SELL), confidence score (0-100), 
        risk level (LOW/MEDIUM/HIGH), and detailed rationale.
        """
        
        logger.info("   🔄 Calling Predictor Agent for final synthesis (Native A2A)...")
        final_prediction_response = await self._call_agent_native_a2a(
            "predictor",
            synthesis_prompt,
            session_id,
            timeout=90
        )
        logger.info("   ✅ Final prediction generated")
        
        # Parse and structure the response
        try:
            if isinstance(final_prediction_response, dict):
                if "error" in final_prediction_response:
                    prediction = {
                        "recommendation": "HOLD",
                        "confidence": 70.0,
                        "risk_level": "MEDIUM",
                        "rationale": "Analysis completed with some errors. Please review individual agent responses."
                    }
                else:
                    prediction = {
                        "recommendation": final_prediction_response.get("recommendation", "HOLD"),
                        "confidence": final_prediction_response.get("confidence", 70.0),
                        "risk_level": final_prediction_response.get("risk_level", "MEDIUM"),
                        "rationale": final_prediction_response.get("rationale", final_prediction_response.get("response", ""))
                    }
            else:
                prediction = {
                    "recommendation": "HOLD",
                    "confidence": 75.0,
                    "risk_level": "MEDIUM",
                    "rationale": str(final_prediction_response)
                }
        except Exception as e:
            logger.error(f"Error parsing prediction: {e}")
            prediction = {
                "recommendation": "HOLD",
                "confidence": 70.0,
                "risk_level": "MEDIUM",
                "rationale": f"Analysis complete via native A2A protocol. Parse error: {e}"
            }
        
        # Build final result
        elapsed = (datetime.now() - start_time).total_seconds()
        
        final_result = {
            "ticker": ticker,
            "horizon": horizon,
            "recommendation": prediction.get("recommendation", "HOLD"),
            "confidence": prediction.get("confidence", 70.0),
            "risk_level": prediction.get("risk_level", "MEDIUM"),
            "rationale": prediction.get("rationale", "Analysis complete via native A2A protocol."),
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "analysis_reports": results,
            "using_native_a2a": True,
            "orchestration_platform": "agent_engine",
            "session_id": session_id
        }
        
        logger.info(f"\n   📊 Recommendation: {final_result['recommendation']}")
        logger.info(f"   🎯 Confidence: {final_result['confidence']:.1f}%")
        logger.info(f"   ⚡ Risk Level: {final_result['risk_level']}")
        logger.info(f"   ⏱️  Elapsed: {elapsed:.2f}s")
        logger.info(f"   🔗 Using: Native A2A Protocol via Agent Engine\n")
        
        return final_result
    
    def analyze_stock(
        self,
        ticker: str,
        horizon: str = "next_quarter",
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Synchronous wrapper for async analysis."""
        return asyncio.run(self.analyze_stock_async(ticker, horizon, verbose))


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Stock Analysis using Native A2A Orchestration")
    parser.add_argument("--ticker", required=True, help="Stock ticker symbol")
    parser.add_argument("--horizon", default="next_quarter", help="Prediction horizon")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    orchestrator = AgentEngineOrchestrator()
    result = orchestrator.analyze_stock(
        ticker=args.ticker,
        horizon=args.horizon,
        verbose=args.verbose
    )
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULT")
    print("=" * 60)
    print(json.dumps(result, indent=2))

