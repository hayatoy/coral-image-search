```
export PROJECT_ID="your_project_id"
export BUCKET_NAME="your_bucket_name"
gcloud builds submit --tag gcr.io/${PROJECT_ID}/coral-image-search
gcloud run deploy coral-image-search \
    --platform managed \
    --region asia-northeast1 \
    --image gcr.io/${PROJECT_ID}/coral-image-search \
    --memory 2G \
    --allow-unauthenticated \
    --update-env-vars BUCKET_NAME=${BUCKET_NAME}
```
