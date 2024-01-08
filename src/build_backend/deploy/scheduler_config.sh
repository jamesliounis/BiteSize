gcloud scheduler jobs create http generate-mcq-job \
  --schedule="*/5 * * * *" \
  --uri="https://bitesize-gen-test-jsrdxhl2pa-ue.a.run.app/generate-questions" \
  --http-method=POST \
  --oidc-service-account-email=generate-mcq@ac215-bitesize.iam.gserviceaccount.com \
  --oidc-token-audience="https://bitesize-gen-test-jsrdxhl2pa-ue.a.run.app" \
  --location=us-east1


gcloud scheduler jobs create http generate-explanations-job \
  --schedule="*/5 * * * *" \
  --uri="https://bitesize-grading-jsrdxhl2pa-ue.a.run.app/generate-explanations" \
  --http-method=POST \
  --oidc-service-account-email=generate-mcq@ac215-bitesize.iam.gserviceaccount.com \
  --oidc-token-audience="https://bitesize-grading-jsrdxhl2pa-ue.a.run.app" \
  --location=us-east1


gcloud scheduler jobs create http extract-text-job \
  --schedule="*/5 * * * *" \
  --uri="https://extract-text-jsrdxhl2pa-ue.a.run.app" \
  --http-method=POST \
  --oidc-service-account-email=generate-mcq@ac215-bitesize.iam.gserviceaccount.com \
  --oidc-token-audience="https://extract-text-jsrdxhl2pa-ue.a.run.app" \
  --location=us-east1
