import Card from 'react-bootstrap/Card';

function TCard({ name, email, imageSrc }) {
  return (
    <Card style={{ width: '18rem' }}>
      <Card.Img variant="top" src={imageSrc} />
      <Card.Body>
        <Card.Title>{name}</Card.Title>
        <Card.Text>
          {email}
        </Card.Text>
      </Card.Body>
    </Card>
  );
}

export default TCard;