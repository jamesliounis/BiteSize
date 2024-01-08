from google.cloud import aiplatform

STAGING_BUCKET = 'gs://hugging-face-models'
PROJECT_ID = 'ac215-bitesize'
LOCATION = 'us-east1'

aiplatform.init(project=PROJECT_ID, staging_bucket=STAGING_BUCKET, location=LOCATION)

DEPLOY_IMAGE = 'gcr.io/ac215-bitesize/llama-optimized:v1.0' 
HEALTH_ROUTE = "/health"
PREDICT_ROUTE = "/isalive"
SERVING_CONTAINER_PORTS = [8080]

model = aiplatform.Model.upload(
    display_name=f'llama2-7b-optimized',    
    description=f'llama2-7B-chat-pruned-and-quantized',
    serving_container_image_uri=DEPLOY_IMAGE,
    serving_container_predict_route=PREDICT_ROUTE,
    serving_container_health_route=HEALTH_ROUTE,
    serving_container_ports=SERVING_CONTAINER_PORTS,
)
print(model.resource_name)

# Retrieve a Model on Vertex
model = aiplatform.Model(model.resource_name)

# Deploy model
endpoint = model.deploy(
    machine_type='n1-standard-4', 
    accelerator_type= "NVIDIA_TESLA_T4",
    accelerator_count = 1,
    traffic_split={"0": 100}, 
    min_replica_count=1,
    max_replica_count=1,
    traffic_percentage=100,
    deploy_request_timeout=1200,
    sync=True,
)
endpoint.wait()