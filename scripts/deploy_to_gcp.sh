#!/bin/bash
# Deploy Chatbot and Agent Registry to Google Cloud Platform

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}
REGION=${REGION:-us-central1}

echo "🚀 Deploying to Google Cloud Platform"
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo ""

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Not authenticated. Run: gcloud auth login"
    exit 1
fi

# Enable required APIs
echo "📦 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable secretmanager.googleapis.com --quiet
gcloud services enable aiplatform.googleapis.com --quiet

# Check if secrets exist
echo "🔐 Checking secrets..."
if ! gcloud secrets describe GOOGLE_API_KEY --project=$PROJECT_ID &>/dev/null; then
    echo "⚠️  GOOGLE_API_KEY secret not found. Creating..."
    read -sp "Enter GOOGLE_API_KEY: " api_key
    echo ""
    echo -n "$api_key" | gcloud secrets create GOOGLE_API_KEY --data-file=- --project=$PROJECT_ID
fi

# Deploy agents first (if not already deployed)
echo ""
echo "🤖 Checking if agents are deployed..."
if ! gcloud run services describe fundamental-agent --region=$REGION --project=$PROJECT_ID &>/dev/null; then
    echo "⚠️  Agents not deployed. Deploying agents first..."
    echo "   Run: gcloud builds submit --config=deploy/cloudbuild.yaml"
    echo "   Then re-run this script."
    exit 1
fi

# Get agent URLs
echo "📡 Getting agent URLs..."
FUNDAMENTAL_URL=$(gcloud run services describe fundamental-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
TECHNICAL_URL=$(gcloud run services describe technical-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
SENTIMENT_URL=$(gcloud run services describe sentiment-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
MACRO_URL=$(gcloud run services describe macro-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
REGULATORY_URL=$(gcloud run services describe regulatory-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
PREDICTOR_URL=$(gcloud run services describe predictor-agent --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)

echo "   ✅ Found all agent URLs"

# Deploy agent registry
echo ""
echo "📋 Deploying Agent Registry..."
gcloud builds submit \
  --config=deploy/cloudbuild-chatbot.yaml \
  --substitutions=_REGION=$REGION \
  --project=$PROJECT_ID

REGISTRY_URL=$(gcloud run services describe agent-registry --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)
echo "   ✅ Registry deployed: $REGISTRY_URL"

# Deploy chatbot
echo ""
echo "🤖 Deploying Chatbot..."
gcloud run deploy stock-chatbot \
  --image=gcr.io/$PROJECT_ID/stock-chatbot:latest \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --set-env-vars="FUNDAMENTAL_AGENT_URL=$FUNDAMENTAL_URL,TECHNICAL_AGENT_URL=$TECHNICAL_URL,SENTIMENT_AGENT_URL=$SENTIMENT_URL,MACRO_AGENT_URL=$MACRO_URL,REGULATORY_AGENT_URL=$REGULATORY_URL,PREDICTOR_AGENT_URL=$PREDICTOR_URL,AGENT_REGISTRY_URL=$REGISTRY_URL" \
  --set-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest" \
  --memory=2Gi \
  --cpu=2 \
  --timeout=600 \
  --max-instances=20 \
  --min-instances=1 \
  --project=$PROJECT_ID

CHATBOT_URL=$(gcloud run services describe stock-chatbot --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)

echo ""
echo "✅ Deployment Complete!"
echo ""
echo "📋 Services:"
echo "   Chatbot: $CHATBOT_URL"
echo "   Registry: $REGISTRY_URL"
echo ""
echo "🧪 Test:"
echo "   curl -X POST \"$CHATBOT_URL/chat\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"message\": \"Analyze AAPL fundamentals\"}'"
echo ""
echo "📊 View logs:"
echo "   gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=stock-chatbot\" --limit=10"

