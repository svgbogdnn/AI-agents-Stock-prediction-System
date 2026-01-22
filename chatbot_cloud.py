#!/usr/bin/env python3
"""
Cloud-Ready Chatbot with Function Calling
Deployed on Google Cloud Run with external agent discovery
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ADK imports for A2A agent calls
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService

load_dotenv()

app = FastAPI(
    title="Stock Analysis Chatbot - Cloud Function Calling",
    description="Gemini API function calling with A2A agents on Google Cloud",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Internal agent URLs (from Cloud Run env vars or defaults)
INTERNAL_AGENTS = {
    "fundamental": os.getenv("FUNDAMENTAL_AGENT_URL", "http://localhost:8001"),
    "technical": os.getenv("TECHNICAL_AGENT_URL", "http://localhost:8002"),
    "sentiment": os.getenv("SENTIMENT_AGENT_URL", "http://localhost:8003"),
    "macro": os.getenv("MACRO_AGENT_URL", "http://localhost:8004"),
    "regulatory": os.getenv("REGULATORY_AGENT_URL", "http://localhost:8005"),
    "predictor": os.getenv("PREDICTOR_AGENT_URL", "http://localhost:8006"),
}

# External agent registry (can be populated from agent marketplace/discovery service)
EXTERNAL_AGENTS = {}

# Agent Registry URL (for discovering external agents)
AGENT_REGISTRY_URL = os.getenv("AGENT_REGISTRY_URL", "http://localhost:9000")


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    function_calls: List[Dict[str, Any]]
    session_id: str


def discover_external_agents():
    """Discover external agents from registry."""
    global EXTERNAL_AGENTS
    try:
        response = requests.get(f"{AGENT_REGISTRY_URL}/agents", timeout=5)
        if response.status_code == 200:
            registry_agents = response.json()
            for agent in registry_agents.get("agents", []):
                agent_id = agent.get("id")
                agent_card_url = agent.get("agent_card_url")
                if agent_id and agent_card_url:
                    EXTERNAL_AGENTS[agent_id] = {
                        "name": agent.get("name", agent_id),
                        "description": agent.get("description", ""),
                        "agent_card_url": agent_card_url,
                        "category": agent.get("category", "general")
                    }
            print(f"✅ Discovered {len(EXTERNAL_AGENTS)} external agents")
    except Exception as e:
        print(f"⚠️  Could not connect to agent registry: {e}")


def call_a2a_agent(agent_url: str, ticker: str, query: str = None) -> str:
    """Call an A2A agent via HTTP/JSONRPC (more reliable than native A2A for now)."""
    try:
        prompt = query or f"Analyze {ticker} from your specialized perspective. Provide a directional_signal (-1 to +1) and confidence_score (0-100)."
        
        # Use HTTP/JSONRPC directly (more reliable than RemoteA2aAgent for message passing)
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "method": "agent/invoke",
            "params": {
                "message": prompt,
                "session_id": f"session_{int(datetime.now().timestamp())}"
            },
            "id": int(datetime.now().timestamp() * 1000)
        }
        
        response = requests.post(
            agent_url,
            json=jsonrpc_request,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                return result["result"].get("response", json.dumps(result["result"]))
            elif "error" in result:
                return json.dumps({"error": result["error"].get("message", "Unknown error")})
            return json.dumps(result)
        else:
            return json.dumps({"error": f"HTTP {response.status_code}: {response.text[:200]}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def call_external_agent(agent_id: str, prompt: str) -> str:
    """Call an external A2A agent via HTTP/JSONRPC."""
    if agent_id not in EXTERNAL_AGENTS:
        return json.dumps({"error": f"Agent {agent_id} not found"})
    
    agent_info = EXTERNAL_AGENTS[agent_id]
    # Extract base URL from agent card URL
    card_url = agent_info["agent_card_url"]
    agent_url = card_url.replace("/.well-known/agent-card.json", "")
    
    try:
        # Use HTTP/JSONRPC directly
        jsonrpc_request = {
            "jsonrpc": "2.0",
            "method": "agent/invoke",
            "params": {
                "message": prompt,
                "session_id": f"ext_{int(datetime.now().timestamp())}"
            },
            "id": int(datetime.now().timestamp() * 1000)
        }
        
        response = requests.post(
            agent_url,
            json=jsonrpc_request,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result:
                return result["result"].get("response", json.dumps(result["result"]))
            elif "error" in result:
                return json.dumps({"error": result["error"].get("message", "Unknown error")})
            return json.dumps(result)
        else:
            return json.dumps({"error": f"HTTP {response.status_code}: {response.text[:200]}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_function_declarations():
    """Get function declarations including external agents."""
    functions = [
        {
            "name": "analyze_fundamentals",
            "description": "Analyze company fundamentals including financial metrics, valuation ratios.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"},
                    "query": {"type": "string", "description": "Optional specific question"}
                },
                "required": ["ticker"]
            }
        },
        {
            "name": "analyze_technical",
            "description": "Perform technical analysis including price trends, RSI, MACD.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"},
                    "query": {"type": "string", "description": "Optional specific question"}
                },
                "required": ["ticker"]
            }
        },
        {
            "name": "analyze_sentiment",
            "description": "Analyze news sentiment and key events affecting the stock.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"},
                    "query": {"type": "string", "description": "Optional specific question"}
                },
                "required": ["ticker"]
            }
        },
        {
            "name": "analyze_macro",
            "description": "Analyze macroeconomic conditions including GDP, inflation, Fed rates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"},
                    "query": {"type": "string", "description": "Optional specific question"}
                },
                "required": ["ticker"]
            }
        },
        {
            "name": "analyze_regulatory",
            "description": "Check regulatory risks, SEC filings, compliance issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"},
                    "query": {"type": "string", "description": "Optional specific question"}
                },
                "required": ["ticker"]
            }
        },
        {
            "name": "get_full_analysis",
            "description": "Get complete stock analysis using all specialist agents.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"]
            }
        }
    ]
    
    # Add external agent functions
    for agent_id, agent_info in EXTERNAL_AGENTS.items():
        functions.append({
            "name": f"call_external_{agent_id}",
            "description": f"{agent_info['description']} - External agent: {agent_info['name']}",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Query for the external agent"}
                },
                "required": ["prompt"]
            }
        })
    
    return functions


FUNCTION_IMPLEMENTATIONS = {
    "analyze_fundamentals": lambda args: call_a2a_agent(INTERNAL_AGENTS["fundamental"], args["ticker"], args.get("query")),
    "analyze_technical": lambda args: call_a2a_agent(INTERNAL_AGENTS["technical"], args["ticker"], args.get("query")),
    "analyze_sentiment": lambda args: call_a2a_agent(INTERNAL_AGENTS["sentiment"], args["ticker"], args.get("query")),
    "analyze_macro": lambda args: call_a2a_agent(INTERNAL_AGENTS["macro"], args["ticker"], args.get("query")),
    "analyze_regulatory": lambda args: call_a2a_agent(INTERNAL_AGENTS["regulatory"], args["ticker"], args.get("query")),
    "get_full_analysis": lambda args: get_full_analysis(args["ticker"])
}


def get_full_analysis(ticker: str) -> str:
    """Get comprehensive analysis from all agents."""
    results = {}
    for agent_type in ["fundamental", "technical", "sentiment", "macro", "regulatory"]:
        try:
            result = call_a2a_agent(INTERNAL_AGENTS[agent_type], ticker)
            results[agent_type] = result
        except Exception as e:
            results[agent_type] = {"error": str(e)}
    return json.dumps(results, indent=2)


def setup_external_agent_functions():
    """Setup function implementations for external agents."""
    for agent_id in EXTERNAL_AGENTS.keys():
        def make_impl(aid):
            return lambda args: call_external_agent(aid, args["prompt"])
        FUNCTION_IMPLEMENTATIONS[f"call_external_{agent_id}"] = make_impl(agent_id)


def chat_with_function_calling(user_message: str) -> tuple[str, List[Dict]]:
    """Chat with Gemini using function calling."""
    functions = get_function_declarations()
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GOOGLE_API_KEY}"
    
    function_calls_made = []
    contents = [{"role": "user", "parts": [{"text": user_message}]}]
    max_iterations = 5
    
    for iteration in range(max_iterations):
        payload = {
            "contents": contents,
            "tools": [{"function_declarations": functions}],
            "system_instruction": "You are a helpful stock analysis assistant. Use internal agents for stock analysis. Use external agents for additional intelligence when appropriate."
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        if "candidates" not in result or not result["candidates"]:
            break
        
        candidate = result["candidates"][0]
        if "content" not in candidate or "parts" not in candidate["content"]:
            break
        
        parts = candidate["content"]["parts"]
        function_call = None
        
        for part in parts:
            if "functionCall" in part:
                function_call = part["functionCall"]
                break
        
        if not function_call:
            break
        
        function_name = function_call.get("name", "")
        function_args = function_call.get("args", {})
        
        function_calls_made.append({"name": function_name, "args": function_args})
        
        # Execute function
        if function_name in FUNCTION_IMPLEMENTATIONS:
            function_result = FUNCTION_IMPLEMENTATIONS[function_name](function_args)
        else:
            function_result = json.dumps({"error": f"Unknown function: {function_name}"})
        
        contents.append({"role": "model", "parts": [{"functionCall": function_call}]})
        contents.append({
            "role": "function",
            "parts": [{"functionResponse": {"name": function_name, "response": function_result}}]
        })
    
    # Get final response
    if function_calls_made:
        payload = {"contents": contents}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
    
    if "candidates" in result and result["candidates"]:
        parts = result["candidates"][0]["content"]["parts"]
        response_text = "".join([part.get("text", "") for part in parts])
    else:
        response_text = f"I analyzed your request and called {len(function_calls_made)} function(s)."
    
    return response_text, function_calls_made


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serves chat UI."""
    # Try multiple paths for the HTML file
    possible_paths = [
        os.path.join(os.path.dirname(__file__), "chatbot_ui.html"),
        "chatbot_ui.html",
        "/app/chatbot_ui.html",
        os.path.join(os.getcwd(), "chatbot_ui.html")
    ]
    
    for html_path in possible_paths:
        if os.path.exists(html_path):
            return FileResponse(html_path, media_type="text/html")
    
    # If file not found, return inline HTML
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis Chatbot - Function Calling Demo</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%;
            max-width: 800px;
            height: 90vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .header p { opacity: 0.9; font-size: 14px; }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user { justify-content: flex-end; }
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .message.user .message-content {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }
        .message.assistant .message-content {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        .function-calls {
            margin-top: 8px;
            padding: 8px;
            background: #f0f0f0;
            border-radius: 8px;
            font-size: 12px;
            font-family: 'Courier New', monospace;
        }
        .function-calls summary {
            cursor: pointer;
            color: #667eea;
            font-weight: bold;
        }
        .input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s;
        }
        .input-area input:focus { border-color: #667eea; }
        .input-area button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .input-area button:hover { transform: translateY(-2px); }
        .input-area button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .status {
            text-align: center;
            padding: 10px;
            font-size: 12px;
            color: #666;
            background: #f8f9fa;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Stock Analysis Chatbot</h1>
            <p>Function Calling Demo - Gemini API + A2A Agents</p>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="message assistant">
                <div class="message-content">
                    👋 Hello! I'm your stock analysis assistant powered by Google Gemini with function calling.
                    <br><br>
                    I can help you analyze stocks using specialized AI agents:
                    <ul style="margin-top: 10px; padding-left: 20px;">
                        <li>📊 Fundamental Analysis</li>
                        <li>📈 Technical Analysis</li>
                        <li>📰 Sentiment Analysis</li>
                        <li>🌍 Macro Economic Analysis</li>
                        <li>⚖️ Regulatory Analysis</li>
                    </ul>
                    <br>
                    Try asking: "Analyze AAPL fundamentals" or "Get full analysis of MSFT"
                </div>
            </div>
        </div>
        <div class="status" id="status">Ready</div>
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="Ask about a stock (e.g., 'Analyze AAPL fundamentals')..." onkeypress="if(event.key === 'Enter') sendMessage()">
            <button id="sendButton" onclick="sendMessage()">Send</button>
        </div>
    </div>
    <script>
        const API_URL = window.location.origin;
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const status = document.getElementById('status');
        function addMessage(text, isUser, functionCalls = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'assistant'}`;
            let content = `<div class="message-content">${text.replace(/\\n/g, '<br>')}</div>`;
            if (functionCalls && functionCalls.length > 0) {
                content += `<div class="function-calls"><details><summary>🔧 ${functionCalls.length} Function Call(s) Made</summary><pre>${JSON.stringify(functionCalls, null, 2)}</pre></details></div>`;
            }
            messageDiv.innerHTML = content;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;
            addMessage(message, true);
            messageInput.value = '';
            sendButton.disabled = true;
            sendButton.innerHTML = '<div class="loading"></div>';
            status.textContent = 'Thinking and calling functions...';
            try {
                const response = await fetch(`${API_URL}/chat`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ message })
                });
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                const data = await response.json();
                addMessage(data.response, false, data.function_calls);
                status.textContent = `Ready • ${data.function_calls?.length || 0} function call(s) executed`;
            } catch (error) {
                addMessage(`❌ Error: ${error.message}`, false);
                status.textContent = 'Error occurred';
            } finally {
                sendButton.disabled = false;
                sendButton.innerHTML = 'Send';
            }
        }
        fetch(`${API_URL}/health`).then(res => res.json()).then(data => {
            status.textContent = `Ready • ${data.external_agents || 0} external agents available`;
        }).catch(err => {
            status.textContent = 'Service check failed';
        });
    </script>
</body>
</html>
    """)


@app.get("/api/info")
async def api_info():
    """API info endpoint."""
    return {
        "service": "Stock Analysis Chatbot - Function Calling Demo",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chat": "/chat (POST)",
            "external_agents": "/agents/external",
            "discover_agents": "/agents/discover (POST)",
            "docs": "/docs"
        },
        "external_agents_count": len(EXTERNAL_AGENTS)
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "healthy", "external_agents": len(EXTERNAL_AGENTS)}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint with function calling."""
    try:
        response_text, function_calls = chat_with_function_calling(request.message)
        session_id = request.session_id or f"session_{int(datetime.now().timestamp())}"
        return ChatResponse(
            response=response_text,
            function_calls=function_calls,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents/external")
async def list_external_agents():
    """List discovered external agents."""
    return {"agents": list(EXTERNAL_AGENTS.values())}


@app.post("/agents/discover")
async def discover_agents():
    """Trigger agent discovery."""
    discover_external_agents()
    return {"status": "discovered", "count": len(EXTERNAL_AGENTS)}


# Discover agents on startup
@app.on_event("startup")
async def startup():
    """Discover external agents on startup."""
    discover_external_agents()
    setup_external_agent_functions()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

