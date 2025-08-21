import React, { useState } from 'react';
import styled from 'styled-components';

const FeedbackContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 8px;
`;

const FeedbackButton = styled.button<{ active?: boolean }>`
  background: ${props => props.active ? '#007bff' : 'transparent'};
  color: ${props => props.active ? 'white' : '#6c757d'};
  border: 1px solid ${props => props.active ? '#007bff' : '#dee2e6'};
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;

  &:hover {
    background: ${props => props.active ? '#0056b3' : '#e9ecef'};
  }
`;

const FeedbackText = styled.span`
  font-size: 12px;
  color: #6c757d;
`;

const FeedbackInput = styled.textarea`
  width: 100%;
  margin-top: 8px;
  padding: 8px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 12px;
  resize: vertical;
  min-height: 60px;
`;

const SubmitButton = styled.button`
  background: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  margin-top: 8px;

  &:hover {
    background: #218838;
  }

  &:disabled {
    background: #6c757d;
    cursor: not-allowed;
  }
`;

interface FeedbackButtonsProps {
  onFeedback: (rating: number, feedbackText?: string) => void;
}

const FeedbackButtons: React.FC<FeedbackButtonsProps> = ({ onFeedback }) => {
  const [rating, setRating] = useState<number | null>(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [showInput, setShowInput] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleRating = (newRating: number) => {
    setRating(newRating);
    if (newRating <= 3) {
      setShowInput(true);
    } else {
      // For positive ratings, submit immediately
      onFeedback(newRating);
      setSubmitted(true);
    }
  };

  const handleSubmitFeedback = () => {
    if (rating) {
      onFeedback(rating, feedbackText || undefined);
      setSubmitted(true);
    }
  };

  if (submitted) {
    return (
      <FeedbackContainer>
        <FeedbackText>Thank you for your feedback!</FeedbackText>
      </FeedbackContainer>
    );
  }

  return (
    <FeedbackContainer>
      <FeedbackText>Was this helpful?</FeedbackText>
      
      <FeedbackButton
        active={rating === 1}
        onClick={() => handleRating(1)}
        title="Poor"
      >
        👎
      </FeedbackButton>
      
      <FeedbackButton
        active={rating === 2}
        onClick={() => handleRating(2)}
        title="Fair"
      >
        😐
      </FeedbackButton>
      
      <FeedbackButton
        active={rating === 3}
        onClick={() => handleRating(3)}
        title="Good"
      >
        🙂
      </FeedbackButton>
      
      <FeedbackButton
        active={rating === 4}
        onClick={() => handleRating(4)}
        title="Very Good"
      >
        😊
      </FeedbackButton>
      
      <FeedbackButton
        active={rating === 5}
        onClick={() => handleRating(5)}
        title="Excellent"
      >
        👍
      </FeedbackButton>

      {showInput && rating && rating <= 3 && (
        <div style={{ width: '100%' }}>
          <FeedbackInput
            placeholder="Please tell us how we can improve..."
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
          />
          <SubmitButton
            onClick={handleSubmitFeedback}
            disabled={!rating}
          >
            Submit Feedback
          </SubmitButton>
        </div>
      )}
    </FeedbackContainer>
  );
};

export default FeedbackButtons;
