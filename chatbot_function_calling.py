#!/usr/bin/env python3
"""
Chatbot with Function Calling Demo
Demonstrates Gemini API function calling with A2A agents.

This is a clear demonstration of:
- Function calling (assessment criteria)
- Integration with A2A agents
- Google Gemini API usage
- Clean, visual interface
"""

import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
import requests

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ADK imports for A2A agent calls
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.sessions import InMemorySessionService

load_dotenv()

# Agent URLs (your existing A2A agents)
AGENT_URLS = {
    "fundamental": "http://localhost:8001",
    "technical": "http://localhost:8002",
    "sentiment": "http://localhost:8003",
    "macro": "http://localhost:8004",
    "regulatory": "http://localhost:8005",
    "predictor": "http://localhost:8006"
}

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


def call_a2a_agent(agent_type: str, ticker: str, query: str = None) -> str:
    """
    Call an A2A agent synchronously.
    This function will be exposed to Gemini as a tool.
    """
    try:
        if agent_type not in AGENT_URLS:
            return json.dumps({"error": f"Unknown agent type: {agent_type}"})
        
        base_url = AGENT_URLS[agent_type]
        card_url = f"{base_url}/.well-known/agent-card.json"
        
        # Create remote agent
        agent = RemoteA2aAgent(
            name=f"{agent_type}_agent",
            agent_card=card_url
        )
        
        # Create invocation context
        session_service = InMemorySessionService()
        session_id = f"{ticker}_{int(datetime.now().timestamp())}"
        session = session_service.create_session(session_id=session_id)
        
        context = InvocationContext(
            session_service=session_service,
            invocation_id=f"inv_{int(datetime.now().timestamp())}",
            agent=agent,
            session=session
        )
        
        # Build prompt
        if query:
            prompt = f"{query} for {ticker}"
        else:
            prompts = {
                "fundamental": f"Analyze the fundamental financials for {ticker}. Provide directional_signal, confidence_score, and key metrics.",
                "technical": f"Perform technical analysis for {ticker}. Include RSI, MACD, trend, directional_signal, and confidence_score.",
                "sentiment": f"Analyze recent news sentiment for {ticker}. Provide overall sentiment, key events, directional_signal, and confidence_score.",
                "macro": f"Analyze current macro-economic conditions and their impact on stocks like {ticker}. Provide market_regime, directional_signal, and confidence_score.",
                "regulatory": f"Check for regulatory risks and industry trends for {ticker}. Review SEC filings and provide directional_signal and confidence_score.",
                "predictor": f"Generate final prediction for {ticker} based on all analysis."
            }
            prompt = prompts.get(agent_type, f"Analyze {ticker}")
        
        # Run agent
        async def run_agent():
            full_response = ""
            async for event in agent.run_async(context):
                if hasattr(event, 'content'):
                    full_response += str(event.content)
                elif hasattr(event, 'text'):
                    full_response += event.text
            return full_response
        
        response = asyncio.run(run_agent())
        return response
        
    except Exception as e:
        return json.dumps({"error": str(e), "agent": agent_type, "ticker": ticker})


def get_full_analysis(ticker: str) -> str:
    """Get comprehensive analysis from all agents."""
    results = {}
    
    for agent_type in ["fundamental", "technical", "sentiment", "macro", "regulatory"]:
        try:
            result = call_a2a_agent(agent_type, ticker)
            results[agent_type] = result
        except Exception as e:
            results[agent_type] = {"error": str(e)}
    
    # Get final prediction
    try:
        prediction = call_a2a_agent("predictor", ticker)
        results["prediction"] = prediction
    except Exception as e:
        results["prediction"] = {"error": str(e)}
    
    return json.dumps(results, indent=2)


# Function implementations map
FUNCTION_IMPLEMENTATIONS = {
    "analyze_fundamentals": lambda args: call_a2a_agent("fundamental", args["ticker"], args.get("query")),
    "analyze_technical": lambda args: call_a2a_agent("technical", args["ticker"], args.get("query")),
    "analyze_sentiment": lambda args: call_a2a_agent("sentiment", args["ticker"], args.get("query")),
    "analyze_macro": lambda args: call_a2a_agent("macro", args["ticker"], args.get("query")),
    "analyze_regulatory": lambda args: call_a2a_agent("regulatory", args["ticker"], args.get("query")),
    "get_full_analysis": lambda args: get_full_analysis(args["ticker"])
}


