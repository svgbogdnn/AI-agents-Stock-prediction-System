#!/bin/bash
# Start all A2A agent servers in background
# Following Day 5b deployment pattern

echo "🚀 Starting Stock Prediction System - All Agents"
echo "================================================"

# Get the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Set Python command to use venv
PYTHON="./venv/bin/python"

# Check if venv exists
if [ ! -f "$PYTHON" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run: python3 -m venv venv"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Please create it from .env.example"
    echo "   Copy .env.example to .env and add your API keys"
    exit 1
fi

# Start each agent server in background
echo ""
echo "Starting agents..."

echo "  → Fundamental Analyst (port 8001)..."
$PYTHON agents/fundamental_analyst_server.py > logs/fundamental_8001.log 2>&1 &
echo $! > .pids/fundamental.pid

echo "  → Technical Analyst (port 8002)..."
$PYTHON agents/technical_analyst_server.py > logs/technical_8002.log 2>&1 &
echo $! > .pids/technical.pid

echo "  → Sentiment Analyst (port 8003)..."
$PYTHON agents/news_sentiment_analyst_server.py > logs/sentiment_8003.log 2>&1 &
echo $! > .pids/sentiment.pid

echo "  → Macro Analyst (port 8004)..."
$PYTHON agents/macro_analyst_server.py > logs/macro_8004.log 2>&1 &
echo $! > .pids/macro.pid

echo "  → Regulatory Analyst (port 8005)..."
$PYTHON agents/regulatory_analyst_server.py > logs/regulatory_8005.log 2>&1 &
echo $! > .pids/regulatory.pid

echo "  → Predictor Agent (port 8006)..."
$PYTHON agents/predictor_agent_server.py > logs/predictor_8006.log 2>&1 &
echo $! > .pids/predictor.pid

echo ""
echo "⏳ Waiting for agents to initialize (15 seconds)..."
sleep 15

echo ""
echo "Verifying agent cards..."
echo ""

# Verify each agent by checking its agent card
for port in 8001 8002 8003 8004 8005 8006; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/.well-known/agent-card.json)
    if [ "$response" = "200" ]; then
        agent_name=$(curl -s http://localhost:$port/.well-known/agent-card.json | python -c "import sys, json; print(json.load(sys.stdin).get('name', 'unknown'))" 2>/dev/null)
        echo "  ✅ Port $port: $agent_name"
    else
        echo "  ❌ Port $port: Not responding (HTTP $response)"
    fi
done

echo ""
echo "================================================"
echo "✅ All agents started!"
echo ""
echo "Agent Cards:"
echo "  • http://localhost:8001/.well-known/agent-card.json"
echo "  • http://localhost:8002/.well-known/agent-card.json"
echo "  • http://localhost:8003/.well-known/agent-card.json"
echo "  • http://localhost:8004/.well-known/agent-card.json"
echo "  • http://localhost:8005/.well-known/agent-card.json"
echo "  • http://localhost:8006/.well-known/agent-card.json"
echo ""
echo "Logs: $PROJECT_ROOT/logs/"
echo ""
echo "To analyze a stock:"
echo "  ./venv/bin/python main.py --ticker GOOGL"
echo ""
echo "To stop all agents:"
echo "  bash scripts/stop_all_agents.sh"
echo "================================================"

