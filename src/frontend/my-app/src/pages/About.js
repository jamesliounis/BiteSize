// Our pictures and emails, missiong statement (from the proposal)
import React from "react";
import TCard from "../components/TCard"
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';


const About = () => {
  const teamMembers = [
    { name: "James Liounis", email: "jamesliounis@g.harvard.edu", imageSrc: "james.jpg" },
    { name: "Hope Neveux", email: "hopeneveux@g.harvard.edu", imageSrc: "hope.jpg" },
    { name: "Kimberly Llajaruna Peralta", email: "kllajarunaperalta@g.harvard.edu", imageSrc: "kim.jpg" },
    { name: "Michael Sam Chec", email: "msamchec@g.harvard.edu", imageSrc: "michael.jpg" },
  ];

  return (
    <Container fluid>
      <Row style = {{padding: 10}}>
        {/* TODO: Add in an "Our Mission" section here */}
          <h1 style ={{textAlign: 'center'}}>Team Members</h1>
      </Row>
      <Row style = {{padding: 10}}>
        <Col>
          <TCard name={teamMembers[0].name} email={teamMembers[0].email} imageSrc ={teamMembers[0].imageSrc}/>
        </Col>
        <Col>
          <TCard name={teamMembers[1].name} email={teamMembers[1].email} imageSrc ={teamMembers[1].imageSrc}/>
        </Col>
        <Col>
          <TCard name={teamMembers[2].name} email={teamMembers[2].email} imageSrc ={teamMembers[2].imageSrc}/>
        </Col>
        <Col>
          <TCard name={teamMembers[3].name} email={teamMembers[3].email} imageSrc ={teamMembers[3].imageSrc}/>
        </Col>
      </Row>
    </Container>
  );
};

export default About;