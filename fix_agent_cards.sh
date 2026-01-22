#!/bin/bash
# Quick script to make all agent cards publicly accessible

set -e

echo "🔧 Making Agent Cards Publicly Accessible..."
echo "=============================================="
echo ""

PROJECT_ID="stock-predictor-agent"
REGION="us-central1"

# Set project
gcloud config set project $PROJECT_ID

# List of agents
AGENTS=(
  "fundamental-agent"
  "technical-agent"
  "sentiment-agent"
  "macro-agent"
  "regulatory-agent"
  "predictor-agent"
)

# Make each agent public
for service in "${AGENTS[@]}"; do
  echo "📝 Making $service public..."
  gcloud run services add-iam-policy-binding $service \
    --region=$REGION \
    --member="allUsers" \
    --role="roles/run.invoker" \
    --quiet || echo "  ⚠️  $service - may already be public"
done

echo ""
echo "✅ Done! Verifying agent cards..."
echo ""

# Verify agent cards
for service in "${AGENTS[@]}"; do
  URL=$(gcloud run services describe $service --region=$REGION --format='value(status.url)')
  CARD_URL="${URL}/.well-known/agent-card.json"
  
  HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$CARD_URL" 2>/dev/null || echo "000")
  
  if [ "$HTTP_CODE" = "200" ]; then
    echo "  ✅ $service: Accessible (HTTP $HTTP_CODE)"
  else
    echo "  ❌ $service: Not accessible (HTTP $HTTP_CODE)"
    echo "     URL: $CARD_URL"
  fi
done

echo ""
echo "🧪 Test the orchestrator:"
echo "   ./scripts/test_agent_engine.sh AAPL"
