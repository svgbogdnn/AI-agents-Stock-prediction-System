#!/bin/bash
# Deployment script for Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Stock Prediction System - Cloud Deployment${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI not found. Please install it first:${NC}"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
echo -e "${YELLOW}📋 Configuration${NC}"
echo ""
read -p "Enter your GCP Project ID: " PROJECT_ID
read -p "Enter deployment region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

echo ""
echo -e "${GREEN}✓ Project ID: ${PROJECT_ID}${NC}"
echo -e "${GREEN}✓ Region: ${REGION}${NC}"
echo ""

# Set project
echo -e "${YELLOW}🔧 Setting GCP project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo ""
echo -e "${YELLOW}🔌 Enabling required APIs...${NC}"
gcloud services enable \
    cloudbuild.googleapis.com \
    run.googleapis.com \
    containerregistry.googleapis.com \
    secretmanager.googleapis.com \
    aiplatform.googleapis.com

echo -e "${GREEN}✓ APIs enabled${NC}"

# Create secrets (if they don't exist)
echo ""
echo -e "${YELLOW}🔐 Setting up secrets...${NC}"
echo ""
echo "Please enter your API keys (they will be stored securely in Secret Manager)"
echo ""

# Function to create/update secret
create_or_update_secret() {
    local SECRET_NAME=$1
    local SECRET_VALUE=$2
    
    if gcloud secrets describe $SECRET_NAME &> /dev/null; then
        echo "Updating existing secret: $SECRET_NAME"
        echo -n "$SECRET_VALUE" | gcloud secrets versions add $SECRET_NAME --data-file=-
    else
        echo "Creating new secret: $SECRET_NAME"
        echo -n "$SECRET_VALUE" | gcloud secrets create $SECRET_NAME --data-file=-
    fi
}

read -sp "Google API Key: " GOOGLE_API_KEY
echo ""
create_or_update_secret "GOOGLE_API_KEY" "$GOOGLE_API_KEY"

read -sp "Polygon API Key: " POLYGON_API_KEY
echo ""
create_or_update_secret "POLYGON_API_KEY" "$POLYGON_API_KEY"

read -sp "FRED API Key (optional, press enter to skip): " FRED_API_KEY
echo ""
if [ ! -z "$FRED_API_KEY" ]; then
    create_or_update_secret "FRED_API_KEY" "$FRED_API_KEY"
fi

read -sp "News API Key (optional, press enter to skip): " NEWS_API_KEY
echo ""
if [ ! -z "$NEWS_API_KEY" ]; then
    create_or_update_secret "NEWS_API_KEY" "$NEWS_API_KEY"
fi

echo ""
echo -e "${GREEN}✓ Secrets configured${NC}"

# Build and deploy using Cloud Build
echo ""
echo -e "${YELLOW}🏗️  Building and deploying services...${NC}"
echo ""
echo "This will:"
echo "  1. Build container images"
echo "  2. Deploy 6 specialist agents to Cloud Run"
echo "  3. Deploy orchestrator service"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

# Submit build
gcloud builds submit \
    --config=deploy/cloudbuild.yaml \
    --substitutions=_REGION=$REGION \
    .

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🎉 Deployment Complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Get service URLs
echo -e "${BLUE}📡 Service URLs:${NC}"
echo ""
ORCHESTRATOR_URL=$(gcloud run services describe orchestrator --region=$REGION --format='value(status.url)')
echo -e "${GREEN}Orchestrator API:${NC} $ORCHESTRATOR_URL"
echo ""

echo -e "${BLUE}Agent Services:${NC}"
for agent in fundamental technical sentiment macro regulatory predictor; do
    URL=$(gcloud run services describe ${agent}-agent --region=$REGION --format='value(status.url)' 2>/dev/null || echo "Not found")
    echo "  ${agent}-agent: $URL"
done

echo ""
echo -e "${BLUE}🧪 Test your deployment:${NC}"
echo ""
echo "  curl '$ORCHESTRATOR_URL/health'"
echo "  curl '$ORCHESTRATOR_URL/api/analyze?ticker=AAPL'"
echo ""

echo -e "${BLUE}📊 View logs:${NC}"
echo ""
echo "  gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=orchestrator' --limit 50"
echo ""

echo -e "${BLUE}💰 Monitor costs:${NC}"
echo ""
echo "  https://console.cloud.google.com/billing/${PROJECT_ID}"
echo ""

echo -e "${YELLOW}⚠️  Important:${NC}"
echo "  - All services are publicly accessible"
echo "  - Consider adding authentication for production"
echo "  - Monitor your API usage and costs"
echo "  - Services scale to zero when not in use"
echo ""

echo -e "${GREEN}✨ Next: Deploy the Vertex AI UI${NC}"
echo "  Run: ./deploy/deploy-vertex-ui.sh"
echo ""

