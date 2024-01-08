// General react
import React from "react";

// React bootstrap
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import Form from 'react-bootstrap/Form';
import InputGroup from 'react-bootstrap/InputGroup';


const SACard = () => {

  const question = "What is the name of the North Star?"

  return (
    <Container fluid>
      <Row style = {{padding: 10}}>
        <Card>
          <Card.Header>Question</Card.Header>
          <Card.Body>
            <Card.Title>
              <Row className = "justify-content-md-center">
                <Col md = "auto">
                  {question}
                </Col>
              </Row>
            </Card.Title>
            <Form>
            <InputGroup>
              <InputGroup.Text>Response</InputGroup.Text>
              <Form.Control as="textarea" aria-label="With textarea" />
            </InputGroup>

            <Form.Group as={Row } className="mb-3 justify-content-md-center">
              <Col md = "auto">
                <Button type="submit">Submit</Button>
              </Col>
            </Form.Group>
          </Form>
          </Card.Body>
        </Card>
      </Row>
    </Container>
  );
};

export default SACard;