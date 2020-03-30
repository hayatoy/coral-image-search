In this section you will deploy Cloud Run application. Clone this repository on your [Cloud Shell](https://ssh.cloud.google.com/cloudshell/editor), or click the link below.  

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://ssh.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2Fhayatoy%2Fcoral-image-search&cloudshell_working_dir=%2Fcloudrun)

### Set your Project ID and Bucket name that you created in `Make_Index_and_Upload.ipynb`

```
export PROJECT_ID="your_project_id"
export BUCKET_NAME="your_bucket_name"
```

### Build your app and Deploy to Cloud Run
Change `--region` to your closest [location](https://cloud.google.com/run/docs/locations). 

```
gcloud builds submit --tag gcr.io/${PROJECT_ID}/coral-image-search
gcloud run deploy coral-image-search \
    --platform managed \
    --region asia-northeast1 \
    --image gcr.io/${PROJECT_ID}/coral-image-search \
    --memory 2G \
    --allow-unauthenticated \
    --update-env-vars BUCKET_NAME=${BUCKET_NAME}
```
