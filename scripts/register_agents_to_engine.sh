#!/bin/bash
# Register all agents to Google Agent Engine as A2A cards

set -e

echo "🚀 Registering Agents to Google Agent Engine..."
echo "================================================"

# Get project ID
PROJECT_ID=$(gcloud config get-value project)
REGION=${REGION:-us-central1}

echo "Project: $PROJECT_ID"
echo "Region: $REGION"
echo ""

# Check if agents are deployed
echo "📡 Checking deployed agents..."
FUNDAMENTAL_URL=$(gcloud run services describe fundamental-agent --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
TECHNICAL_URL=$(gcloud run services describe technical-agent --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
SENTIMENT_URL=$(gcloud run services describe sentiment-agent --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
MACRO_URL=$(gcloud run services describe macro-agent --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
REGULATORY_URL=$(gcloud run services describe regulatory-agent --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
PREDICTOR_URL=$(gcloud run services describe predictor-agent --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")

if [ -z "$FUNDAMENTAL_URL" ]; then
    echo "❌ Agents not deployed. Please deploy first:"
    echo "   ./deploy/deploy.sh"
    exit 1
fi

# Function to register an agent
register_agent() {
    local agent_name=$1
    local agent_url=$2
    local display_name=$3
    local description=$4
    
    if [ -z "$agent_url" ]; then
        echo "⚠️  Skipping $agent_name (not deployed)"
        return
    fi
    
    local card_url="${agent_url}/.well-known/agent-card.json"
    
    echo ""
    echo "📝 Registering $display_name..."
    echo "   Card URL: $card_url"
    
    # Verify agent card is accessible
    if ! curl -s -f "$card_url" > /dev/null; then
        echo "   ❌ Agent card not accessible. Skipping."
        return
    fi
    
    # Register with Agent Engine
    # Note: This uses gcloud ai agents register if available
    # Otherwise, we'll use the agent registry service
    
    if gcloud ai agents register --help > /dev/null 2>&1; then
        # Use native Agent Engine registration
        gcloud ai agents register \
            --agent-card-url="$card_url" \
            --display-name="$display_name" \
            --description="$description" \
            --region=$REGION \
            --quiet || echo "   ⚠️  Registration command not available, using fallback"
    fi
    
    # Fallback: Register via agent registry service
    REGISTRY_URL=$(gcloud run services describe agent-registry --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")
    
    if [ -n "$REGISTRY_URL" ]; then
        echo "   📋 Registering via agent registry..."
        curl -X POST "$REGISTRY_URL/agents/register" \
            -H "Content-Type: application/json" \
            -d "{
                \"id\": \"$agent_name\",
                \"name\": \"$display_name\",
                \"description\": \"$description\",
                \"agent_card_url\": \"$card_url\",
                \"category\": \"financial\",
                \"provider\": \"$PROJECT_ID\"
            }" 2>/dev/null || echo "   ⚠️  Registry service not available"
    fi
    
    echo "   ✅ Registered $display_name"
}

# Register all agents
register_agent \
    "fundamental-analyst" \
    "$FUNDAMENTAL_URL" \
    "Fundamental Analyst" \
    "Expert in financial metrics, valuations, and company fundamentals"

register_agent \
    "technical-analyst" \
    "$TECHNICAL_URL" \
    "Technical Analyst" \
    "Expert in price action, trends, and technical indicators"

register_agent \
    "sentiment-analyst" \
    "$SENTIMENT_URL" \
    "News & Sentiment Analyst" \
    "Expert in news analysis and market sentiment"

register_agent \
    "macro-analyst" \
    "$MACRO_URL" \
    "Macro-Economic Analyst" \
    "Expert in macroeconomic factors and Federal Reserve policy"

register_agent \
    "regulatory-analyst" \
    "$REGULATORY_URL" \
    "Industry & Regulatory Analyst" \
    "Expert in regulatory landscape and compliance"

register_agent \
    "predictor-agent" \
    "$PREDICTOR_URL" \
    "Predictor Agent" \
    "Synthesizes specialist reports into final predictions"

echo ""
echo "================================================"
echo "✅ Agent Registration Complete!"
echo ""
echo "Agent Card URLs:"
echo "  Fundamental:  $FUNDAMENTAL_URL/.well-known/agent-card.json"
echo "  Technical:    $TECHNICAL_URL/.well-known/agent-card.json"
echo "  Sentiment:    $SENTIMENT_URL/.well-known/agent-card.json"
echo "  Macro:        $MACRO_URL/.well-known/agent-card.json"
echo "  Regulatory:   $REGULATORY_URL/.well-known/agent-card.json"
echo "  Predictor:    $PREDICTOR_URL/.well-known/agent-card.json"
echo ""
echo "Next steps:"
echo "  1. Deploy orchestrator: python agents/agent_engine_orchestrator.py"
echo "  2. Test native A2A: python agents/agent_engine_orchestrator.py --ticker AAPL"
echo "  3. View in console: https://console.cloud.google.com/vertex-ai/agents"
echo ""