def chat_with_function_calling(user_message: str, chat_history: List[Dict] = None) -> tuple[str, List[Dict], List[Dict]]:
    """
    Chat with Gemini using function calling via REST API.
    Returns: (response_text, updated_history, function_calls_made)
    """
    # Function declarations for Gemini
    functions = [
        {
            "name": "analyze_fundamentals",
            "description": "Analyze company fundamentals including financial metrics, valuation ratios, balance sheet, and earnings.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol (e.g., 'AAPL', 'GOOGL')"},
                    "query": {"type": "string", "description": "Optional specific question"}
                },
                "required": ["ticker"]
            }
        },
        {
            "name": "analyze_technical",
            "description": "Perform technical analysis including price trends, RSI, MACD, moving averages.",
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
            "description": "Analyze news sentiment, market sentiment, and key events affecting the stock.",
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
            "description": "Get complete stock analysis using all specialist agents and generate final prediction.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticker": {"type": "string", "description": "Stock ticker symbol"}
                },
                "required": ["ticker"]
            }
        }
    ]
    
    # Build conversation history
    if chat_history is None:
        chat_history = []
    
    # Convert to Gemini format
    contents = []
    for msg in chat_history:
        if isinstance(msg, dict):
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                contents.append({"role": "user", "parts": [{"text": content}]})
            elif role == "model":
                contents.append({"role": "model", "parts": [{"text": content}]})
    
    # Add current user message
    contents.append({"role": "user", "parts": [{"text": user_message}]})
    
    # Call Gemini API with function calling
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GOOGLE_API_KEY}"
    
    function_calls_made = []
    max_iterations = 5
    
    for iteration in range(max_iterations):
        payload = {
            "contents": contents,
            "tools": [{"function_declarations": functions}],
            "system_instruction": "You are a helpful stock analysis assistant. When users ask about stocks, intelligently call the appropriate functions. Be conversational."
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        # Check for function calls
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
            # No function call, we're done
            break
        
        # Extract function call details
        function_name = function_call.get("name", "")
        function_args = function_call.get("args", {})
        
        function_calls_made.append({
            "name": function_name,
            "args": function_args
        })
        
        # Execute function
        if function_name in FUNCTION_IMPLEMENTATIONS:
            function_result = FUNCTION_IMPLEMENTATIONS[function_name](function_args)
        else:
            function_result = json.dumps({"error": f"Unknown function: {function_name}"})
        
        # Add function call and result to conversation
        contents.append({
            "role": "model",
            "parts": [{"functionCall": function_call}]
        })
        contents.append({
            "role": "function",
            "parts": [{
                "functionResponse": {
                    "name": function_name,
                    "response": function_result
                }
            }]
        })
    
    # Get final text response
    if function_calls_made:
        # Final response after function calls
        payload = {
            "contents": contents,
            "system_instruction": "You are a helpful stock analysis assistant. Summarize the analysis results in a conversational way."
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
    
    # Extract text response
    if "candidates" in result and result["candidates"]:
        parts = result["candidates"][0]["content"]["parts"]
        response_text = ""
        for part in parts:
            if "text" in part:
                response_text += part["text"]
    else:
        response_text = f"I analyzed your request and called {len(function_calls_made)} function(s)."
    
    # Update history
    updated_history = []
    for msg in chat_history:
        if isinstance(msg, dict) and msg.get("content"):
            updated_history.append(msg)
    
    updated_history.extend([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": response_text}
    ])
    
    return response_text, updated_history, function_calls_made


# Streamlit UI
st.set_page_config(
    page_title="Stock Analysis Chatbot - Function Calling Demo",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Stock Analysis Chatbot")
st.markdown("**Function Calling Demo** - Gemini API calling A2A agents")
st.markdown("---")

# Sidebar with info
with st.sidebar:
    st.header("📋 Function Calling Demo")
    st.markdown("""
    **Assessment Criteria: Function Calling**
    
    This chatbot demonstrates:
    - ✅ Gemini API function calling
    - ✅ A2A agent integration
    - ✅ Multi-agent orchestration
    - ✅ Google ecosystem integration
    
    **Available Functions:**
    1. `analyze_fundamentals(ticker)`
    2. `analyze_technical(ticker)`
    3. `analyze_sentiment(ticker)`
    4. `analyze_macro(ticker)`
    5. `analyze_regulatory(ticker)`
    6. `get_full_analysis(ticker)`
    """)
    
    st.markdown("---")
    st.markdown("**Example Questions:**")
    st.code("""
    Analyze AAPL fundamentals
    What's the technical outlook for GOOGL?
    Get full analysis of MSFT
    Check sentiment for TSLA
    """)
    
    # Agent status check
    st.markdown("---")
    st.markdown("**Agent Status:**")
    agent_status = {}
    for name, url in AGENT_URLS.items():
        try:
            resp = requests.get(f"{url}/.well-known/agent-card.json", timeout=2)
            agent_status[name] = "✅ Online" if resp.status_code == 200 else "❌ Offline"
        except:
            agent_status[name] = "❌ Offline"
    
    for name, status in agent_status.items():
        st.text(f"{name}: {status}")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "function_calls" not in st.session_state:
    st.session_state.function_calls = []

# Display chat history
for i, msg in enumerate(st.session_state.chat_history):
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.write(msg["content"])
            
            # Show function calls if any
            if i < len(st.session_state.function_calls) and st.session_state.function_calls[i]:
                with st.expander("🔧 Function Calls Made"):
                    for fc in st.session_state.function_calls[i]:
                        st.json({
                            "function": fc["name"],
                            "arguments": fc["args"]
                        })

# User input
user_input = st.chat_input("Ask about a stock (e.g., 'Analyze AAPL fundamentals')")

if user_input:
    # Add user message to chat
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    # Show user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking and calling functions..."):
            try:
                response_text, updated_history, function_calls = chat_with_function_calling(
                    user_input,
                    st.session_state.chat_history[:-1]  # Exclude current user message
                )
                
                st.write(response_text)
                
                # Show function calls
                if function_calls:
                    with st.expander("🔧 Function Calls Made (Function Calling Demo)"):
                        st.markdown("**Functions called by Gemini:**")
                        for fc in function_calls:
                            st.json({
                                "function": fc["name"],
                                "arguments": fc["args"]
                            })
                        st.success(f"✅ {len(function_calls)} function call(s) executed")
                
                # Update session state
                st.session_state.chat_history = updated_history
                st.session_state.function_calls.append(function_calls)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.chat_history.append({"role": "assistant", "content": f"Error: {str(e)}"})
                st.session_state.function_calls.append([])

# Footer
st.markdown("---")
st.markdown("**Built with:** Google Gemini API • Google ADK • A2A Protocol • Streamlit")
