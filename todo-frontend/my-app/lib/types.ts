// Type definitions for the Todo Chatbot application

export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface Todo {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'completed';
  userId: string;
  createdAt: string;
  completedAt?: string;
}

export interface Message {
  id: string;
  conversationId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface Conversation {
  id: string;
  userId: string;
  title: string;
  createdAt: string;
  updatedAt: string;
}

export interface ChatRequest {
  message: string;
  conversationId?: string;
  metadata?: any;
}

export interface ChatResponse {
  conversationId: string;
  response: string;
  action: string;
  todo?: Todo;
  metadata?: any;
}