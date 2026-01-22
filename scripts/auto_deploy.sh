#!/bin/bash
# Auto-deploy script - runs automatically or manually

set -e

# Load config
if [ -f .deploy_config ]; then
    source .deploy_config
else
    echo "❌ .deploy_config not found. Run scripts/auto_deploy_setup.sh first"
    exit 1
fi

echo "🚀 Auto-deploying to $PROJECT_ID ($REGION)..."

# Get agent URLs
echo "📡 Getting agent URLs..."
FUNDAMENTAL_URL=$(gcloud run services describe fundamental-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
TECHNICAL_URL=$(gcloud run services describe technical-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
SENTIMENT_URL=$(gcloud run services describe sentiment-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
MACRO_URL=$(gcloud run services describe macro-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
REGULATORY_URL=$(gcloud run services describe regulatory-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
PREDICTOR_URL=$(gcloud run services describe predictor-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)

# Deploy registry and chatbot
echo "📦 Building and deploying..."
gcloud builds submit \
  --config=deploy/cloudbuild-chatbot.yaml \
  --substitutions="_REGION=$REGION" \
  --project=$PROJECT_ID

# Get service URLs
REGISTRY_URL=$(gcloud run services describe agent-registry --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
CHATBOT_URL=$(gcloud run services describe stock-chatbot --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Services:"
echo "   Chatbot: $CHATBOT_URL"
echo "   Registry: $REGISTRY_URL"
echo ""
echo "🧪 Test:"
echo "   curl -X POST \"$CHATBOT_URL/chat\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"message\": \"Analyze AAPL fundamentals\"}'"

