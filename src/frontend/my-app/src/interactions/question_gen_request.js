export function getExtractedTextAndSendRequest(userChoice) {
  return new Promise((resolve, reject) => {
    // Step 1: Make a GET request to the Flask app to retrieve the extracted text
    fetch('https://bitesize-question-gen-matz6gu77q-ue.a.run.app/extract-text')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        
        }
        console.log("getExtractedTextAndSendRequest extract-text response OK!")
        return response.json();

      })
      .then(data => {
        // Assuming response has a "document_text" key with the extracted text
        const extractedText = data.document_text.join("\n");

        // Construct payload with extracted text and user choice
        const payload = {
          text: extractedText,
          choice: userChoice,

        };

        // Make POST request to Cloud Run service with payload
        const url = "https://bitesize-question-gen-matz6gu77q-ue.a.run.app/generate-questions";
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
        console.log("getExtractedTextAndSendRequest generate-questions response OK!")
        return response.json();

      })
      .then(data => {
        console.log(data);
        resolve(data);

      })
      .catch(error => {
        console.error('Error:', error);
        reject(error);

      });
  });
}
