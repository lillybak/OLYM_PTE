import React, { useState } from 'react';

interface MCQ {
  question: string;
  choices: string[];
  correct: number;
  explanations: Record<number, string>;
  links: Record<number, string[]>;
}

interface TopicInputProps {
  onQuestionReceived: (mcq: MCQ) => void;
}

const TOPICS = [
  "Cardiovascular and pulmonary systems",
  "Musculoskeletal system",
  "Neuromuscular and nervous systems",
  "Integumentary system",
  "Metabolic and endocrine systems",
  "Gastrointestinal system",
  "Genitourinary system",
  "Lymphatic system",
  "System interactions"
];

const TopicInput: React.FC<TopicInputProps> = ({ onQuestionReceived }) => {
  const [topic, setTopic] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic || topic === '') return;
    setLoading(true);
    setError('');
    try {
      const response = await fetch('http://localhost:8000/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: topic }),
      });
      if (!response.ok) throw new Error('Backend error');
      const data = await response.json();
      onQuestionReceived(data);
      setTopic(''); // Reset to empty after submission
    } catch (err) {
      setError('Failed to fetch MCQ from backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
      <div style={{ marginBottom: '0.5rem', color: '#666', fontSize: '0.9rem' }}>
        Please select one of the 9 NPTE topics
      </div>
      <select
        value={topic}
        onChange={e => setTopic(e.target.value)}
        style={{ padding: '0.5rem', width: '350px', marginRight: '1rem' }}
      >
        <option value="">Select a topic...</option>
        {TOPICS.map((t) => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>
      <button type="submit" disabled={loading || !topic}>
        {loading ? 'Generating...' : 'Get MCQ'}
      </button>
      {error && <div style={{ color: 'red', marginTop: '0.5rem' }}>{error}</div>}
    </form>
  );
};

export default TopicInput;