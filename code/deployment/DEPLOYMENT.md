# ARC-DSL Refactoring Agent - Cloud Run Deployment

## Quick Deploy to Google Cloud Run

### Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud SDK** installed ([Install gcloud](https://cloud.google.com/sdk/docs/install))
3. **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/app/api-keys)

### One-Command Deployment

```bash
# Set your project ID and region
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Authenticate
gcloud auth login
gcloud config set project $PROJECT_ID

# Deploy to Cloud Run (builds and deploys in one command)
gcloud run deploy arc-dsl-refactoring-agent \
  --source . \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="your-gemini-api-key-here" \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --timeout 300
```

### Step-by-Step Deployment

#### 1. Enable Required APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

#### 2. Build Docker Image

```bash
# Build locally (optional - Cloud Run can build automatically)
docker build -t arc-dsl-refactoring-agent .

# Test locally
docker run -p 8080:8080 \
  -e GOOGLE_API_KEY="your-api-key" \
  arc-dsl-refactoring-agent
```

#### 3. Deploy to Cloud Run

```bash
# Deploy with automatic build
gcloud run deploy arc-dsl-refactoring-agent \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_API_KEY="your-gemini-api-key" \
  --memory 1Gi
```

#### 4. Get Service URL

```bash
# Service URL will be displayed after deployment
# Example: https://arc-dsl-refactoring-agent-xxxxxxxxxx-uc.a.run.app

# Or retrieve it:
gcloud run services describe arc-dsl-refactoring-agent \
  --region us-central1 \
  --format 'value(status.url)'
```

### Using the Deployed Application

Once deployed, visit your Cloud Run URL to access the web interface:

1. **Landing Page**: Interactive workflow UI
2. **Analyze Function**: Enter function name (e.g., "first", "last")
3. **Review Proposals**: See ADK-approved specialized versions
4. **Approve/Reject**: Human-in-the-loop decision making

### API Endpoints

- `GET /` - Web UI for HITL workflow
- `POST /api/analyze` - Analyze function usage and generate proposals
- `GET /api/health` - Health check (returns 200 if healthy)
- `GET /api/metrics` - System metrics

### Example API Usage

```bash
# Health check
curl https://your-service-url.run.app/api/health

# Analyze function
curl -X POST https://your-service-url.run.app/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "generic_function": "first",
    "source_file": "arc-dsl/solvers.py"
  }'
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_API_KEY` | Yes | Gemini API key from AI Studio |
| `PORT` | No | Port to run on (default: 8080) |

### Updating the Deployment

```bash
# Redeploy after code changes
gcloud run deploy arc-dsl-refactoring-agent \
  --source . \
  --region us-central1
```

### Monitoring

```bash
# View logs
gcloud run services logs read arc-dsl-refactoring-agent \
  --region us-central1 \
  --limit 50

# Monitor metrics in Cloud Console
open "https://console.cloud.google.com/run/detail/$REGION/arc-dsl-refactoring-agent/metrics?project=$PROJECT_ID"
```

### Troubleshooting

**Issue**: Deployment fails with "GOOGLE_API_KEY not set"
- **Solution**: Add `--set-env-vars GOOGLE_API_KEY="your-key"` to deploy command

**Issue**: Container fails health check
- **Solution**: Check logs with `gcloud run services logs read`

**Issue**: 403 Forbidden
- **Solution**: Add `--allow-unauthenticated` or configure IAM properly

### Cost Estimation

Cloud Run pricing (as of Nov 2024):
- **Free tier**: 2 million requests/month, 360,000 GB-seconds
- **After free tier**: ~$0.00002400 per request, $0.00000900 per GB-second
- **Estimated cost**: <$5/month for light usage

### Security Best Practices

1. **Use Secret Manager** for API keys:
   ```bash
   # Store secret
   echo -n "your-api-key" | gcloud secrets create gemini-api-key --data-file=-
   
   # Deploy with secret
   gcloud run deploy arc-dsl-refactoring-agent \
     --set-secrets GOOGLE_API_KEY=gemini-api-key:latest
   ```

2. **Enable authentication** for production:
   ```bash
   # Remove --allow-unauthenticated
   # Add IAM policy for authorized users
   gcloud run services add-iam-policy-binding arc-dsl-refactoring-agent \
     --member="user:your-email@example.com" \
     --role="roles/run.invoker"
   ```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
export GOOGLE_API_KEY="your-api-key"
python app.py

# Visit http://localhost:8080
```

---

**Documentation**: See [README.md](../../README.md) for full project details  
**Issues**: Report at GitHub repository  
**Status**: ✅ Production-ready for Kaggle Capstone submission
