#!/bin/bash
# Set environment variables for Agent Engine native orchestrator

# Get agent URLs from Cloud Run
REGION=${REGION:-us-central1}

echo "🔧 Setting up Agent Engine environment variables..."
echo ""

FUNDAMENTAL_URL=$(gcloud run services describe fundamental-agent --region=$REGION --format='value(status.url)' 2>/dev/null)
TECHNICAL_URL=$(gcloud run services describe technical-agent --region=$REGION --format='value(status.url)' 2>/dev/null)
SENTIMENT_URL=$(gcloud run services describe sentiment-agent --region=$REGION --format='value(status.url)' 2>/dev/null)
MACRO_URL=$(gcloud run services describe macro-agent --region=$REGION --format='value(status.url)' 2>/dev/null)
REGULATORY_URL=$(gcloud run services describe regulatory-agent --region=$REGION --format='value(status.url)' 2>/dev/null)
PREDICTOR_URL=$(gcloud run services describe predictor-agent --region=$REGION --format='value(status.url)' 2>/dev/null)

# Export agent card URLs
export FUNDAMENTAL_AGENT_CARD_URL="${FUNDAMENTAL_URL}/.well-known/agent-card.json"
export TECHNICAL_AGENT_CARD_URL="${TECHNICAL_URL}/.well-known/agent-card.json"
export SENTIMENT_AGENT_CARD_URL="${SENTIMENT_URL}/.well-known/agent-card.json"
export MACRO_AGENT_CARD_URL="${MACRO_URL}/.well-known/agent-card.json"
export REGULATORY_AGENT_CARD_URL="${REGULATORY_URL}/.well-known/agent-card.json"
export PREDICTOR_AGENT_CARD_URL="${PREDICTOR_URL}/.well-known/agent-card.json"

echo "✅ Environment variables set:"
echo ""
echo "export FUNDAMENTAL_AGENT_CARD_URL=\"$FUNDAMENTAL_AGENT_CARD_URL\""
echo "export TECHNICAL_AGENT_CARD_URL=\"$TECHNICAL_AGENT_CARD_URL\""
echo "export SENTIMENT_AGENT_CARD_URL=\"$SENTIMENT_AGENT_CARD_URL\""
echo "export MACRO_AGENT_CARD_URL=\"$MACRO_AGENT_CARD_URL\""
echo "export REGULATORY_AGENT_CARD_URL=\"$REGULATORY_AGENT_CARD_URL\""
echo "export PREDICTOR_AGENT_CARD_URL=\"$PREDICTOR_AGENT_CARD_URL\""
echo ""
echo "💡 To use these in your shell, run:"
echo "   source ./scripts/setup_agent_engine_env.sh"
echo ""
echo "🧪 Then test with:"
echo "   python agents/agent_engine_orchestrator.py --ticker AAPL"

