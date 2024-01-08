// General React
import React, { useState } from "react";
import { Link, useNavigate, useLocation } from 'react-router-dom';

// React-Bootstrap compoonents
import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Form from 'react-bootstrap/Form';
import Card from 'react-bootstrap/Card';
import axios from "axios";

// Custom page
import Finish from './Finish';

// Function
import { getExtractedTextAndSendGradingRequest } from "../interactions/grading_request";

const MCQCard = () => {
  // Recieving data from Upload + accessing data from the state object
  const location = useLocation();
  const data = location.state && location.state.data;
  const questions_mcq = data.MCQ;

  const [userAnswers, setUserAnswers] = useState([]);
  const [questionIndex, setQuestionIndex] = useState(0);
  const totalQuestions = questions_mcq.length;
  const navigate = useNavigate();
  
  // Tracks the user choice as they click, which we take as final at submit
  const thisChoice = {
    current: null,
  }

  // Create an empty JSON, which we will populate in the next (sans selected_options)
  const allAnswers = {
    MCQ : {}
  }

  // Setup the answers JSON
  questions_mcq.forEach((currentQuestion) => {
    // console.log("Current Question:", currentQuestion);
 
    allAnswers["MCQ"] = {
      ...allAnswers["MCQ"],
      [`${currentQuestion.question_text}`]: {
        selected_option: null,
        options: [...currentQuestion.options, `Difficulty: ${currentQuestion.difficulty}`]
      }
    };
  });

  // As they click a choice, update their choice
  const decisionUpdate = (currentChoice) => {
    thisChoice.current = currentChoice.target.value;

  }
  

  const handleAnswer = (event) => {
    setUserAnswers((prevAnswers) => [...prevAnswers, thisChoice.current]);
  
    if (questionIndex + 1 < totalQuestions) {
      setQuestionIndex((prevIndex) => prevIndex + 1);
    } else {
      Object.entries(allAnswers.MCQ).forEach(([question, info], index) => {
        info.selected_option = userAnswers[index];
      });
  
      const UPLOAD_ENDPOINT = 'http://0.0.0.0:8080/upload_answers/';
      axios.post(UPLOAD_ENDPOINT, allAnswers, {
        headers: {
          'Content-Type': 'application/json'
        }
      })
      .then((response) => {
        console.log('Answers uploaded successfully', response);
        // Only call getExtractedTextAndSendGradingRequest after successful upload
        return getExtractedTextAndSendGradingRequest();
      })
      .then(() => {
        // Navigate to /finish after grading is done
        navigate("/finish");
      })
      .catch((error) => {
        console.error("Error processing requests:", error);
        // Handle error scenario (perhaps notify the user)
      });
    }
  };
  

  const currentQuestion = questions_mcq[questionIndex];

  return (
    <Container fluid>
      <Row style={{ padding: 10 }}>
        {questionIndex < totalQuestions ? (
          <Card>
            <Card.Header> Question {questionIndex + 1}</Card.Header>
            <Card.Body>
              <Card.Title>
                <Row className="justify-content-md-center">
                  {/* removes the question number */}
                  <Col md="auto">{currentQuestion.question_text.split(". ")[1]}</Col>
                </Row>
              </Card.Title>
                <Form>
                <fieldset>
                {currentQuestion.options.map((option, index) => (
                  <Form.Group as={Row} className="mb-3">
                    <Col sm={10}>
                     <Form.Check
                      type="radio"
                      name="formHorizontalRadios"
                      id="formHorizontalRadios1"
                      label = {option.split(") ")[1]}
                      // id={`option-${option.split(")")[0]}`}
                      // name="options"
                      value={option.split(") ")[0]}
                      onChange={decisionUpdate}
                      checked = {option.split(") ")[0] === `${thisChoice.current}`}
                    />
                  </Col>
                  </Form.Group>
                  ))}
                  </fieldset>
                </Form>

              <Row className="justify-content-md-center" sytle = {{padding: 10}}>
                  <Button size="sm" variant="primary" onClick={handleAnswer}>Submit</Button>
                </Row>
            </Card.Body>
          </Card>
        ) : (
          <Finish userAnswers={allAnswers} />
        )}
    </Row>
    </Container>
  );
};

export default MCQCard;
