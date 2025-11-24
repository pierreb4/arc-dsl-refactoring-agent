# Deployment script for Cloud Run
# Usage: bash deploy.sh

set -e  # Exit on error

echo "🚀 ARC-DSL Refactoring Agent - Cloud Run Deployment"
echo "=================================================="

# Check for required tools
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Install from https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check for API key
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  Warning: GOOGLE_API_KEY not set in environment"
    read -p "Enter your Gemini API key: " GOOGLE_API_KEY
fi

# Get project configuration
read -p "Enter your GCP Project ID (or press Enter for current): " PROJECT_ID
if [ -z "$PROJECT_ID" ]; then
    PROJECT_ID=$(gcloud config get-value project)
fi

read -p "Enter region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

SERVICE_NAME="arc-dsl-refactoring-agent"

echo ""
echo "📋 Deployment Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service Name: $SERVICE_NAME"
echo ""

read -p "Proceed with deployment? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Deployment cancelled."
    exit 0
fi

# Set project
echo "🔧 Setting project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com --quiet

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="$GOOGLE_API_KEY" \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --timeout 300 \
  --quiet

# Get service URL
echo ""
echo "✅ Deployment complete!"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format 'value(status.url)')

echo ""
echo "🌐 Your service is live at:"
echo "   $SERVICE_URL"
echo ""
echo "📊 Next steps:"
echo "   1. Visit $SERVICE_URL to access the web UI"
echo "   2. Test the API: curl $SERVICE_URL/api/health"
echo "   3. View logs: gcloud run services logs read $SERVICE_NAME --region $REGION"
echo ""
echo "🎉 Ready for Kaggle Capstone submission!"
