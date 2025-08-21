import axios from 'axios';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  sources?: Source[];
  confidence?: number;
  fallback?: boolean;
}

export interface Source {
  doc_title: string;
  section?: string;
  source_type: string;
  ticket_id?: string;
  confidence: number;
  chunk_id: string;
}

export interface ChatRequest {
  user_id: string;
  query: string;
  product_version?: string;
  conversation_id?: string;
  document_ids?: string[];
}

export interface ChatResponse {
  answer: string;
  sources: Source[];
  conversation_id: string;
  confidence: number;
  fallback_triggered: boolean;
}

export interface FeedbackRequest {
  conversation_id: string;
  user_id: string;
  rating: number;
  feedback_text?: string;
}

class ChatAPI {
  private baseURL: string;
  private userId: string;

  constructor() {
    this.baseURL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
    this.userId = process.env.REACT_APP_USER_ID || 'demo_user';
  }

  async sendMessage(
    query: string, 
    conversationId?: string, 
    productVersion?: string,
    documentIds?: string[]
  ): Promise<ChatResponse> {
    try {
      const request: ChatRequest = {
        user_id: this.userId,
        query,
        conversation_id: conversationId,
        product_version: productVersion,
        document_ids: documentIds,
      };

      const response = await axios.post(`${this.baseURL}/chat`, request);
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw new Error('Failed to send message');
    }
  }

  async submitFeedback(
    conversationId: string,
    rating: number,
    feedbackText?: string
  ): Promise<void> {
    try {
      const request: FeedbackRequest = {
        conversation_id: conversationId,
        user_id: this.userId,
        rating,
        feedback_text: feedbackText,
      };

      await axios.post(`${this.baseURL}/feedback`, request);
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw new Error('Failed to submit feedback');
    }
  }

  async getConversation(conversationId: string): Promise<ChatMessage[]> {
    try {
      const response = await axios.get(`${this.baseURL}/conversations/${conversationId}`);
      return response.data.messages;
    } catch (error) {
      console.error('Error getting conversation:', error);
      throw new Error('Failed to get conversation');
    }
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await axios.get(`${this.baseURL}/health`);
      return response.data.status === 'healthy';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}

export const chatAPI = new ChatAPI();
