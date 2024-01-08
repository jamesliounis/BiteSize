// General react things
import React, { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import axios from "axios";
import Button from 'react-bootstrap/Button'

// Dropdown option for TestType, ring loader
import TestType from "../components/TestType"
import Loading from "../components/Loading";

// Custom style for this page 
import "../css/Upload.css"; 
// General thematic styles
import "../css/index.css"

import { getExtractedTextAndSendRequest } from "../interactions/question_gen_request";

function Upload() {
  const fileInputRef = useRef(null);
  const [pdfFile, setPdfFile] = useState(null);
  const [numberOfQuestions, setNumberOfQuestions] = useState('');
  const [testType, setTestType] = useState('');
  const [error, setError] = useState('');
  const testValue = '1';
  const navigate = useNavigate();

  // Saves the pdf in "file" on upload
  const handleFileUpload = () => {
    const file = fileInputRef.current.files[0];
    setPdfFile(URL.createObjectURL(file));
  };

  // Opens document selector on local machine to upload a document 
  const openFilePicker = () => {
    // Click on the button to start the upload
    fileInputRef.current.click(); 
  };

  // Ensures the number of questions we have is correct
  const handleInputChange = (e, setState) => {
    const value = e.target.value;

    // Validate that the entered value is a positive number
    if (setState === setNumberOfQuestions && (isNaN(value) || parseInt(value) <= 0)) {
      setError('To generate a test, we need a number greater than 0!');
    } else {
      setError('');
    }

    // Update the state
    setState(value);
  };

  const handleButtonClick = () => {
    // Check for validation errors before proceeding
    if (error) {
      alert('Please fix the error before proceeding.');
      return;
    }

    // replace the start test with loading spinner and remove the upload button
    document.getElementById('startTest').style.display = "none";
    document.getElementById('uploadButton').style.display = "none";
    document.getElementById('loadingWheel').style.display = "block";
    
    // Send the file to the backend
    console.log("Sending file...");
    const UPLOAD_ENDPOINT = 'http://0.0.0.0:8080/upload/';
    const formData = new FormData();
    formData.append('file', fileInputRef.current.files[0]);
    axios.post(UPLOAD_ENDPOINT, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }

    }).then((response) => {
      console.log(response);

    }).then(response => {
      // this doesn't actually do anything, but it waits for the response before doing the post request
          // Send POST request to backend with the file to get the questions
      console.log("Sending POST request...");
      getExtractedTextAndSendRequest(testValue)
      .then(data => {
        // Depending on the choice the user made with the dropdown, route to the correct test
        if (testType === '1') {
          navigate("/mcqcard", { state: { data } });

        } else if (testType === '2') {
          navigate("/sacard");

        } else{
          // maybe an alert or something

        }

      })

    }).catch((error) => {
      console.log(error);
      
    });

  };

  const handleTestTypeChange = (selectedValue) => {
    // Update the state with the selected value
    setTestType(selectedValue);
  };

  return (
    <Container fluid>
      <Row style = {{padding: 10}}>
        <Col>
          {/* <label className="text-mid_page1" htmlFor="numberOfQuestions">
              Number of Questions
            </label>
            <input
              type="number"
              id="numberOfQuestions"
              className="text-mid_page1"
              value={numberOfQuestions}
              onChange={(e) => handleInputChange(e, setNumberOfQuestions)}
            />
            {error && <p className="error">{error}</p>} */}

          <TestType onTestTypeChange={handleTestTypeChange} />
        </Col>
        <Col>
          {/* Your image */}
          <img src="upload.png" alt="Upload" className="upload-image" />

          {/* Button to open file picker */}
          <Button id = "uploadButton" className="text-mid_page1 rb-button" onClick={openFilePicker}>
            Upload Doc
          </Button>
          {/* Hidden file input */}
          <input
            type="file"
            id="fileUpload"
            onChange={handleFileUpload}
            ref={fileInputRef}
            style={{ display: "none" }}
          />
        </Col>
      </Row>
      <Row className="justify-content-md-center" style = {{padding: 10}}>
        <Col md = "auto">
          {/* PDF Viewer */}
          {pdfFile && (
            <div className="pdf-viewer">
              <iframe title="PDF Preview" width="120%" height="80%" src={pdfFile} />
            </div>
          )}
        </Col>
      </Row>
      <Row style = {{padding: 10}}>
        {pdfFile && (
          <Button id = "startTest" className="text-mid_page1 rb-button" onClick={handleButtonClick}>
            Start Test
          </Button>
        )}
      </Row>
      <Row className="justify-content-md-center">
      <Col md = "auto">
        <div id = "loadingWheel" style = {{display: "none"}}>
          <Loading/>
        </div>
      </Col>
      </Row>
    </Container>

  );
}

export default Upload;
