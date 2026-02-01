// lib/api.ts - API service for backend communication with advanced features
import axios, { AxiosInstance } from 'axios';

interface Todo {
  id: string;
  title: string;
  description?: string;
  status: string;
  priority: 'low' | 'medium' | 'high';
  tags?: string[];
  dueDate?: string;
  userId: string;
  createdAt: string;
  completedAt?: string;
}

interface User {
  id: string;
  email: string;
  createdAt: string;
  updatedAt: string;
}

class ApiService {
  private api: AxiosInstance;

  constructor(baseURL: string = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://todo-web-app-nvu7.onrender.com') {
    this.api = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add interceptors for auth, error handling, etc.
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor to add auth tokens
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for handling responses
    this.api.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        console.error('API Error:', error);
        return Promise.reject(error);
      }
    );
  }

  // Authentication methods
  async login(email: string, password: string): Promise<{ access_token: string }> {
    const response = await this.api.post('/auth/login', { email, password });
    return response.data;
  }

  async register(email: string, password: string): Promise<{ access_token: string }> {
    const response = await this.api.post('/auth/register', { email, password });
    return response.data;
  }

  async getUser(): Promise<User> {
    const response = await this.api.get('/users/me');
    return response.data;
  }

  // Todo methods with advanced features
  async getTodos(filters?: {
    completed?: boolean;
    priority?: 'low' | 'medium' | 'high';
    tags?: string[];
    search?: string;
    sortBy?: 'created_at' | 'due_date' | 'priority' | 'title';
    sortOrder?: 'asc' | 'desc';
    page?: number;
    limit?: number;
  }): Promise<{ todos: Todo[]; pagination?: any }> {
    const params = new URLSearchParams();
    
    if (filters) {
      if (filters.completed !== undefined) params.append('completed', String(filters.completed));
      if (filters.priority) params.append('priority', filters.priority);
      if (filters.tags) filters.tags.forEach(tag => params.append('tag', tag));
      if (filters.search) params.append('search', filters.search);
      if (filters.sortBy) params.append('sort_by', filters.sortBy);
      if (filters.sortOrder) params.append('order', filters.sortOrder);
      if (filters.page) params.append('page', String(filters.page));
      if (filters.limit) params.append('limit', String(filters.limit));
    }

    const response = await this.api.get('/tasks', { params });
    return response.data;
  }

  async createTodo(todoData: {
    title: string;
    description?: string;
    priority?: 'low' | 'medium' | 'high';
    tags?: string[];
    dueDate?: string;
    recurrencePattern?: string;
  }): Promise<Todo> {
    const response = await this.api.post('/tasks', {
      title: todoData.title,
      description: todoData.description,
      priority: todoData.priority || 'medium',
      tags: todoData.tags || [],
      due_date: todoData.dueDate,
      recurrence_pattern: todoData.recurrencePattern
    });
    return response.data;
  }

  async updateTodo(id: string, todoData: Partial<{
    title: string;
    description?: string;
    status: string;
    priority: 'low' | 'medium' | 'high';
    tags: string[];
    dueDate: string;
  }>): Promise<Todo> {
    const response = await this.api.put(`/tasks/${id}`, {
      title: todoData.title,
      description: todoData.description,
      status: todoData.status,
      priority: todoData.priority,
      tags: todoData.tags,
      due_date: todoData.dueDate
    });
    return response.data;
  }

  async deleteTodo(id: string): Promise<void> {
    await this.api.delete(`/tasks/${id}`);
  }

  async markTodoCompleted(id: string): Promise<Todo> {
    const response = await this.api.put(`/tasks/${id}`, { status: 'completed' });
    return response.data;
  }

  async markTodoPending(id: string): Promise<Todo> {
    const response = await this.api.put(`/tasks/${id}`, { status: 'pending' });
    return response.data;
  }

  // Chatbot methods
  async sendMessage(message: string, conversationId?: string): Promise<any> {
    const response = await this.api.post('/chat/conversation', {
      message,
      conversation_id: conversationId
    });
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.api.get('/health');
      return response.status === 200;
    } catch (error) {
      return false;
    }
  }
}

// Create a singleton instance
const apiService = new ApiService();

export default apiService;
export type { Todo, User };