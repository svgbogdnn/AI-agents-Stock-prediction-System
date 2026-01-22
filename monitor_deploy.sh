#!/bin/bash
# Deployment monitoring and auto-retry script

PROJECT_ID="stock-predictor-agent"
MAX_RETRIES=5
RETRY_COUNT=0

echo "🚀 Starting deployment monitor..."
echo "Project: $PROJECT_ID"
echo "Max retries: $MAX_RETRIES"
echo ""

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    echo "=========================================="
    echo "Deployment attempt: $((RETRY_COUNT + 1))"
    echo "=========================================="
    
    # Start build
    BUILD_ID=$(gcloud builds submit --config=deploy/cloudbuild.yaml --project=$PROJECT_ID --async 2>&1 | grep -oP 'id: \K[^\s]+' || echo "")
    
    if [ -z "$BUILD_ID" ]; then
        echo "❌ Failed to start build. Retrying..."
        RETRY_COUNT=$((RETRY_COUNT + 1))
        sleep 5
        continue
    fi
    
    echo "📦 Build ID: $BUILD_ID"
    echo "⏳ Monitoring build progress..."
    
    # Monitor build
    while true; do
        STATUS=$(gcloud builds describe $BUILD_ID --project=$PROJECT_ID --format="value(status)" 2>/dev/null)
        
        if [ -z "$STATUS" ]; then
            echo "⚠️  Could not get build status. Waiting..."
            sleep 10
            continue
        fi
        
        echo "[$(date +%H:%M:%S)] Status: $STATUS"
        
        if [ "$STATUS" = "SUCCESS" ]; then
            echo ""
            echo "✅✅✅ DEPLOYMENT SUCCESSFUL! ✅✅✅"
            echo ""
            echo "Getting service URLs..."
            gcloud run services list --project=$PROJECT_ID --region=us-central1 --format="table(SERVICE,URL)" 2>/dev/null
            exit 0
        fi
        
        if [ "$STATUS" = "FAILURE" ] || [ "$STATUS" = "CANCELLED" ] || [ "$STATUS" = "TIMEOUT" ]; then
            echo ""
            echo "❌ Build failed with status: $STATUS"
            echo ""
            echo "📋 Getting build logs..."
            gcloud builds log $BUILD_ID --project=$PROJECT_ID | tail -50
            
            echo ""
            echo "🔍 Diagnosing failure..."
            
            # Check for secret access errors
            if gcloud builds log $BUILD_ID --project=$PROJECT_ID 2>&1 | grep -q "Permission.*secretmanager"; then
                echo "🔧 Fixing Secret Manager permissions..."
                PROJECT_NUMBER="257136441203"
                BUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
                
                for secret in GOOGLE_API_KEY POLYGON_API_KEY FRED_API_KEY; do
                    echo "  → Granting access to $secret"
                    gcloud secrets add-iam-policy-binding $secret \
                        --member="serviceAccount:${BUILD_SA}" \
                        --role="roles/secretmanager.secretAccessor" \
                        --project=$PROJECT_ID --quiet 2>/dev/null
                done
                echo "✅ Permissions updated"
            fi
            
            # Check for missing NEWS_API_KEY
            if gcloud builds log $BUILD_ID --project=$PROJECT_ID 2>&1 | grep -q "NEWS_API_KEY.*not exist"; then
                echo "🔧 NEWS_API_KEY is optional. Creating placeholder..."
                echo "placeholder" | gcloud secrets create NEWS_API_KEY \
                    --project=$PROJECT_ID \
                    --data-file=- 2>/dev/null || echo "  (Already exists or can't create)"
            fi
            
            RETRY_COUNT=$((RETRY_COUNT + 1))
            
            if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
                echo ""
                echo "❌ Max retries reached. Deployment failed."
                exit 1
            fi
            
            echo ""
            echo "🔄 Waiting 10 seconds before retry..."
            sleep 10
            break
        fi
        
        # Still working
        sleep 15
    done
done

echo "❌ Deployment failed after $MAX_RETRIES attempts"
exit 1

