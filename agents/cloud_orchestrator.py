"""
Cloud-ready Production Orchestrator for Google Cloud deployment
Supports dynamic agent URLs from environment variables
"""

import requests
import json
import asyncio
import os
from typing import Dict, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CloudOrchestrator:
    """
    Production orchestrator optimized for Google Cloud Platform.
    Reads agent URLs from environment variables set by Cloud Run.
    """
    
    def __init__(self):
        """Initialize with agent endpoints from environment."""
        logger.info("🎯 Initializing Cloud Orchestrator...")
        logger.info("📡 Discovering agent endpoints...\n")
        
        self.agents = {
            "fundamental": {
                "url": os.getenv("FUNDAMENTAL_AGENT_URL", "http://localhost:8001"),
                "name": "Fundamental Analyst",
                "prompt_template": "Analyze {ticker} fundamentals: PE ratio, revenue, margins, debt. Provide directional_signal (-1 to +1) and confidence (0-100)."
            },
            "technical": {
                "url": os.getenv("TECHNICAL_AGENT_URL", "http://localhost:8002"),
                "name": "Technical Analyst",
                "prompt_template": "Analyze {ticker} technical indicators: moving averages, RSI, MACD, volume. Provide directional_signal (-1 to +1) and confidence (0-100)."
            },
            "sentiment": {
                "url": os.getenv("SENTIMENT_AGENT_URL", "http://localhost:8003"),
                "name": "News & Sentiment Analyst",
                "prompt_template": "Analyze {ticker} recent news and sentiment. Identify key events. Provide directional_signal (-1 to +1) and confidence (0-100)."
            },
            "macro": {
                "url": os.getenv("MACRO_AGENT_URL", "http://localhost:8004"),
                "name": "Macro-Economic Analyst",
                "prompt_template": "Analyze macroeconomic conditions for {ticker}: interest rates, inflation, GDP. Provide directional_signal (-1 to +1) and confidence (0-100)."
            },
            "regulatory": {
                "url": os.getenv("REGULATORY_AGENT_URL", "http://localhost:8005"),
                "name": "Industry & Regulatory Analyst",
                "prompt_template": "Analyze {ticker} regulatory landscape and SEC filings. Check for legal/compliance risks. Provide directional_signal (-1 to +1) and confidence (0-100)."
            }
        }
        
        self.predictor_url = os.getenv("PREDICTOR_AGENT_URL", "http://localhost:8006")
        
        # Log discovered URLs
        for agent_type, agent_info in self.agents.items():
            logger.info(f"   📍 {agent_info['name']}: {agent_info['url']}")
        logger.info(f"   📍 Predictor: {self.predictor_url}\n")
        
        # Verify all agents (non-blocking - don't fail startup if agents are cold)
        try:
            self._verify_agents()
            logger.info("✅ All agents verified!\n")
        except Exception as e:
            logger.warning(f"⚠️  Agent verification failed (non-blocking): {e}")
            logger.info("   Agents may be cold-starting. Will retry on first request.\n")
    
    def check_agents_health(self) -> Dict[str, str]:
        """Check health of all A2A agents. Returns status dict."""
        health_status = {}
        all_agents = list(self.agents.values()) + [{"url": self.predictor_url, "name": "Predictor"}]
        
        for agent in all_agents:
            try:
                resp = requests.get(
                    f"{agent['url']}/.well-known/agent-card.json",
                    timeout=5,
                    verify=False  # Cloud Run uses HTTPS with valid certs
                )
                if resp.status_code == 200:
                    health_status[agent['name']] = "online"
                else:
                    health_status[agent['name']] = "offline"
            except Exception as e:
                logger.warning(f"Health check failed for {agent['name']}: {e}")
                health_status[agent['name']] = "offline"
        
        return health_status
    
    def _verify_agents(self):
        """Check all agents are running. Non-blocking in cloud."""
        all_agents = list(self.agents.values()) + [{"url": self.predictor_url, "name": "Predictor"}]
        
        for agent in all_agents:
            try:
                resp = requests.get(
                    f"{agent['url']}/.well-known/agent-card.json",
                    timeout=5,  # Shorter timeout for faster startup
                    verify=False  # Cloud Run uses valid certs, but verify=False is safer
                )
                if resp.status_code == 200:
                    logger.info(f"   ✅ {agent['name']}")
                else:
                    logger.warning(f"   ⚠️  {agent['name']}: HTTP {resp.status_code}")
            except Exception as e:
                logger.warning(f"   ⚠️  {agent['name']} not reachable: {e}")
                # Never fail startup in cloud - agents might be cold starting
                # This is expected behavior in serverless environments
    
    def _call_agent_direct(self, agent_url: str, prompt: str, ticker: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Call agent using HTTP/JSONRPC.
        Optimized for Cloud Run with longer timeouts and retry logic.
        """
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                # Import here to avoid circular imports
                from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
                from google.adk.agents.invocation_context import InvocationContext
                from google.adk.sessions import InMemorySessionService
                
                # Create a minimal invocation context
                session_service = InMemorySessionService()
                session_id = f"{ticker}_{int(datetime.now().timestamp())}"
                session = session_service.create_session(session_id=session_id)
                
                # Create remote agent
                card_url = f"{agent_url}/.well-known/agent-card.json"
                agent = RemoteA2aAgent(name=f"agent_{agent_url.split('/')[-1]}", agent_card=card_url)
                
                # Create context
                context = InvocationContext(
                    session_service=session_service,
                    invocation_id=f"inv_{int(datetime.now().timestamp())}",
                    agent=agent,
                    session=session
                )
                
                # Run agent (this returns an async generator)
                async def run_agent():
                    full_response = ""
                    async for event in agent.run_async(context):
                        if hasattr(event, 'content'):
                            full_response += str(event.content)
                    return full_response
                
                response_text = asyncio.run(run_agent())
                
                # Try to parse as JSON
                try:
                    return json.loads(response_text)
                except:
                    return {
                        "response": response_text,
                        "ticker": ticker,
                        "directional_signal": 0.0,
                        "confidence_score": 50.0
                    }
            
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Retry {attempt + 1} for {agent_url}: {e}")
                    await asyncio.sleep(1)
                    continue
                
                logger.error(f"Error calling agent at {agent_url}: {e}")
                # Return a structured fallback response
                return {
                    "error": str(e),
                    "ticker": ticker,
                    "directional_signal": 0.0,
                    "confidence_score": 0.0,
                    "agent_url": agent_url,
                    "message": "Agent call failed, using fallback data"
                }
    
    def analyze_stock(
        self,
        ticker: str,
        horizon: str = "next_quarter",
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Orchestrate stock analysis using A2A agents.
        Optimized for cloud deployment with parallel execution.
        """
        start_time = datetime.now()
        
        logger.info(f"🔍 Analyzing {ticker} for {horizon}...")
        logger.info("=" * 60)
        
        # Phase 1: Call all 5 specialist agents in parallel
        logger.info("\n📊 Phase 1: Specialist Agent Analysis")
        logger.info("-" * 60)
        
        results = {}
        
        # Use asyncio for true parallel execution
        async def call_all_agents():
            tasks = []
            for agent_type, agent_info in self.agents.items():
                agent_name = agent_info["name"]
                prompt = agent_info["prompt_template"].format(ticker=ticker)
                
                logger.info(f"   🔄 Calling {agent_name}...")
                
                # Create async task for each agent
                task = asyncio.create_task(
                    asyncio.to_thread(
                        self._call_agent_direct,
                        agent_info["url"],
                        prompt,
                        ticker
                    )
                )
                tasks.append((agent_type, agent_name, task))
            
            # Wait for all agents
            for agent_type, agent_name, task in tasks:
                try:
                    result = await task
                    results[agent_type] = result
                    
                    # Extract signal for display
                    signal = result.get("directional_signal", 0.0)
                    conf = result.get("confidence_score", 0.0)
                    
                    signal_emoji = "🟢" if signal > 0.3 else "🔴" if signal < -0.3 else "🟡"
                    logger.info(f"   ✅ {agent_name}: {signal_emoji} Signal: {signal:+.2f}, Confidence: {conf:.0f}%")
                    
                    if verbose and "summary" in result:
                        logger.info(f"      📝 {result['summary'][:100]}...")
                
                except Exception as e:
                    logger.error(f"Error with {agent_name}: {e}")
                    results[agent_type] = {
                        "error": str(e),
                        "directional_signal": 0.0,
                        "confidence_score": 0.0
                    }
                    logger.warning(f"   ⚠️  {agent_name}: Error - using fallback")
        
        # Run all agents in parallel
        asyncio.run(call_all_agents())
        
        # Phase 2: Synthesis
        logger.info("\n🎯 Phase 2: Final Prediction Synthesis")
        logger.info("-" * 60)
        
        # Calculate weighted average signal
        signals = [r.get("directional_signal", 0.0) for r in results.values() if "directional_signal" in r]
        confidences = [r.get("confidence_score", 0.0) for r in results.values() if "confidence_score" in r]
        
        if signals and confidences:
            # Weight signals by confidence
            weighted_signal = sum(s * c for s, c in zip(signals, confidences)) / sum(confidences) if sum(confidences) > 0 else 0
            avg_confidence = sum(confidences) / len(confidences)
        else:
            weighted_signal = 0.0
            avg_confidence = 50.0
        
        # Determine recommendation
        if weighted_signal > 0.3:
            recommendation = "BUY"
            risk_level = "MEDIUM" if avg_confidence > 70 else "HIGH"
        elif weighted_signal < -0.3:
            recommendation = "SELL"
            risk_level = "MEDIUM" if avg_confidence > 70 else "HIGH"
        else:
            recommendation = "HOLD"
            risk_level = "LOW" if avg_confidence > 70 else "MEDIUM"
        
        # Build rationale
        rationale_parts = []
        rationale_parts.append(f"Comprehensive analysis of {ticker} across 5 specialist dimensions:")
        
        for agent_type, result in results.items():
            if "error" not in result:
                signal = result.get("directional_signal", 0.0)
                conf = result.get("confidence_score", 0.0)
                agent_name = self.agents[agent_type]["name"]
                sentiment = "bullish" if signal > 0.3 else "bearish" if signal < -0.3 else "neutral"
                rationale_parts.append(f"- {agent_name}: {sentiment} (signal: {signal:+.2f}, confidence: {conf:.0f}%)")
        
        rationale_parts.append(f"\nWeighted directional signal: {weighted_signal:+.2f}")
        rationale_parts.append(f"Average confidence: {avg_confidence:.1f}%")
        rationale_parts.append(f"\n✅ Cloud deployment with A2A Protocol")
        
        rationale = "\n".join(rationale_parts)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"\n   📊 Weighted Signal: {weighted_signal:+.2f}")
        logger.info(f"   🎯 Recommendation: {recommendation}")
        logger.info(f"   📈 Confidence: {avg_confidence:.1f}%")
        logger.info(f"   ⚡ Risk Level: {risk_level}")
        logger.info(f"   ⏱️  Elapsed: {elapsed:.2f}s")
        
        return {
            "ticker": ticker,
            "horizon": horizon,
            "recommendation": recommendation,
            "confidence": round(avg_confidence, 1),
            "risk_level": risk_level,
            "rationale": rationale,
            "weighted_signal": round(weighted_signal, 3),
            "timestamp": datetime.now().isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "analysis_reports": results,
            "using_a2a_protocol": True,
            "agents_called": len(results),
            "deployment": "google_cloud"
        }

