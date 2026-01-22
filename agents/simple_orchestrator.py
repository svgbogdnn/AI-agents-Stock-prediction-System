"""
Simple Strategist - Direct HTTP calls to A2A agents
Simpler approach that uses direct HTTP requests instead of complex ADK RemoteA2aAgent
"""

import requests
import json
import asyncio
from typing import Dict, Any
from datetime import datetime

class SimpleStrategistOrchestrator:
    """
    Simplified orchestrator that calls A2A agents via direct HTTP.
    Much simpler than dealing with async generators and contexts.
    """
    
    def __init__(self):
        """Initialize with agent URLs."""
        print("🎯 Initializing Simple Strategist Orchestrator...")
        
        self.agents = {
            "fundamental": "http://localhost:8001",
            "technical": "http://localhost:8002",
            "sentiment": "http://localhost:8003",
            "macro": "http://localhost:8004",
            "regulatory": "http://localhost:8005",
            "predictor": "http://localhost:8006"
        }
        
        # Verify all agents are accessible
        for name, url in self.agents.items():
            try:
                response = requests.get(f"{url}/.well-known/agent-card.json", timeout=2)
                if response.status_code == 200:
                    print(f"   ✅ Connected to {name}")
                else:
                    print(f"   ❌ {name} returned HTTP {response.status_code}")
            except Exception as e:
                print(f"   ❌ {name} not reachable: {e}")
                raise RuntimeError(f"Agent {name} not running. Start with: bash scripts/start_all_agents.sh")
        
        print("✅ All agents connected!\n")
    
    def _call_agent_simple(self, agent_url: str, prompt: str) -> Dict[str, Any]:
        """
        Call an A2A agent via simple HTTP POST.
        This is a simplified version that directly posts to the agent.
        """
        try:
            # For now, return mock data since A2A protocol is complex
            # In production, we'd implement full A2A protocol
            return {
                "agent": agent_url,
                "prompt": prompt[:100],
                "response": f"Mock response from {agent_url}",
                "directional_signal": 0.5,
                "confidence_score": 75.0
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def analyze_stock_async(
        self,
        ticker: str,
        horizon: str = "next_quarter",
        verbose: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze a stock by orchestrating all specialist agents.
        """
        print(f"🔍 Analyzing {ticker} for {horizon}...")
        print("=" * 60)
        
        # Phase 1: Call all analysis agents in parallel
        print("\n📊 Phase 1: Parallel Analysis by Specialist Agents")
        print("-" * 60)
        
        tasks = []
        for agent_type in ["fundamental", "technical", "sentiment", "macro", "regulatory"]:
            prompt = f"Analyze {ticker} from a {agent_type} perspective for {horizon}"
            task = asyncio.to_thread(self._call_agent_simple, self.agents[agent_type], prompt)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        fundamental_report, technical_report, sentiment_report, macro_report, regulatory_report = results
        
        for report in results:
            print(f"   ✅ {report.get('agent', 'agent')} analysis complete")
        
        # Phase 2: Synthesize with predictor
        print("\n🎯 Phase 2: Synthesis & Prediction")
        print("-" * 60)
        
        prediction_prompt = f"""
        Synthesize these 5 specialist reports for {ticker}:
        - Fundamental: {json.dumps(fundamental_report)}
        - Technical: {json.dumps(technical_report)}
        - Sentiment: {json.dumps(sentiment_report)}
        - Macro: {json.dumps(macro_report)}
        - Regulatory: {json.dumps(regulatory_report)}
        """
        
        prediction = self._call_agent_simple(self.agents["predictor"], prediction_prompt)
        
        # Generate final prediction
        final_prediction = {
            "ticker": ticker,
            "horizon": horizon,
            "recommendation": "HOLD",  # Mock for now
            "confidence": 70.0,
            "risk_level": "MEDIUM",
            "rationale": f"Based on analysis of 5 specialist agents for {ticker}. "
                        f"System is in demo mode - full A2A protocol integration coming soon.",
            "timestamp": datetime.now().isoformat(),
            "analysis_reports": {
                "fundamental": fundamental_report,
                "technical": technical_report,
                "sentiment": sentiment_report,
                "macro": macro_report,
                "regulatory": regulatory_report
            }
        }
        
        return final_prediction
    
    def analyze_stock(self, ticker: str, horizon: str = "next_quarter", verbose: bool = False) -> Dict[str, Any]:
        """Synchronous wrapper for async analyze_stock."""
        return asyncio.run(self.analyze_stock_async(ticker, horizon, verbose))

