function getExtractedTextAndSendRequest(userChoice) {
  // Step 1: Make a GET request to the Flask app to retrieve the extracted text
  fetch('https://bitesize-question-gen-jsrdxhl2pa-ue.a.run.app/extract-text')
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // Assuming the response has a "document_text" key with the extracted text
      const extractedText = data.document_text.join("\n");

      // Step 2: Construct the payload with the extracted text and user choice
      const payload = {
        text: extractedText,
        choice: userChoice, // This should be provided by the user in your app
      };

      // Step 3: Make a POST request to the Cloud Run service with the payload
      const url = "https://bitesize-question-gen-jsrdxhl2pa-ue.a.run.app/generate-questions";
      return fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log(data);
      // Handle the response from the Cloud Run service here
      // This is where you would update the UI with the questions and answers
    })
    .catch(error => {
      console.error('Error:', error);
      // Handle any errors that occurred during the fetch here
    });
}

// Example usage: this function can be called when the user submits their choice
// getExtractedTextAndSendRequest('2');
