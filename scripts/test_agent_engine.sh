#!/bin/bash
# Test Agent Engine native orchestrator

set -e

echo "🧪 Testing Agent Engine Native A2A Orchestrator"
echo "=================================================="
echo ""

# Activate venv if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Set up environment variables
echo "🔧 Setting up environment variables..."
source ./scripts/setup_agent_engine_env.sh 2>/dev/null || true

# Export them for the Python script
export FUNDAMENTAL_AGENT_CARD_URL="${FUNDAMENTAL_AGENT_CARD_URL:-http://localhost:8001/.well-known/agent-card.json}"
export TECHNICAL_AGENT_CARD_URL="${TECHNICAL_AGENT_CARD_URL:-http://localhost:8002/.well-known/agent-card.json}"
export SENTIMENT_AGENT_CARD_URL="${SENTIMENT_AGENT_CARD_URL:-http://localhost:8003/.well-known/agent-card.json}"
export MACRO_AGENT_CARD_URL="${MACRO_AGENT_CARD_URL:-http://localhost:8004/.well-known/agent-card.json}"
export REGULATORY_AGENT_CARD_URL="${REGULATORY_AGENT_CARD_URL:-http://localhost:8005/.well-known/agent-card.json}"
export PREDICTOR_AGENT_CARD_URL="${PREDICTOR_AGENT_CARD_URL:-http://localhost:8006/.well-known/agent-card.json}"

echo ""
echo "✅ Environment ready!"
echo ""
echo "Agent Card URLs:"
echo "  Fundamental:  $FUNDAMENTAL_AGENT_CARD_URL"
echo "  Technical:    $TECHNICAL_AGENT_CARD_URL"
echo "  Sentiment:    $SENTIMENT_AGENT_CARD_URL"
echo "  Macro:        $MACRO_AGENT_CARD_URL"
echo "  Regulatory:   $REGULATORY_AGENT_CARD_URL"
echo "  Predictor:    $PREDICTOR_AGENT_CARD_URL"
echo ""

# Get ticker from args or use default
TICKER=${1:-AAPL}

echo "🚀 Testing with ticker: $TICKER"
echo ""

# Run the orchestrator
if [ -d "venv" ]; then
    ./venv/bin/python agents/agent_engine_orchestrator.py --ticker "$TICKER" ${2:+"--verbose"}
else
    python3 agents/agent_engine_orchestrator.py --ticker "$TICKER" ${2:+"--verbose"}
fi

echo ""
echo "✅ Test complete!"

