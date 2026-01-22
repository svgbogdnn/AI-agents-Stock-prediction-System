#!/bin/bash
# Deploy the Vertex AI UI to App Engine

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Vertex AI UI Deployment${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Get project and region
read -p "Enter your GCP Project ID: " PROJECT_ID
read -p "Enter region where orchestrator is deployed (default: us-central1): " REGION
REGION=${REGION:-us-central1}

gcloud config set project $PROJECT_ID

# Get orchestrator URL
echo ""
echo -e "${YELLOW}🔍 Finding orchestrator URL...${NC}"
ORCHESTRATOR_URL=$(gcloud run services describe orchestrator --region=$REGION --format='value(status.url)' 2>/dev/null)

if [ -z "$ORCHESTRATOR_URL" ]; then
    echo -e "${RED}❌ Orchestrator service not found. Please deploy backend first.${NC}"
    echo "   Run: ./deploy/deploy.sh"
    exit 1
fi

echo -e "${GREEN}✓ Found orchestrator: ${ORCHESTRATOR_URL}${NC}"

# Update app.yaml with orchestrator URL
echo ""
echo -e "${YELLOW}📝 Configuring UI...${NC}"
sed -i.bak "s|ORCHESTRATOR_URL:.*|ORCHESTRATOR_URL: \"${ORCHESTRATOR_URL}\"|" deploy/vertex-ui/app.yaml
rm deploy/vertex-ui/app.yaml.bak 2>/dev/null || true

# Update index.html with orchestrator URL
sed -i.bak "s|window.ORCHESTRATOR_URL.*||" deploy/vertex-ui/index.html
sed -i.bak "s|<head>|<head>\n    <meta name=\"orchestrator-url\" content=\"${ORCHESTRATOR_URL}\">|" deploy/vertex-ui/index.html
rm deploy/vertex-ui/index.html.bak 2>/dev/null || true

echo -e "${GREEN}✓ Configuration updated${NC}"

# Deploy to App Engine
echo ""
echo -e "${YELLOW}🚀 Deploying to App Engine...${NC}"
cd deploy/vertex-ui
gcloud app deploy --quiet
cd ../..

# Get App Engine URL
APP_URL=$(gcloud app browse --no-launch-browser 2>&1 | grep -o 'https://[^"]*' || echo "https://${PROJECT_ID}.uc.r.appspot.com")

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  🎉 UI Deployed Successfully!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}🌐 Access your UI:${NC}"
echo ""
echo -e "${GREEN}${APP_URL}${NC}"
echo ""
echo -e "${BLUE}📊 Try analyzing some stocks:${NC}"
echo "  - ${APP_URL}?ticker=AAPL"
echo "  - ${APP_URL}?ticker=GOOGL"
echo "  - ${APP_URL}?ticker=NVDA"
echo ""
echo -e "${YELLOW}💡 Features:${NC}"
echo "  ✓ Real-time agent workflow visualization"
echo "  ✓ Live execution timeline"
echo "  ✓ Interactive signal meters"
echo "  ✓ Confidence gauges"
echo "  ✓ Beautiful dark theme UI"
echo ""

