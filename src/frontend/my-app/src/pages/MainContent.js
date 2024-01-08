// MainContent.js
import React from 'react';
import { Link } from 'react-router-dom';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Button from 'react-bootstrap/Button'

import '../css/index.css'


const MainContent = () => {
  return (
    <Container fluid>
      <Row style = {{padding: 10}}>
        <h1 style = {{textAlign: 'center'}}>Learning material in Bitesize chunks</h1>
      </Row>
      <Row className="justify-content-md-center" style = {{padding: 10}}>
        <Col md="auto">
          <img style={{ width: 200, height: 'auto'}} src="paper.png" alt="Paper"/>
        </Col>
      </Row>
      <Row style = {{padding: 10}}>
        <h1 style = {{textAlign: 'center'}}>Handouts, lectures, and general pats transformed into customizable mini-tests</h1>
      </Row>
      <Row className="justify-content-md-center" style = {{padding: 10}}>
        <Col md="auto">
          <Link to="/upload">
            {/* <button>Let's Go!</button> */}
            <Button className='rb-button'>Let's Go!</Button>
          </Link>
        </Col>
      </Row>
      <Row style = {{padding: 10}}>
        <footer className="footer">
          <p className="text-footer">
            Copyright ©-All rights are reserved
          </p>
        </footer>
      </Row>
    </Container>

  );
};

export default MainContent;
