import React from 'react';
import styled from 'styled-components';
import { Source } from '../api/chatAPI';

const SourceContainer = styled.div`
  background: rgba(60, 64, 67, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 12px 16px;
  margin: 6px 0;
  font-size: 13px;
  backdrop-filter: blur(8px);
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
  
  &:hover {
    background: rgba(60, 64, 67, 0.8);
    border-color: rgba(255, 255, 255, 0.12);
  }
`;

const SourceHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  gap: 8px;
`;

const SourceTitle = styled.span`
  font-weight: 500;
  color: #e8eaed;
  flex: 1;
  font-family: 'Google Sans', sans-serif;
  font-size: 13px;
`;

const SourceMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SourceType = styled.span`
  background: rgba(138, 180, 248, 0.2);
  color: #8ab4f8;
  border: 1px solid rgba(138, 180, 248, 0.3);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  text-transform: uppercase;
  font-weight: 500;
  font-family: 'Google Sans', sans-serif;
`;

const ConfidenceScore = styled.span`
  font-size: 11px;
  color: #9aa0a6;
  font-weight: 500;
  font-family: 'Google Sans', sans-serif;
`;

const TicketInfo = styled.div`
  color: #9aa0a6;
  font-size: 12px;
  margin-top: 4px;
  font-family: 'Google Sans', sans-serif;
`;

interface SourceCardProps {
  source: Source;
}

const SourceCard: React.FC<SourceCardProps> = ({ source }) => {
  const getTypeIcon = (sourceType: string) => {
    switch (sourceType) {
      case 'pdf': return '📄';
      case 'docx': return '📝';
      case 'txt': return '📃';
      case 'md': return '📋';
      case 'zendesk': return '🎫';
      default: return '📁';
    }
  };

  return (
    <SourceContainer>
      <SourceHeader>
        <SourceTitle>
          {getTypeIcon(source.source_type)} {source.doc_title}
        </SourceTitle>
        <SourceMeta>
          <SourceType>{source.source_type}</SourceType>
          <ConfidenceScore>
            {Math.round(source.confidence * 100)}%
          </ConfidenceScore>
        </SourceMeta>
      </SourceHeader>
      
      {source.section && (
        <div style={{ color: '#9aa0a6', fontSize: '12px', fontFamily: 'Google Sans, sans-serif' }}>
          Section: {source.section}
        </div>
      )}
      
      {source.ticket_id && (
        <TicketInfo>
          Ticket #{source.ticket_id}
        </TicketInfo>
      )}
    </SourceContainer>
  );
};

export default SourceCard;
