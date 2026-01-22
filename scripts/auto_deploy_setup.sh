#!/bin/bash
# Automated Deployment Setup - Run once to configure everything

set -e

echo "🚀 Automated Deployment Setup"
echo "=============================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Install from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")
    if [ -z "$CURRENT_PROJECT" ]; then
        echo "📋 Enter your Google Cloud Project ID:"
        read -r PROJECT_ID
    else
        echo "📋 Current project: $CURRENT_PROJECT"
        echo "   Use this? (y/n):"
        read -r USE_CURRENT
        if [ "$USE_CURRENT" = "y" ] || [ "$USE_CURRENT" = "Y" ]; then
            PROJECT_ID=$CURRENT_PROJECT
        else
            echo "📋 Enter your Google Cloud Project ID:"
            read -r PROJECT_ID
        fi
    fi
else
    PROJECT_ID=$GOOGLE_CLOUD_PROJECT
fi

gcloud config set project "$PROJECT_ID"
echo "✅ Project set to: $PROJECT_ID"

# Get region
echo ""
echo "📋 Select region (default: us-central1):"
read -r REGION
REGION=${REGION:-us-central1}
echo "✅ Region: $REGION"

# Check authentication
echo ""
echo "🔐 Checking authentication..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "⚠️  Not authenticated. Please run: gcloud auth login"
    exit 1
fi
echo "✅ Authenticated"

# Enable APIs
echo ""
echo "📦 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable secretmanager.googleapis.com --quiet
gcloud services enable aiplatform.googleapis.com --quiet
gcloud services enable cloudresourcemanager.googleapis.com --quiet
gcloud services enable artifactregistry.googleapis.com --quiet
echo "✅ APIs enabled"

# Setup secrets
echo ""
echo "🔐 Setting up secrets..."

# Check if GOOGLE_API_KEY exists
if ! gcloud secrets describe GOOGLE_API_KEY --project="$PROJECT_ID" &>/dev/null; then
    echo "📋 Enter your GOOGLE_API_KEY (will be stored in Secret Manager):"
    read -sp "GOOGLE_API_KEY: " GOOGLE_API_KEY
    echo ""
    echo -n "$GOOGLE_API_KEY" | gcloud secrets create GOOGLE_API_KEY --data-file=- --project="$PROJECT_ID"
    echo "✅ GOOGLE_API_KEY stored"
else
    echo "✅ GOOGLE_API_KEY already exists"
fi

# Check if POLYGON_API_KEY exists (optional)
if ! gcloud secrets describe POLYGON_API_KEY --project="$PROJECT_ID" &>/dev/null; then
    echo "📋 Enter your POLYGON_API_KEY (optional, press Enter to skip):"
    read -sp "POLYGON_API_KEY: " POLYGON_API_KEY
    echo ""
    if [ -n "$POLYGON_API_KEY" ]; then
        echo -n "$POLYGON_API_KEY" | gcloud secrets create POLYGON_API_KEY --data-file=- --project="$PROJECT_ID"
        echo "✅ POLYGON_API_KEY stored"
    fi
else
    echo "✅ POLYGON_API_KEY already exists"
fi

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
        break
    fi
done

if [ "$AGENTS_DEPLOYED" = "false" ]; then
    echo "⚠️  Agents not deployed yet."
    echo "   Deploying agents first..."
    
    # Deploy agents
    gcloud builds submit --config=deploy/cloudbuild.yaml \
        --substitutions=_REGION="$REGION" \
        --project="$PROJECT_ID" || {
        echo "❌ Agent deployment failed. Please deploy agents manually first:"
        echo "   gcloud builds submit --config=deploy/cloudbuild.yaml"
        exit 1
    }
    
    echo "✅ Agents deployed"
else
    echo "✅ Agents already deployed"
fi

# Setup Cloud Build trigger (optional)
echo ""
echo "🔄 Setup automatic deployment on git push? (y/n):"
read -r SETUP_TRIGGER

if [ "$SETUP_TRIGGER" = "y" ] || [ "$SETUP_TRIGGER" = "Y" ]; then
    echo "📋 Enter your GitHub repository (format: owner/repo):"
    read -r GITHUB_REPO
    
    echo "📋 Enter GitHub branch (default: main):"
    read -r GITHUB_BRANCH
    GITHUB_BRANCH=${GITHUB_BRANCH:-main}
    
    # Connect GitHub repo (requires manual auth first time)
    echo "🔗 Connecting GitHub repository..."
    gcloud builds triggers create github \
        --name="deploy-chatbot" \
        --repo-name="$GITHUB_REPO" \
        --branch-pattern="^${GITHUB_BRANCH}$" \
        --build-config="deploy/cloudbuild-chatbot.yaml" \
        --substitutions="_REGION=$REGION" \
        --project="$PROJECT_ID" 2>/dev/null || {
        echo "⚠️  Could not create trigger. You may need to connect GitHub first:"
        echo "   gcloud builds triggers create github --help"
    }
    
    echo "✅ Trigger created"
fi

# Create auto-deploy script
echo ""
echo "📝 Creating auto-deploy script..."
cat > scripts/auto_deploy.sh <<'AUTODEPLOY_EOF'
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
AUTODEPLOY_EOF

chmod +x scripts/auto_deploy.sh
echo "✅ Auto-deploy script created"

# Summary
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📋 Configuration:"
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo ""
echo "🚀 To deploy now:"
echo "   bash scripts/auto_deploy.sh"
echo ""
echo "🔄 To deploy automatically on git push:"
echo "   Push to your repository - Cloud Build will trigger automatically"
echo ""
echo "📝 Config saved in: .deploy_config"
echo ""

