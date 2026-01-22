#!/bin/bash
# Test deployed services

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Testing Cloud Deployment${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Get project
read -p "Enter your GCP Project ID: " PROJECT_ID
read -p "Enter region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

gcloud config set project $PROJECT_ID

echo ""
echo -e "${YELLOW}🔍 Discovering services...${NC}"
echo ""

# Get orchestrator URL
ORCHESTRATOR_URL=$(gcloud run services describe orchestrator --region=$REGION --format='value(status.url)' 2>/dev/null || echo "")

if [ -z "$ORCHESTRATOR_URL" ]; then
    echo -e "${RED}❌ Orchestrator not found. Please deploy first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Orchestrator: $ORCHESTRATOR_URL${NC}"

# Get agent URLs
echo ""
echo -e "${BLUE}Agent Services:${NC}"
for agent in fundamental technical sentiment macro regulatory predictor; do
    URL=$(gcloud run services describe ${agent}-agent --region=$REGION --format='value(status.url)' 2>/dev/null || echo "NOT FOUND")
    if [ "$URL" != "NOT FOUND" ]; then
        echo -e "  ${GREEN}✓${NC} ${agent}-agent: $URL"
    else
        echo -e "  ${RED}✗${NC} ${agent}-agent: NOT DEPLOYED"
    fi
done

# Test orchestrator health
echo ""
echo -e "${YELLOW}🏥 Testing health checks...${NC}"
echo ""

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$ORCHESTRATOR_URL/health")
if [ "$HTTP_CODE" == "200" ]; then
    echo -e "${GREEN}✓ Orchestrator health check passed${NC}"
else
    echo -e "${RED}✗ Orchestrator health check failed (HTTP $HTTP_CODE)${NC}"
fi

# Test analysis
echo ""
echo -e "${YELLOW}📊 Running sample analysis (AAPL)...${NC}"
echo ""

RESPONSE=$(curl -s "$ORCHESTRATOR_URL/api/analyze?ticker=AAPL" || echo '{"error":"request failed"}')

# Check if response contains expected fields
if echo "$RESPONSE" | grep -q "recommendation"; then
    echo -e "${GREEN}✓ Analysis completed successfully${NC}"
    echo ""
    echo "Response summary:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null | head -n 20 || echo "$RESPONSE" | head -n 10
else
    echo -e "${RED}✗ Analysis failed${NC}"
    echo "Error: $RESPONSE"
fi

# Test UI
echo ""
echo -e "${YELLOW}🎨 Checking UI deployment...${NC}"
echo ""

APP_URL=$(gcloud app browse --no-launch-browser 2>&1 | grep -o 'https://[^"]*' || echo "")
if [ ! -z "$APP_URL" ]; then
    echo -e "${GREEN}✓ UI deployed: $APP_URL${NC}"
    
    # Test UI health
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL")
    if [ "$HTTP_CODE" == "200" ]; then
        echo -e "${GREEN}✓ UI is accessible${NC}"
    else
        echo -e "${YELLOW}⚠️  UI returned HTTP $HTTP_CODE${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  UI not deployed yet${NC}"
    echo "   Run: ./deploy/deploy-vertex-ui.sh"
fi

# Performance test
echo ""
echo -e "${YELLOW}⚡ Testing performance...${NC}"
echo ""

START_TIME=$(date +%s)
curl -s "$ORCHESTRATOR_URL/api/analyze?ticker=GOOGL" > /dev/null
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

if [ $ELAPSED -lt 15 ]; then
    echo -e "${GREEN}✓ Fast response: ${ELAPSED}s${NC}"
elif [ $ELAPSED -lt 30 ]; then
    echo -e "${YELLOW}⚠️  Moderate response: ${ELAPSED}s${NC}"
else
    echo -e "${RED}✗ Slow response: ${ELAPSED}s${NC}"
fi

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Test Summary${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${GREEN}Services:${NC}"
echo "  Orchestrator: $ORCHESTRATOR_URL"
if [ ! -z "$APP_URL" ]; then
    echo "  UI: $APP_URL"
fi
echo ""
echo -e "${GREEN}Quick tests:${NC}"
echo "  Health: curl $ORCHESTRATOR_URL/health"
echo "  Analyze: curl '$ORCHESTRATOR_URL/api/analyze?ticker=AAPL'"
echo ""
echo -e "${GREEN}Monitor:${NC}"
echo "  Logs: gcloud logging tail 'resource.type=cloud_run_revision'"
echo "  Console: https://console.cloud.google.com/run?project=$PROJECT_ID"
echo ""

# Interactive test
echo -e "${YELLOW}💡 Try interactive test? (y/n)${NC}"
read -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    while true; do
        echo ""
        read -p "Enter ticker symbol (or 'quit'): " TICKER
        
        if [ "$TICKER" == "quit" ]; then
            break
        fi
        
        TICKER=$(echo "$TICKER" | tr '[:lower:]' '[:upper:]')
        
        echo ""
        echo -e "${BLUE}Analyzing $TICKER...${NC}"
        
        RESULT=$(curl -s "$ORCHESTRATOR_URL/api/analyze?ticker=$TICKER")
        
        # Extract key fields
        RECOMMENDATION=$(echo "$RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('recommendation', data.get('prediction', {}).get('recommendation', 'N/A')))" 2>/dev/null || echo "N/A")
        CONFIDENCE=$(echo "$RESULT" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('confidence', data.get('prediction', {}).get('confidence', 'N/A')))" 2>/dev/null || echo "N/A")
        
        echo ""
        echo -e "${GREEN}Recommendation: $RECOMMENDATION${NC}"
        echo -e "${GREEN}Confidence: $CONFIDENCE%${NC}"
        
        echo ""
        echo "Full response:"
        echo "$RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESULT"
    done
fi

echo ""
echo -e "${GREEN}✨ Testing complete!${NC}"
echo ""

