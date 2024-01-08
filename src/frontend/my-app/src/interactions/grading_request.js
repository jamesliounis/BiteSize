export function getExtractedTextAndSendGradingRequest() {
  // Step 1: Make a GET request to the Flask app to retrieve the extracted text
  fetch('https://bitesize-question-gen-matz6gu77q-ue.a.run.app/extract-text')
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      else{
        console.log('Initial response OK')
      }
      
      return response.json();
    })
    .then(data => {
      const extractedText = data.document_text.join("\n");
      const userAnswers = getUserAnswers();

      // Step 2: Construct the payload with the extracted text and user answers
      const payload = {
        text: extractedText,
        user_answers: userAnswers,
      };

      // Step 3: Make a POST request to the bitesize-grading service with the payload
      const gradingUrl = "https://bitesize-grading-matz6gu77q-ue.a.run.app/generate-explanations";
      return fetch(gradingUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      else{
        console.log('Generate Explantions OK')
      }
      return response.json();
    })
    .then(data => {
      console.log(data);
      // Handle the response data here
      
      // Step 4: Delete the contents of the bucket now that grading is done
      const bucketUrl = "https://bitesize-grading-matz6gu77q-ue.a.run.app/empty-bucket";
      return fetch(bucketUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          bucket_name: "bitesize-documents-2",
          folder_name: "documents_to_be_summarized"
        }),
      });
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Failed to empty the bucket');
      }
      console.log('Bucket contents deleted successfully');
    })
    .catch(error => {
      console.error('Error:', error);
    });
}

function getUserAnswers() {
  fetch('https://bitesize-grading-matz6gu77q-ue.a.run.app/get-user-answers')
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
   return data;
  })

}
