import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { chatAPI, ChatResponse, Source } from '../api/chatAPI';
import MessageBubble from './MessageBubble';
import SourceCard from './SourceCard';
import FeedbackButtons from './FeedbackButtons';
import { v4 as uuidv4 } from 'uuid';

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 650px;
  width: 480px;
  background: rgba(32, 33, 36, 0.95);
  backdrop-filter: blur(40px) saturate(1.8);
  border-radius: 12px;
  box-shadow: 0 8px 28px rgba(0, 0, 0, 0.4), 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow: hidden;
  font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
`;

const ChatHeader = styled.div`
  background: rgba(32, 33, 36, 0.8);
  color: #e8eaed;
  padding: 20px 24px;
  font-weight: 500;
  font-size: 16px;
  text-align: left;
  position: relative;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  
  & > * {
    position: relative;
    z-index: 1;
  }
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: rgba(32, 33, 36, 0.4);
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 3px;
  }
`;

const InputContainer = styled.div`
  padding: 16px 24px 24px 24px;
  background: rgba(32, 33, 36, 0.8);
  backdrop-filter: blur(8px);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  gap: 12px;
  align-items: flex-end;
`;

const MessageInput = styled.textarea`
  flex: 1;
  padding: 12px 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 24px;
  font-size: 14px;
  outline: none;
  resize: none;
  min-height: 20px;
  max-height: 100px;
  background: rgba(60, 64, 67, 0.8);
  color: #e8eaed;
  font-family: 'Google Sans', sans-serif;
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);

  &::placeholder {
    color: #9aa0a6;
  }

  &:focus {
    border-color: #8ab4f8;
    box-shadow: 0 0 0 2px rgba(138, 180, 248, 0.2);
    background: rgba(60, 64, 67, 1);
  }
`;

const SendButton = styled.button`
  background: #8ab4f8;
  color: #202124;
  border: none;
  border-radius: 20px;
  width: 40px;
  height: 40px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s cubic-bezier(0.2, 0, 0, 1);
  font-size: 16px;
  font-weight: 500;

  &:hover:not(:disabled) {
    background: #aecbfa;
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }

  &:disabled {
    background: rgba(255, 255, 255, 0.12);
    color: rgba(255, 255, 255, 0.3);
    cursor: not-allowed;
    transform: none;
  }
`;

const TypingIndicator = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  color: #86868b;
  font-style: italic;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  margin: 0 20px;
`;

const SourcesContainer = styled.div`
  margin-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const ErrorMessage = styled.div`
  background: rgba(255, 59, 48, 0.1);
  color: #FF3B30;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid rgba(255, 59, 48, 0.2);
  margin: 0 20px 16px 20px;
`;

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sources?: Source[];
  confidence?: number;
  fallback?: boolean;
  conversationId?: string;
}

interface ChatWidgetProps {
  title?: string;
  welcomeMessage?: string;
  placeholder?: string;
  productVersion?: string;
  onClose?: () => void;
  selectedDocuments?: string[];
}

const ChatWidget: React.FC<ChatWidgetProps> = ({
  title = process.env.REACT_APP_CHAT_TITLE || 'AI Support Assistant',
  welcomeMessage = process.env.REACT_APP_WELCOME_MESSAGE || 'Hello! How can I help you today?',
  placeholder = process.env.REACT_APP_PLACEHOLDER_TEXT || 'Type your question here...',
  productVersion,
  onClose,
  selectedDocuments = []
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState<string>('');
  const [error, setError] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize with welcome message
    const welcomeMsg: Message = {
      id: uuidv4(),
      role: 'assistant',
      content: welcomeMessage,
      timestamp: new Date(),
    };
    setMessages([welcomeMsg]);
  }, [welcomeMessage]);

  useEffect(() => {
    // Scroll to bottom when messages change
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const messageContent = inputValue.trim();
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content: messageContent,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError('');

    try {
      const response: ChatResponse = await chatAPI.sendMessage(
        messageContent,
        conversationId,
        productVersion,
        selectedDocuments.length > 0 ? selectedDocuments : undefined
      );

      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
        sources: response.sources,
        confidence: response.confidence,
        fallback: response.fallback_triggered,
        conversationId: response.conversation_id,
      };

      setMessages(prev => [...prev, assistantMessage]);
      setConversationId(response.conversation_id);
    } catch (error) {
      console.error('Error sending message:', error);
      setError('Sorry, there was an error processing your message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFeedback = async (messageId: string, rating: number, feedbackText?: string) => {
    const message = messages.find(m => m.id === messageId);
    if (!message?.conversationId) return;

    try {
      await chatAPI.submitFeedback(message.conversationId, rating, feedbackText);
      console.log('Feedback submitted successfully');
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  return (
    <ChatContainer>
      <ChatHeader>
        {title}
      </ChatHeader>

      <MessagesContainer>
        {messages.map((message) => (
          <div key={message.id}>
            <MessageBubble
              message={message.content}
              isUser={message.role === 'user'}
              timestamp={message.timestamp}
              confidence={message.confidence}
              fallback={message.fallback}
            />
            
            {message.sources && message.sources.length > 0 && (
              <SourcesContainer>
                {message.sources.map((source, index) => (
                  <SourceCard key={index} source={source} />
                ))}
              </SourcesContainer>
            )}

            {message.role === 'assistant' && message.conversationId && (
              <FeedbackButtons
                onFeedback={(rating, feedbackText) => 
                  handleFeedback(message.id, rating, feedbackText)
                }
              />
            )}
          </div>
        ))}

        {isLoading && (
          <TypingIndicator>
            AI is typing...
          </TypingIndicator>
        )}

        {error && (
          <ErrorMessage>
            {error}
          </ErrorMessage>
        )}

        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputContainer>
        <MessageInput
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={isLoading}
          rows={1}
        />
        <SendButton
          onClick={handleSendMessage}
          disabled={isLoading || !inputValue.trim()}
        >
          {isLoading ? '⏳' : '→'}
        </SendButton>
      </InputContainer>
    </ChatContainer>
  );
};

export default ChatWidget;
