from google.cloud import aiplatform

def check_model_health(project_id, location, endpoint_id):
    """Check the health of the deployed model."""
    
    # Initialize Vertex AI with the given project and location
    aiplatform.init(project=project_id, location=location)
    
    # Retrieve the endpoint details
    endpoint = aiplatform.Endpoint(endpoint_id)
    deployed_models = endpoint.list_models()
    
    # Check if there's at least one deployed model
    if not deployed_models:
        print("No models are deployed to this endpoint!")
        return
    
    # Print details about the deployed models
    for model in deployed_models:
        print(f"Model ID: {model.id}")
        print(f"Model Display Name: {model.display_name}")
        # Removed the traffic_percentage line
        print("==============================================")
    
    # Send a simple prediction request
    test_instance = {"prompt": "Once upon a time,"}
    predictions = endpoint.predict(instances=[test_instance])
    
    if predictions:
        print("Predictions:", predictions)
    else:
        print("Failed to get predictions!")


# Example usage:
project_id = "1033487265630"
location = "us-east1"
endpoint_id = "projects/1033487265630/locations/us-east1/endpoints/8718150841938214912"

check_model_health(project_id, location, endpoint_id)
