import requests
import json

# Define the URL for the Flask application's endpoint to get user answers
get_user_answers_api_url = "https://bitesize-grading-jsrdxhl2pa-ue.a.run.app/get-user-answers"
# Define the URL for the Flask application's endpoint to extract text
extract_text_api_url = "https://bitesize-grading-jsrdxhl2pa-ue.a.run.app/extract-text"
# Define the URL for the Flask application's endpoint to generate explanations
generate_explanations_api_url = "https://bitesize-grading-jsrdxhl2pa-ue.a.run.app/generate-explanations"

# Make a GET request to retrieve user answers
user_answers_response = requests.get(get_user_answers_api_url)

# Check if the request to get user answers was successful
if user_answers_response.status_code == 200:
    # Extract user answers data from the response
    user_answers = user_answers_response.json()
    
    # Make a GET request to the extract-text endpoint to get the parsed texts
    get_response = requests.get(extract_text_api_url)
    
    # Check if the GET request to extract text was successful
    if get_response.status_code == 200:
        # Extract the text data from the response
        parsed_texts = get_response.json().get('document_text', [])
        
        # Define the request payload using the extracted text and user answers
        payload = {
            "text": "\n".join(parsed_texts),  # Combine text from all files
            "user_answers": user_answers
        }
        
        # Send the POST request to the generate-explanations endpoint
        post_response = requests.post(generate_explanations_api_url, json=payload)
        
        # Check the response status code for the POST request
        if post_response.status_code == 200:
            # Print the JSON response with explanations
            response_data = post_response.json()
            print(json.dumps(response_data, indent=4))
        else:
            print(f"Error in POST request: {post_response.status_code} - {post_response.text}")
    else:
        print(f"Error in GET request to extract text: {get_response.status_code} - {get_response.text}")
else:
    print(f"Error in GET request to get user answers: {user_answers_response.status_code} - {user_answers_response.text}")
