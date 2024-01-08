docker build -t extract-text:v1 .

docker tag extract-text gcr.io/ac215-bitesize/extract-text:v1

docker push gcr.io/ac215-bitesize/extract-text:v1

#gcloud builds submit --tag gcr.io/ac215-bitesize/extract-text

gcloud run deploy extract-text --image gcr.io/ac215-bitesize/extract-text:v1 --platform managed --region us-east1 --allow-unauthenticated --cpu 1 --max-instances 10

