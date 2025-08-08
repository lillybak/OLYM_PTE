import React, { useState, useEffect } from 'react';
import './App.css';
import TopicInput from './TopicInput';

interface MCQ {
  question: string;
  choices: string[];
  correct: number;
  explanations: Record<number, string>;
  links: Record<number, string[]>;
}

const App: React.FC = () => {
  const [selected, setSelected] = useState<number | null>(null);
  const [randomNumber, setRandomNumber] = useState<number | null>(null);
  const [mcq, setMcq] = useState<MCQ | null>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/random')
      .then((res) => res.json())
      .then((data) => setRandomNumber(data.number))
      .catch(() => setRandomNumber(null));
  }, []);

  const handleQuestionReceived = (newMcq: MCQ) => {
    setMcq(newMcq);
    setSelected(null);
  };

  const handleSelect = (idx: number) => {
    setSelected(idx);
  };

  return (
    <div className="center-container">
      <h1>NPTE Practice Questions</h1>
      <TopicInput onQuestionReceived={handleQuestionReceived} onTopicSelected={() => {}} />
      {mcq && (
        <div className="question-container">
          <div className="question-text">
            {mcq.question}
          </div>
          <div className="choices-container">
            {mcq.choices.map((choice, idx) => {
              let btnClass = 'choice-btn';
              if (selected !== null) {
                if (idx === selected && idx === mcq.correct) btnClass += ' selected';
                else if (idx === selected && idx !== mcq.correct) btnClass += ' incorrect';
                else if (idx === mcq.correct) btnClass += ' correct';
              }
              return (
                <button
                  key={choice}
                  onClick={() => handleSelect(idx)}
                  className={btnClass}
                  disabled={selected !== null}
                  style={{ display: 'flex', alignItems: 'center' }}
                >
                  <span style={{ fontWeight: 'bold', marginRight: 12 }}>{idx + 1}.</span> {choice}
                </button>
              );
            })}
          </div>
          {selected !== null && (
            <div style={{ marginTop: '1.5rem' }}>
              <div className={`feedback ${selected === mcq.correct ? 'correct' : 'incorrect'}`}>
                {mcq.explanations[selected]}
              </div>
              {selected !== mcq.correct && mcq.links[selected] && mcq.links[selected].length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <strong>Learn more:</strong>
                  <ul>
                    {mcq.links[selected].map((url, i) => (
                      <li key={url + i}>
                        <a href={url} target="_blank" rel="noopener noreferrer">{url}</a>
                      </li>
                    ))}
                  </ul>
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