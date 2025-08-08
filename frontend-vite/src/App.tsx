import React, { useState } from 'react';
import './App.css';
import TopicInput from './TopicInput';

interface MCQ {
  question: string;
  choices: string[];
  correct: number;
  explanations: Record<number, string>;
  links: Record<number, string[]>;
}

interface AnswerValidation {
  correct: boolean;
  explanation: string;
  suggest_same_topic: boolean;
  mastery_level: number;
}

const App: React.FC = () => {
  const [selected, setSelected] = useState<number | null>(null);
  const [mcq, setMcq] = useState<MCQ | null>(null);
  const [currentTopic, setCurrentTopic] = useState<string>('');
  const [answerValidation, setAnswerValidation] = useState<AnswerValidation | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearQuestionContainer = () => {
    setMcq(null);
    setSelected(null);
    setAnswerValidation(null);
    setError(null);
  };

  const handleQuestionReceived = (newMcq: MCQ) => {
    console.log('Received MCQ:', newMcq);
    console.log('Choices count:', newMcq.choices.length);
    setMcq(newMcq);
    setSelected(null);
    setAnswerValidation(null);
    setError(null); // Clear any previous errors
  };

  const handleSelect = async (idx: number) => {
    console.log('Answer selected:', idx);
    setSelected(idx);
    setLoading(true);
    
    // Client-side validation using MCQ data
    const isCorrect = idx === mcq?.correct;
    
    // Build comprehensive explanation
    let explanation = '';
    if (isCorrect) {
      explanation = `✅ Correct! ${mcq?.explanations?.[idx] || 'This is the right answer.'}`;
    } else {
      explanation = `❌ Incorrect. ${mcq?.explanations?.[idx] || 'This is not the correct answer.'} `;
      explanation += `The correct answer is: ${mcq?.choices?.[mcq.correct] || 'Unknown'}. `;
      explanation += `${mcq?.explanations?.[mcq.correct] || 'Please review this topic.'}`;
    }
    
    const validation: AnswerValidation = {
      correct: isCorrect,
      explanation: explanation,
      suggest_same_topic: !isCorrect, // Suggest same topic if wrong
      mastery_level: isCorrect ? 0.8 : 0.2 // Simple mastery calculation
    };
    
    setAnswerValidation(validation);
    setError(null);
    setLoading(false);
  };

  const handleTopicSelected = (topic: string) => {
    setCurrentTopic(topic);
  };

  const handleSameTopic = async () => {
    if (!currentTopic) return;
    
    // Clear the question container before making the API request
    clearQuestionContainer();
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: currentTopic }),
      });
      
      if (response.ok) {
        const newMcq = await response.json();
        // Reset all states before setting the new MCQ
        setSelected(null);
        setAnswerValidation(null);
        setError(null);
        setMcq(newMcq);
      } else {
        const errorText = await response.text();
        console.error('HTTP Error:', response.status, errorText);
        setError(`Server Error (${response.status}): ${errorText}`);
      }
    } catch (error) {
      console.error('Network error:', error);
      setError('Network error: Unable to connect to server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="center-container">
      <h2>NPTE MCQ Demo</h2>
      <TopicInput 
        onQuestionReceived={handleQuestionReceived} 
        onTopicSelected={handleTopicSelected}
        onClearContainer={clearQuestionContainer}
        disabled={loading}
      />
      
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}
      
      {mcq && (
        <div className="question-container">
          <div className="question-text">
            {mcq.question}
          </div>
          <div className="choices-container">
            {mcq.choices.map((choice, idx) => {
              let btnClass = 'choice-btn';
              if (selected !== null) {
                if (idx === selected && idx === mcq.correct) {
                  btnClass += ' correct'; // User selected correct answer
                } else if (idx === selected && idx !== mcq.correct) {
                  btnClass += ' incorrect'; // User selected wrong answer
                } else if (idx === mcq.correct) {
                  btnClass += ' correct'; // Show correct answer
                }
              }
              return (
                <button
                  key={choice}
                  onClick={() => handleSelect(idx)}
                  className={btnClass}
                  disabled={selected !== null || loading}
                  style={{ display: 'flex', alignItems: 'center' }}
                >
                  {choice}
                </button>
              );
            })}
          </div>
          
          {answerValidation && (
            <div style={{ marginTop: '1.5rem' }}>
              <div className={`feedback ${answerValidation.correct ? 'correct' : 'incorrect'}`}>
                {answerValidation.explanation}
              </div>
              
              {!answerValidation.correct && mcq.links[selected!] && mcq.links[selected!].length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <strong>Learn more:</strong>
                  <ul>
                    {mcq.links[selected!].map((url, i) => (
                      <li key={url + i}>
                        <a href={url} target="_blank" rel="noopener noreferrer">{url}</a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {answerValidation.suggest_same_topic && (
                <div style={{ marginTop: '1rem' }}>
                  <button 
                    onClick={handleSameTopic}
                    disabled={loading}
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: loading ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {loading ? 'Generating...' : 'Try Another Question (Same Topic)'}
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default App;