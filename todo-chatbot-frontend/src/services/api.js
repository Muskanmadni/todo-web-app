// API service for connecting frontend to backend
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

class TodoAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  // Process natural language request
  async processNaturalLanguageRequest(message) {
    try {
      const response = await fetch(`${this.baseURL}/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: message,
          sender_type: 'user'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.response || "I processed your request successfully.";
    } catch (error) {
      console.error('Error processing natural language request:', error);
      throw error;
    }
  }

  // Get all todos
  async getTodos() {
    try {
      const response = await fetch(`${this.baseURL}/todos`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching todos:', error);
      throw error;
    }
  }

  // Create a new todo
  async createTodo(todoData) {
    try {
      const response = await fetch(`${this.baseURL}/todos`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(todoData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating todo:', error);
      throw error;
    }
  }

  // Update a todo
  async updateTodo(todoId, todoData) {
    try {
      const response = await fetch(`${this.baseURL}/todos/${todoId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(todoData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error updating todo:', error);
      throw error;
    }
  }

  // Delete a todo
  async deleteTodo(todoId) {
    try {
      const response = await fetch(`${this.baseURL}/todos/${todoId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.status === 204; // No content
    } catch (error) {
      console.error('Error deleting todo:', error);
      throw error;
    }
  }
}

export default new TodoAPI();