#!/bin/bash
# Quick non-interactive setup using existing config

set -e

PROJECT_ID="stock-predictor-agent"
REGION="us-central1"

echo "🚀 Quick Setup for $PROJECT_ID"
echo "================================"
echo ""

gcloud config set project "$PROJECT_ID"
echo "✅ Project: $PROJECT_ID"
echo "✅ Region: $REGION"

# Enable APIs
echo ""
echo "📦 Enabling APIs..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable secretmanager.googleapis.com --quiet
gcloud services enable aiplatform.googleapis.com --quiet
gcloud services enable cloudresourcemanager.googleapis.com --quiet
gcloud services enable artifactregistry.googleapis.com --quiet
echo "✅ APIs enabled"

# Grant Cloud Build access to secrets
echo ""
echo "🔑 Granting Cloud Build access to secrets..."
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
gcloud secrets add-iam-policy-binding GOOGLE_API_KEY \
    --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor" \
    --project="$PROJECT_ID" 2>/dev/null || echo "✅ Permissions already set"

if gcloud secrets describe POLYGON_API_KEY --project="$PROJECT_ID" &>/dev/null; then
    gcloud secrets add-iam-policy-binding POLYGON_API_KEY \
        --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
        --role="roles/secretmanager.secretAccessor" \
        --project="$PROJECT_ID" 2>/dev/null || echo "✅ Permissions already set"
fi

# Create config file
echo ""
echo "📝 Creating deployment config..."
cat > .deploy_config <<EOF
PROJECT_ID=$PROJECT_ID
REGION=$REGION
EOF
echo "✅ Config saved to .deploy_config"

# Check if agents are deployed
echo ""
echo "🤖 Checking agent deployment status..."
AGENTS_DEPLOYED=true
for agent in fundamental-agent technical-agent sentiment-agent macro-agent regulatory-agent predictor-agent; do
    if ! gcloud run services describe "$agent" --region="$REGION" --project="$PROJECT_ID" &>/dev/null; then
        AGENTS_DEPLOYED=false
        echo "   ⚠️  $agent not deployed"
        break
    fi
done

if [ "$AGENTS_DEPLOYED" = "false" ]; then
    echo ""
    echo "⚠️  Some agents not deployed. Deploying agents first..."
    gcloud builds submit --config=deploy/cloudbuild.yaml \
        --substitutions=_REGION="$REGION" \
        --project="$PROJECT_ID"
    echo "✅ Agents deployed"
else
    echo "✅ All agents already deployed"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "🚀 Ready to deploy. Run:"
echo "   bash scripts/auto_deploy.sh"
echo ""

