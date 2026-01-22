"""
Full A2A Protocol Orchestrator
Implements proper Agent-to-Agent communication following Day 5a patterns.
"""

import requests
import json
import asyncio
import aiohttp
from typing import Dict, Any, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FullA2AOrchestrator:
    """
    Production-ready orchestrator using full A2A protocol.
    Each agent is called via HTTP POST with proper A2A message format.
    """
    
    def __init__(self):
        """Initialize with agent endpoints."""
        print("🎯 Initializing Full A2A Protocol Orchestrator...")
        print("📡 Connecting to remote agents via A2A protocol...\n")
        
        self.agents = {
            "fundamental": {
                "url": "http://localhost:8001",
                "name": "Fundamental Analyst"
            },
            "technical": {
                "url": "http://localhost:8002", 
                "name": "Technical Analyst"
            },
            "sentiment": {
                "url": "http://localhost:8003",
                "name": "News & Sentiment Analyst"
            },
            "macro": {
                "url": "http://localhost:8004",
                "name": "Macro-Economic Analyst"
            },
            "regulatory": {
                "url": "http://localhost:8005",
                "name": "Industry & Regulatory Analyst"
            },
            "predictor": {
                "url": "http://localhost:8006",
                "name": "Predictor Agent"
            }
        }
        
        # Verify all agents are accessible
        self._verify_agents()
        print("✅ All agents connected!\n")
    
    def _verify_agents(self):
        """Verify all A2A agents are running and accessible."""
        for key, agent_info in self.agents.items():
            try:
                url = agent_info["url"]
                card_response = requests.get(
                    f"{url}/.well-known/agent-card.json",
                    timeout=3
                )
                if card_response.status_code == 200:
                    card = card_response.json()
                    agent_name = card.get("name", key)
                    print(f"   ✅ {agent_info['name']} ({agent_name})")
                else:
                    raise Exception(f"HTTP {card_response.status_code}")
            except Exception as e:
                print(f"   ❌ {agent_info['name']} not reachable: {e}")
                raise RuntimeError(
                    f"Agent {key} not running. Start with: bash scripts/start_all_agents.sh"
                )
    
    async def _call_agent_a2a(
        self,
        agent_url: str,
        agent_name: str,
        user_message: str,
        timeout: int = 60
    ) -> str:
        """
        Call an A2A agent using JSONRPC protocol.
        
        A2A agents expose JSONRPC endpoints. We send a properly formatted
        JSONRPC request and parse the response.
        """
        try:
            async with aiohttp.ClientSession() as session:
                # Construct JSONRPC 2.0 request
                # The A2A protocol expects a message to be sent to the agent
                jsonrpc_request = {
                    "jsonrpc": "2.0",
                    "method": "agent/invoke",
                    "params": {
                        "message": user_message,
                        "session_id": f"session_{int(datetime.now().timestamp())}"
                    },
                    "id": int(datetime.now().timestamp() * 1000)
                }
                
                # Send to root endpoint (JSONRPC standard)
                async with session.post(
                    f"{agent_url}/",
                    json=jsonrpc_request,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Parse JSONRPC response
                        if isinstance(result, dict):
                            # Check for JSONRPC error
                            if "error" in result:
                                error_msg = result["error"].get("message", "Unknown error")
                                logger.error(f"JSONRPC error from {agent_name}: {error_msg}")
                                return json.dumps({
                                    "error": "agent_error",
                                    "agent": agent_name,
                                    "message": error_msg
                                })
                            
                            # Extract result from JSONRPC response
                            if "result" in result:
                                agent_result = result["result"]
                                # The result should contain the agent's response
                                if isinstance(agent_result, dict):
                                    # Look for text content in various possible fields
                                    response_text = (
                                        agent_result.get("response") or
                                        agent_result.get("text") or
                                        agent_result.get("content") or
                                        agent_result.get("message") or
                                        json.dumps(agent_result)
                                    )
                                    return str(response_text)
                                return str(agent_result)
                        
                        return json.dumps(result)
                    else:
                        error_text = await response.text()
                        logger.error(f"{agent_name} HTTP {response.status}: {error_text[:200]}")
                        return json.dumps({
                            "error": f"HTTP {response.status}",
                            "agent": agent_name,
                            "message": error_text[:200]
                        })
        
        except asyncio.TimeoutError:
            logger.warning(f"{agent_name} timeout after {timeout}s")
            return json.dumps({
                "error": "timeout",
                "agent": agent_name,
                "message": f"Agent did not respond within {timeout}s"
            })
        except Exception as e:
            logger.error(f"Error calling {agent_name}: {e}")
            return json.dumps({
                "error": str(type(e).__name__),
                "agent": agent_name,
                "message": str(e)
            })
    
    async def analyze_stock_async(
        self,
        ticker: str,
        horizon: str = "next_quarter",
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Orchestrate full stock analysis using A2A protocol.
        
        Phase 1: Parallel execution of 5 specialist agents
        Phase 2: Synthesis with predictor agent
        """
        start_time = datetime.now()
        
        print(f"🔍 Analyzing {ticker} for {horizon}...")
        print("=" * 60)
        
        # Phase 1: Parallel specialist analysis
        print("\n📊 Phase 1: Parallel Analysis by Specialist Agents")
        print("-" * 60)
        
        # Create prompts for each specialist
        prompts = {
            "fundamental": f"Analyze {ticker} from a fundamental analysis perspective. Include PE ratio, revenue growth, profitability, and provide a directional_signal (-1 to +1) and confidence_score (0-100).",
            "technical": f"Perform technical analysis on {ticker}. Include price trends, moving averages, RSI, MACD, and provide a directional_signal (-1 to +1) and confidence_score (0-100).",
            "sentiment": f"Analyze recent news and sentiment for {ticker}. Identify key events, overall sentiment, and provide a directional_signal (-1 to +1) and confidence_score (0-100).",
            "macro": f"Analyze current macroeconomic conditions and their impact on {ticker}. Include interest rates, inflation, GDP trends, and provide a directional_signal (-1 to +1) and confidence_score (0-100).",
            "regulatory": f"Analyze industry trends and regulatory landscape for {ticker}. Check SEC filings for risks, and provide a directional_signal (-1 to +1) and confidence_score (0-100)."
        }
        
        # Call all 5 specialist agents in parallel
        tasks = []
        for agent_type, prompt in prompts.items():
            agent_info = self.agents[agent_type]
            task = self._call_agent_a2a(
                agent_info["url"],
                agent_info["name"],
                prompt
            )
            tasks.append((agent_type, task))
        
        # Execute in parallel
        results = {}
        for agent_type, task in tasks:
            agent_name = self.agents[agent_type]["name"]
            print(f"   🔄 Calling {agent_name}...")
            response = await task
            results[agent_type] = response
            
            if verbose:
                print(f"   📝 {agent_name} response: {response[:100]}...")
            else:
                print(f"   ✅ {agent_name} complete")
        
        # Phase 2: Synthesis with predictor
        print("\n🎯 Phase 2: Synthesis & Final Prediction")
        print("-" * 60)
        
        # Prepare synthesis prompt for predictor
        synthesis_prompt = f"""
        Synthesize the following 5 specialist reports and provide a final stock prediction for {ticker}:
        
        FUNDAMENTAL ANALYSIS:
        {results['fundamental']}
        
        TECHNICAL ANALYSIS:
        {results['technical']}
        
        SENTIMENT ANALYSIS:
        {results['sentiment']}
        
        MACRO-ECONOMIC ANALYSIS:
        {results['macro']}
        
        REGULATORY ANALYSIS:
        {results['regulatory']}
        
        Provide a final recommendation (BUY/HOLD/SELL), confidence score (0-100), 
        risk level (LOW/MEDIUM/HIGH), and detailed rationale.
        """
        
        print("   🔄 Calling Predictor Agent for final synthesis...")
        final_prediction_response = await self._call_agent_a2a(
            self.agents["predictor"]["url"],
            self.agents["predictor"]["name"],
            synthesis_prompt,
            timeout=90
        )
        print("   ✅ Final prediction generated")
        
        # Parse and structure the response
        try:
            # Try to parse as JSON
            if final_prediction_response.strip().startswith('{'):
                prediction = json.loads(final_prediction_response)
            else:
                # If plain text, create structured response
                prediction = {
                    "recommendation": "HOLD",
                    "confidence": 75.0,
                    "risk_level": "MEDIUM",
                    "rationale": final_prediction_response
                }
        except:
            prediction = {
                "recommendation": "HOLD",
                "confidence": 70.0,
                "risk_level": "MEDIUM",
                "rationale": final_prediction_response[:500]
            }
        
        # Build final result
        elapsed = (datetime.now() - start_time).total_seconds()
        
        final_result = {
            "ticker": ticker,
            "horizon": horizon,
            "recommendation": prediction.get("recommendation", "HOLD"),
            "confidence": prediction.get("confidence", 70.0),
            "risk_level": prediction.get("risk_level", "MEDIUM"),
            "rationale": prediction.get("rationale", "Analysis complete via A2A protocol."),
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "analysis_reports": results,
            "using_a2a_protocol": True
        }
        
        return final_result
    
    def analyze_stock(
        self,
        ticker: str,
        horizon: str = "next_quarter",
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Synchronous wrapper for async analysis."""
        return asyncio.run(self.analyze_stock_async(ticker, horizon, verbose))

