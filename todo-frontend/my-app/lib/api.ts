// API service for backend communication
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://todo-web-app-nvu7.onrender.com';

interface Todo {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'completed';
  userId: string;
  createdAt: string;
  completedAt?: string;
}

interface Message {
  id: string;
  conversationId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

interface Conversation {
  id: string;
  userId: string;
  title: string;
  createdAt: string;
  updatedAt: string;
}

// Todo API functions
export const todoApi = {
  // Get all todos for the user
  getTodos: async (): Promise<Todo[]> => {
    const response = await fetch(`${API_BASE_URL}/todos`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch todos: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Create a new todo
  createTodo: async (title: string, description?: string): Promise<Todo> => {
    const response = await fetch(`${API_BASE_URL}/todos`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, description }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to create todo: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Update an existing todo
  updateTodo: async (id: string, updates: Partial<Todo>): Promise<Todo> => {
    const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to update todo: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Delete a todo
  deleteTodo: async (id: string): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`Failed to delete todo: ${response.statusText}`);
    }
  },
};

// Conversation API functions
export const conversationApi = {
  // Get all conversations for the user
  getConversations: async (): Promise<Conversation[]> => {
    const response = await fetch(`${API_BASE_URL}/chat/conversations`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch conversations: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Get a specific conversation with its messages
  getConversation: async (id: string): Promise<{ conversation: Conversation; messages: Message[] }> => {
    const response = await fetch(`${API_BASE_URL}/chat/conversations/${id}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch conversation: ${response.statusText}`);
    }
    
    return response.json();
  },

  // Send a message to the chatbot
  sendMessage: async (message: string, conversationId?: string) => {
    const response = await fetch(`${API_BASE_URL}/chat/conversation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversationId: conversationId || null,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Failed to send message: ${response.statusText}`);
    }
    
    return response.json();
  },
};