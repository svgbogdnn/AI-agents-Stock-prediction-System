#!/bin/bash
# Start the Function Calling Chatbot Demo

echo "🚀 Starting Function Calling Chatbot Demo..."
echo ""

# Check if agents are running
echo "📡 Checking A2A agents..."
agents_running=true
for port in 8001 8002 8003 8004 8005 8006; do
    if ! curl -s http://localhost:$port/.well-known/agent-card.json > /dev/null 2>&1; then
        agents_running=false
        echo "  ⚠️  Agent on port $port is not running"
    fi
done

if [ "$agents_running" = false ]; then
    echo ""
    echo "❌ Some agents are not running!"
    echo "   Please start agents first: bash scripts/start_all_agents.sh"
    echo ""
    exit 1
fi

echo "✅ All agents are running"
echo ""

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY not set"
    echo "   Please set it: export GOOGLE_API_KEY=your_key"
    echo ""
fi

# Start Streamlit
echo "🌐 Starting Streamlit chatbot..."
echo "   URL: http://localhost:8501"
echo ""

streamlit run chatbot_function_calling.py --server.port 8501 --server.address localhost

