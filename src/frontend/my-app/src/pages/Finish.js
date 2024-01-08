// Import React
import React from 'react';

// Define the QuizFeedback component
const QuizFeedback = ({ quizData }) => {
  // Function to display feedback
  const displayFeedback = (question, isCorrect, feedback) => {
    const feedbackColor = isCorrect ? 'green' : 'red';
    return (
      <div key={question} style={{ margin: '10px 0' }}>
        <p className="question" style={{ fontWeight: 'bold' }}>{question}</p>
        <p style={{ color: feedbackColor }}>{feedback}</p>
      </div>
    );
  };

  // Generate feedback for each question
  const feedbackElements = Object.keys(quizData.MCQ)
    .filter((key) => key !== 'Correct' && key !== 'Grade')
    .map((question) => {
      const index = parseInt(question.split('.')[0]);
      const isCorrect = quizData.MCQ.Correct[index - 1] === 1;
      const feedback = quizData.MCQ[question];
      return displayFeedback(question, isCorrect, feedback);
    });

  // Display overall grade
  const overallGradeStyle = {
    textAlign: 'center',
    fontWeight: 'bold',
    fontSize: '1.5rem', // Adjust the font size as needed
    marginTop: '20px',
  };
  const overallGrade = <p className="grade" style={overallGradeStyle}>Overall Grade: {quizData.MCQ.Grade}%</p>;

  // Render the QuizFeedback component
  return (
    <div style={{ margin: '0 auto', maxWidth: '1000px' }}>
      {feedbackElements}
      {overallGrade}
    </div>
  );
};

// Example usage in a React app
const App = () => {
  // Actual quiz data
  const actualQuizData = {
    'MCQ': {
      '1. What is the main setting of the poem "The Raven"?': 'The correct answer to the question "What is the main setting of the poem \'The Raven\'?" is "a) A chamber door." This is because the poem begins with the narrator sitting in his chamber, pondering and hearing a tapping at his chamber door. The rest of the poem takes place in the same chamber, with the Raven perched above the door.',
      '10. What is the overall mood of the poem?': 'The correct answer is \'c) Melancholic\'. The overall mood of the poem is melancholic because the speaker is filled with sorrow and grief over the loss of his beloved Lenore. The presence of the Raven further adds to the melancholic atmosphere as it symbolizes death and despair. The repetition of the word "Nevermore" also contributes to the melancholic tone of the poem.',
      "2. What is the narrator's initial reaction to the tapping at his chamber door?": "Based on the text, the narrator's initial reaction to the tapping at his chamber door is fear.",
      '3. What is the significance of the word "Nevermore" in the poem?': 'Based on the given text, the correct answer is "b) It represents the narrator\'s lost love, Lenore." The word "Nevermore" is repeatedly spoken by the Raven in response to the narrator\'s questions. The narrator asks if he will ever see his lost love Lenore again, and the Raven\'s response of "Nevermore" signifies that he will never be reunited with her.',
      "4. What does the Raven perch upon in the narrator's chamber?": 'The correct answer is "a) A bust of Pallas." In the text, it is mentioned that the Raven perches upon a bust of Pallas just above the narrator\'s chamber door.',
      "5. What is the narrator's emotional state at the beginning of the poem?": 'Based on the text provided, the correct answer to the question "What is the narrator\'s emotional state at the beginning of the poem?" is \'c) Sad\'. This can be inferred from the lines "Once upon a midnight dreary, while I pondered, weak and weary" and "Eagerly I wished the morrow;—vainly I had sought to borrow From my books surcease of sorrow—sorrow for the lost Lenore". These lines suggest that the narrator is feeling sad and burdened by sorrow.',
      "6. What does the narrator do to try to understand the Raven's meaning?": 'The correct answer is \'a) Engages in guessing\'. This is because in the text, the narrator sits engaged in guessing the meaning of the Raven\'s word "Nevermore". The text states, "This I sat engaged in guessing, but no syllable expressing".',
      "7. What does the Raven's appearance and behavior suggest to the narrator?": 'Based on the given text, the answer "d) It is a sign of impending doom" is correct. The Raven\'s appearance and behavior suggest to the narrator that something ominous and foreboding is about to happen. The Raven\'s presence and its repeated response of "Nevermore" to the narrator\'s questions create a sense of impending doom and despair.',
      '8. What does the narrator hear when he whispers the name "Lenore"?': 'The correct answer is "a) The Raven\'s response." In the text, the narrator whispers the name "Lenore" and the only word spoken in response by the Raven is "Nevermore."',
      '9. What does the narrator find when he opens the shutter?': 'The correct answer to the question "What does the narrator find when he opens the shutter?" is "a) A stately Raven." This is stated in the text: "In there stepped a stately Raven of the saintly days of yore. Not the least obeisance made he; not a minute stopped or stayed he, But, with mien of lord or lady, perched above my chamber door— Perched upon a bust of Pallas just above my chamber door— Perched, and sat, and nothing more."',
      'Correct': [1, 0, 1, 1, 1, 1, 1, 1, 1, 0],
      'Grade': 80.0,
    },
  };

  // Render the QuizFeedback component with the actual quiz data
  return (
    <div>
      <h1 style={{ textAlign: 'center' }}>Quiz Feedback</h1>
      <QuizFeedback quizData={actualQuizData} />
    </div>
  );
};

export default App;
