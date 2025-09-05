import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
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
  study_links?: string[];
  study_message?: string;
}

const App: React.FC = () => {
  const [selected, setSelected] = useState<number | null>(null);
  const [mcq, setMcq] = useState<MCQ | null>(null);
  const [currentTopic, setCurrentTopic] = useState<string>('');
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [answerValidation, setAnswerValidation] = useState<AnswerValidation | null>(null);
  const [loading, setLoading] = useState(false);
  const [questionGenerating, setQuestionGenerating] = useState(false);
  const [evaluating, setEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearQuestionContainer = () => {
    setMcq(null);
    setSelected(null);
    setSessionId(null);
    setAnswerValidation(null);
    setError(null);
    setQuestionGenerating(false);
    setEvaluating(false);
  };

  const handleQuestionReceived = (newMcq: MCQ, newSessionId: string) => {
    console.log('Received MCQ:', newMcq);
    console.log('Session ID:', newSessionId);
    console.log('Choices count:', newMcq.choices.length);
    setMcq(newMcq);
    setSessionId(newSessionId);
    setSelected(null);
    setAnswerValidation(null);
    setError(null); // Clear any previous errors
    setQuestionGenerating(false); // End generation process - ready for interaction
  };

  const handleQuestionStart = () => {
    setQuestionGenerating(true);
  };

  // Removed complex timing effect - now using simpler evaluating state

  const handleSelect = async (idx: number) => {
    console.log('Answer selected:', idx);
    setSelected(idx);
    setLoading(true);
    setEvaluating(true);
    
    try {
      // Call the NEW /api/evaluate endpoint with contextual learning materials
      const response = await fetch('/api/evaluate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId || 'default-session',  // Use stored session ID
          user_answer_index: idx
        }),
      });

      if (!response.ok) {
        throw new Error(`Evaluation failed: ${response.statusText}`);
      }

      const evalResult = await response.json();
      console.log('🎯 Evaluation result:', evalResult);
      
      const validation: AnswerValidation = {
        correct: evalResult.is_correct,
        explanation: evalResult.explanation,
        suggest_same_topic: !evalResult.is_correct,
        mastery_level: evalResult.is_correct ? 0.8 : 0.2,
        study_links: evalResult.study_links || [],
        study_message: evalResult.study_message || ''
      };

      setAnswerValidation(validation);
      setError(null);
      setEvaluating(false);
      setQuestionGenerating(false);
    } catch (error) {
      console.error('❌ Evaluation failed:', error);
      setError(`Failed to evaluate answer: ${error}`);
      setEvaluating(false);
      setQuestionGenerating(false);
    } finally {
      setLoading(false);
    }
  };

  const handleTopicSelected = (topic: string) => {
    setCurrentTopic(topic);
  };

  const handleSameTopic = async () => {
    if (!currentTopic) return;
    
    // Clear the question container before making the API request
    clearQuestionContainer();
    setQuestionGenerating(true); // Start generation process
    
    setLoading(true);
    try {
      const response = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: currentTopic }),
      });
      
      if (response.ok) {
        const newMcq = await response.json();
        console.log('🔄 Same topic MCQ received:', newMcq);
        console.log('🔄 New session ID:', newMcq.session_id);
        
        // Reset all states before setting the new MCQ
        setSelected(null);
        setAnswerValidation(null);
        setError(null);
        setMcq(newMcq);
        setSessionId(newMcq.session_id);  // ← FIX: Update session ID!
        setQuestionGenerating(false); // End generation process
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
      <h2>NPTE-Practice-Learn-Excel!</h2>
      <TopicInput 
        onQuestionReceived={handleQuestionReceived} 
        onTopicSelected={handleTopicSelected}
        onClearContainer={clearQuestionContainer}
        onQuestionStart={handleQuestionStart}
        disabled={loading}
        externalLoading={questionGenerating}
        evaluating={evaluating}
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
          
          {evaluating && (
            <div style={{ marginTop: '1rem', textAlign: 'center', color: '#666', fontStyle: 'italic' }}>
              🤔 Analyzing your answer and finding learning materials...
            </div>
          )}
          
          {answerValidation && (
            <div style={{ marginTop: '1.5rem' }}>
              <div className={`feedback ${answerValidation.correct ? 'correct' : 'incorrect'}`}
                   style={{ textAlign: 'left' }}>
                <ReactMarkdown>{answerValidation.explanation}</ReactMarkdown>
              </div>
              
              {answerValidation.study_links && answerValidation.study_links.length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  {answerValidation.study_message && (
                    <div style={{ marginBottom: '0.5rem', fontWeight: 'bold', color: '#2563eb' }}>
                      {answerValidation.study_message}
                    </div>
                  )}
                  <strong>📚 Learning Materials:</strong>
                  <ul style={{ marginTop: '0.5rem' }}>
                    {answerValidation.study_links.map((url, i) => {
                      // Check if this is a PDF reference (non-clickable)
                      const isPdfReference = url.includes('Please research this paper:');
                      
                      return (
                        <li key={url + i} style={{ marginBottom: '0.25rem' }}>
                          {isPdfReference ? (
                            <span style={{ color: '#059669', fontStyle: 'italic' }}>
                              {url}
                            </span>
                          ) : (
                            <a href={url} target="_blank" rel="noopener noreferrer" 
                               style={{ color: '#2563eb', textDecoration: 'underline' }}>
                              {url.length > 60 ? url.substring(0, 60) + '...' : url}
                            </a>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                </div>
              )}
              
              {answerValidation.suggest_same_topic && (
                <div style={{ marginTop: '1rem' }}>
                  <button 
                    onClick={handleSameTopic}
                    disabled={loading || questionGenerating || evaluating}
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: (loading || questionGenerating || evaluating) ? 'not-allowed' : 'pointer'
                    }}
                  >
                    {(loading || questionGenerating) ? 'Generating...' : 'Try Another Question (Same Topic)'}
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