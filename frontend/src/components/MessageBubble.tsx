import React from 'react';
import styled from 'styled-components';

const MessageContainer = styled.div<{ isUser: boolean }>`
  display: flex;
  justify-content: ${props => props.isUser ? 'flex-end' : 'flex-start'};
  margin-bottom: 8px;
`;

const MessageBubbleStyled = styled.div<{ isUser: boolean }>`
  max-width: 80%;
  padding: 12px 16px;
  border-radius: 18px;
  background: ${props => props.isUser 
    ? '#8ab4f8' 
    : 'rgba(60, 64, 67, 0.8)'
  };
  color: ${props => props.isUser ? '#202124' : '#e8eaed'};
  word-wrap: break-word;
  position: relative;
  backdrop-filter: blur(8px);
  border: 1px solid ${props => props.isUser 
    ? 'transparent' 
    : 'rgba(255, 255, 255, 0.08)'
  };
  font-size: 14px;
  line-height: 1.4;
  font-family: 'Google Sans', sans-serif;
  font-weight: 400;
  
  ${props => props.isUser ? `
    border-bottom-right-radius: 6px;
  ` : `
    border-bottom-left-radius: 6px;
  `}
`;

const MessageInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 6px;
  font-size: 11px;
  color: #9aa0a6;
  font-family: 'Google Sans', sans-serif;
`;

const ConfidenceBadge = styled.span<{ confidence: number }>`
  background: ${props => 
    props.confidence > 0.8 ? '#34a853' : 
    props.confidence > 0.6 ? '#fbbc04' : '#ea4335'
  };
  color: ${props => 
    props.confidence > 0.8 ? 'white' : 
    props.confidence > 0.6 ? '#202124' : 'white'
  };
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 500;
  font-family: 'Google Sans', sans-serif;
`;

const FallbackBadge = styled.span`
  background: #6c757d;
  color: white;
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 600;
`;

interface MessageBubbleProps {
  message: string;
  isUser: boolean;
  timestamp: Date;
  confidence?: number;
  fallback?: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isUser,
  timestamp,
  confidence,
  fallback
}) => {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <MessageContainer isUser={isUser}>
      <div>
        <MessageBubbleStyled isUser={isUser}>
          {message}
        </MessageBubbleStyled>
        <MessageInfo>
          <span>{formatTime(timestamp)}</span>
          {!isUser && confidence !== undefined && (
            <ConfidenceBadge confidence={confidence}>
              {Math.round(confidence * 100)}% confident
            </ConfidenceBadge>
          )}
          {!isUser && fallback && (
            <FallbackBadge>
              Fallback response
            </FallbackBadge>
          )}
        </MessageInfo>
      </div>
    </MessageContainer>
  );
};

export default MessageBubble;
