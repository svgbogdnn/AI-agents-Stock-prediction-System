#!/usr/bin/env python3
"""
A2A Agent Registry Service
Discovers and catalogs A2A agents for subscription
"""

import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import requests
from datetime import datetime

app = FastAPI(
    title="A2A Agent Registry",
    description="Registry for discovering and subscribing to A2A agents",
    version="1.0.0"
)

# In-memory registry (in production, use Cloud Firestore or Cloud SQL)
AGENT_REGISTRY = {}


class AgentRegistration(BaseModel):
    id: str
    name: str
    description: str
    agent_card_url: str
    category: str = "general"
    provider: Optional[str] = None
    tags: List[str] = []
    metadata: Optional[Dict[str, Any]] = None


class AgentDiscovery(BaseModel):
    agent_card_url: str
    category: Optional[str] = None


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "A2A Agent Registry",
        "version": "1.0.0",
        "agents_count": len(AGENT_REGISTRY)
    }


@app.post("/agents/register")
async def register_agent(agent: AgentRegistration):
    """Register a new agent in the registry."""
    # Verify agent card exists
    try:
        response = requests.get(agent.agent_card_url, timeout=5)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Agent card not accessible")
        
        agent_card = response.json()
        # Validate it's a proper A2A agent card
        if "name" not in agent_card or "skills" not in agent_card:
            raise HTTPException(status_code=400, detail="Invalid agent card format")
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Cannot access agent card: {str(e)}")
    
    # Store agent
    AGENT_REGISTRY[agent.id] = {
        **agent.dict(),
        "registered_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    return {"status": "registered", "agent_id": agent.id}


@app.get("/agents")
async def list_agents(category: Optional[str] = None):
    """List all registered agents, optionally filtered by category."""
    agents = list(AGENT_REGISTRY.values())
    
    if category:
        agents = [a for a in agents if a.get("category") == category]
    
    return {"agents": agents, "count": len(agents)}


@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get details for a specific agent."""
    if agent_id not in AGENT_REGISTRY:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return AGENT_REGISTRY[agent_id]


@app.post("/agents/discover")
async def discover_agent(discovery: AgentDiscovery):
    """Discover an agent by its agent card URL."""
    try:
        response = requests.get(discovery.agent_card_url, timeout=5)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Agent card not accessible")
        
        agent_card = response.json()
        
        # Extract agent info from card
        agent_info = {
            "id": agent_card.get("name", discovery.agent_card_url.split("/")[-2]),
            "name": agent_card.get("name", "Unknown Agent"),
            "description": agent_card.get("description", ""),
            "agent_card_url": discovery.agent_card_url,
            "category": discovery.category or "general",
            "skills": agent_card.get("skills", []),
            "discovered_at": datetime.now().isoformat(),
            "status": "discovered"
        }
        
        # Auto-register if valid
        agent_id = agent_info["id"]
        AGENT_REGISTRY[agent_id] = agent_info
        
        return {"status": "discovered", "agent": agent_info}
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Cannot discover agent: {str(e)}")


@app.delete("/agents/{agent_id}")
async def unregister_agent(agent_id: str):
    """Unregister an agent."""
    if agent_id not in AGENT_REGISTRY:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    del AGENT_REGISTRY[agent_id]
    return {"status": "unregistered", "agent_id": agent_id}


@app.get("/agents/search")
async def search_agents(query: str, category: Optional[str] = None):
    """Search agents by name, description, or tags."""
    results = []
    
    for agent_id, agent in AGENT_REGISTRY.items():
        if category and agent.get("category") != category:
            continue
        
        # Simple text search
        search_text = f"{agent.get('name', '')} {agent.get('description', '')} {' '.join(agent.get('tags', []))}".lower()
        if query.lower() in search_text:
            results.append(agent)
    
    return {"agents": results, "count": len(results)}


# Example: Pre-populate with some known agent marketplaces
@app.on_event("startup")
async def startup():
    """Initialize registry with example agents."""
    # Example: Register a hypothetical external intelligence agent
    # In production, this would come from agent marketplaces or discovery services
    
    example_agents = [
        {
            "id": "market-intelligence-agent",
            "name": "Market Intelligence Agent",
            "description": "Provides advanced market insights and trend analysis using external data sources",
            "agent_card_url": os.getenv("MARKET_INTELLIGENCE_AGENT_URL", "https://example.com/agents/market-intelligence/.well-known/agent-card.json"),
            "category": "intelligence",
            "provider": "external",
            "tags": ["market", "intelligence", "trends"]
        },
        {
            "id": "risk-assessment-agent",
            "name": "Risk Assessment Agent",
            "description": "Advanced risk modeling and portfolio risk analysis",
            "agent_card_url": os.getenv("RISK_AGENT_URL", "https://example.com/agents/risk/.well-known/agent-card.json"),
            "category": "risk",
            "provider": "external",
            "tags": ["risk", "portfolio", "assessment"]
        }
    ]
    
    for agent_data in example_agents:
        if agent_data["agent_card_url"].startswith("https://"):
            # Only register if URL is provided (not default example.com)
            try:
                response = requests.get(agent_data["agent_card_url"], timeout=2)
                if response.status_code == 200:
                    AGENT_REGISTRY[agent_data["id"]] = {
                        **agent_data,
                        "registered_at": datetime.now().isoformat(),
                        "status": "active"
                    }
            except:
                pass  # Skip if not accessible


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 9000))
    uvicorn.run(app, host="0.0.0.0", port=port)

