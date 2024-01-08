import React, { useState } from 'react';
import Form from 'react-bootstrap/Form';

function TestType({ onTestTypeChange }) {
  const [selectedValue, setSelectedValue] = useState('');

  const handleSelectChange = (e) => {
    const value = e.target.value;
    setSelectedValue(value);
    // Call the callback function passed from the parent component
    onTestTypeChange(value);
  };

  return (
    <Form.Select
      aria-label="Default select example"
      value={selectedValue}
      onChange={handleSelectChange}
    >
      <option>Select Test Type</option>
      <option value="1">Multiple Choice</option>
      {/* <option value="2">Short Answer</option> */}
    </Form.Select>
  );
}

export default TestType;
