'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  User,
  Lock,
  Mail,
  Eye,
  EyeOff,
  CheckCircle,
  Circle,
  Trash2,
  Plus,
  LogOut,
  Sun,
  Moon,
  AlertCircle,
  Check,
  Edit3,
  Calendar,
  Flag,
  X,
  Bot
} from 'lucide-react';

// Import the professional UI CSS
import './styles/professional-ui.css';
import Chatbot from '@/components/Chatbot';

// Define TypeScript interfaces
interface User {
  id: string;
  email: string;
  created_at: string;
}

interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  due_date: string | null;
  priority: 'low' | 'medium' | 'high';
  user_id: string;
  created_at: string;
  updated_at: string;
}

// Theme context
const useTheme = () => {
  const [theme, setTheme] = useState<'light' | 'dark' | 'neon'>('neon');

  useEffect(() => {
    // Check for saved theme preference or system preference
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | 'neon' | null;
    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      setTheme('neon'); // Default to neon theme
    }
  }, []);

  useEffect(() => {
    // Apply theme to document
    document.documentElement.classList.remove('light', 'dark', 'neon-theme');

    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      document.documentElement.style.colorScheme = 'dark';
    } else if (theme === 'neon') {
      document.documentElement.classList.add('neon-theme');
      document.documentElement.style.colorScheme = 'dark';
    } else {
      document.documentElement.classList.add('light');
      document.documentElement.style.colorScheme = 'light';
    }

    // Save theme preference
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => {
      if (prev === 'light') return 'dark';
      if (prev === 'dark') return 'neon';
      return 'light'; // If neon or anything else, switch to light
    });
  };

  return { theme, toggleTheme };
};

export default function Home() {
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [dueDate, setDueDate] = useState<string>('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showChatbot, setShowChatbot] = useState(false);
  const router = useRouter();
  const { theme, toggleTheme } = useTheme();

  // Check if user is logged in on component mount
  useEffect(() => {
    const checkAuthAndLoadData = async () => {
      setIsLoading(true);
      const token = localStorage.getItem('access_token');
      if (token) {
        try {
          // Verify token is still valid
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'https://todo-web-app-nvu7.onrender.com'}/health`, {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (response.ok) {
            setIsLoggedIn(true);
            await fetchUserData(); // Fetch user data after confirming auth
          } else {
            // Token is invalid, remove it
            localStorage.removeItem('access_token');
            setIsLoggedIn(false);
          }
        } catch (err) {
          console.error('Error verifying authentication:', err);
          localStorage.removeItem('access_token');
          setIsLoggedIn(false);
        }
      }
      setIsLoading(false);
    };

    checkAuthAndLoadData();
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      // Fetch user tasks
      const tasksResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'https://todo-web-app-nvu7.onrender.com'}/tasks`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (tasksResponse.ok) {
        const tasksData = await tasksResponse.json();
        setTasks(tasksData);
      }
    } catch (err) {
      console.error('Error fetching user data:', err);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'https://todo-web-app-nvu7.onrender.com'}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }

      // After successful registration, log in with the same credentials
      const loginResponse = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'https://todo-web-app-nvu7.onrender.com'}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });

      if (!loginResponse.ok) {
        const errorData = await loginResponse.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await loginResponse.json();
      localStorage.setItem('access_token', data.access_token);

      // Update authentication state and fetch user data
      setIsLoggedIn(true);
      await fetchUserData();
    } catch (err: any) {
      setError(err.message || 'Registration failed');
      setLoading(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'https://todo-web-app-nvu7.onrender.com'}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: loginEmail,
          password: loginPassword,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);

      // Update authentication state and fetch user data
      setIsLoggedIn(true);
      await fetchUserData();
    } catch (err: any) {
      setError(err.message || 'Login failed');
      setLoading(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    setTasks([]);
    setIsLoggedIn(false);
    // Optionally redirect to login or reload the page to ensure clean state
    window.location.reload();
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'https://todo-web-app-nvu7.onrender.com'}/tasks`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          description: description || null,
          priority,
          due_date: dueDate || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create task');
      }

      const newTask = await response.json();
      setTasks([...tasks, newTask]);

      // Reset form
      setTitle('');
      setDescription('');
      setPriority('medium');
      setDueDate('');
    } catch (err: any) {
      setError(err.message || 'Failed to create task');
    } finally {
      setLoading(false);
    }
  };

  const toggleTaskCompletion = async (taskId: string, currentStatus: boolean) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        // If no token, redirect to login
        setIsLoggedIn(false);
        return;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'https://todo-web-app-nvu7.onrender.com'}/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          completed: !currentStatus,
        }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Unauthorized - token might be expired
          localStorage.removeItem('access_token');
          setIsLoggedIn(false);
          return;
        }
        throw new Error('Failed to update task');
      }

      const updatedTask = await response.json();
      setTasks(tasks.map(task =>
        task.id === taskId ? updatedTask : task
      ));
    } catch (err) {
      setError('Failed to update task');
      console.error(err);
    }
  };

  const deleteTask = async (taskId: string) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        // If no token, redirect to login
        setIsLoggedIn(false);
        return;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'https://todo-web-app-nvu7.onrender.com'}/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Unauthorized - token might be expired
          localStorage.removeItem('access_token');
          setIsLoggedIn(false);
          return;
        }
        throw new Error('Failed to delete task');
      }

      setTasks(tasks.filter(task => task.id !== taskId));
    } catch (err) {
      setError('Failed to delete task');
      console.error(err);
    }
  };

  // Check if we're on the client side and if user is logged in
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    // Check if we're on the client side and if there's a token
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token');
      setIsLoggedIn(!!token);
      setIsLoading(false);
    }
  }, []);

  // If still loading, return a loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          <p className="mt-4 text-lg text-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // If not logged in, show auth forms
  if (!isLoggedIn) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 flex items-center justify-center p-4">
        <div className="w-full max-w-md auth-form-container">
          <div className="bg-gray-900 rounded-2xl shadow-xl overflow-hidden border border-cyan-500 neon-glow">
            <div className="p-1 bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500">
              <div className="bg-gray-900 rounded-xl p-8 auth-form">
                <div className="text-center">
                  <div className="mx-auto bg-gradient-to-r from-cyan-400 to-purple-500 w-16 h-16 rounded-full flex items-center justify-center">
                    <CheckCircle className="h-8 w-8 text-white" />
                  </div>
                  <h2 className="mt-6 text-2xl font-extrabold text-cyan-300">
                    {isLogin ? 'Welcome Back!' : 'Create Account'}
                  </h2>
                  <p className="mt-2 text-sm text-purple-300">
                    {isLogin ? 'Sign in to continue' : 'Get started with us today'}
                  </p>
                </div>

                {error && (
                  <div className="mt-6 bg-red-900/30 border-l-4 border-red-500 p-4 rounded">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <AlertCircle className="h-5 w-5 text-red-400" />
                      </div>
                      <div className="ml-3">
                        <p className="text-sm text-red-300">{error}</p>
                      </div>
                    </div>
                  </div>
                )}

                <form className="mt-8 space-y-6" onSubmit={isLogin ? handleLogin : handleRegister}>
                  {!isLogin && (
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-cyan-300 mb-1">
                        Email address
                      </label>
                      <input
                        id="email"
                        name="email"
                        type="email"
                        autoComplete="email"
                        required
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="appearance-none block w-full px-4 py-3 border border-cyan-500/50 rounded-lg shadow-sm placeholder-gray-500 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 text-base bg-gray-800 text-white neon-glow input-field"
                        placeholder="you@example.com"
                      />
                    </div>
                  )}

                  {isLogin && (
                    <div>
                      <label htmlFor="login-email" className="block text-sm font-medium text-cyan-300 mb-1">
                        Email address
                      </label>
                      <input
                        id="login-email"
                        name="email"
                        type="email"
                        autoComplete="email"
                        required
                        value={loginEmail}
                        onChange={(e) => setLoginEmail(e.target.value)}
                        className="appearance-none block w-full px-4 py-3 border border-cyan-500/50 rounded-lg shadow-sm placeholder-gray-500 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 text-base bg-gray-800 text-white neon-glow input-field"
                        placeholder="you@example.com"
                      />
                    </div>
                  )}

                  <div>
                    <label htmlFor="password" className="block text-sm font-medium text-cyan-300 mb-1">
                      Password
                    </label>
                    <input
                      id="password"
                      name="password"
                      type="password"
                      autoComplete="current-password"
                      required
                      value={isLogin ? loginPassword : password}
                      onChange={(e) => isLogin
                        ? setLoginPassword(e.target.value)
                        : setPassword(e.target.value)
                      }
                      className="appearance-none block w-full px-4 py-3 border border-cyan-500/50 rounded-lg shadow-sm placeholder-gray-500 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 text-base bg-gray-800 text-white neon-glow input-field"
                      placeholder="••••••••"
                    />
                  </div>

                  {!isLogin && (
                    <div>
                      <label htmlFor="confirm-password" className="block text-sm font-medium text-cyan-300 mb-1">
                        Confirm Password
                      </label>
                      <input
                        id="confirm-password"
                        name="confirm-password"
                        type="password"
                        autoComplete="current-password"
                        required
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="appearance-none block w-full px-4 py-3 border border-cyan-500/50 rounded-lg shadow-sm placeholder-gray-500 focus:outline-none focus:ring-cyan-500 focus:border-cyan-500 text-base bg-gray-800 text-white neon-glow input-field"
                        placeholder="••••••••"
                      />
                    </div>
                  )}

                  <div>
                    <button
                      type="submit"
                      disabled={loading}
                      className="w-1/2 mx-auto flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-md text-base font-medium text-black bg-gradient-to-r from-cyan-400 to-blue-500 hover:from-cyan-300 hover:to-blue-400 focus:outline-none focus:ring-2 focus:ring-cyan-300 transition-all duration-200 transform hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-75 relative overflow-hidden group neon-glow button-primary"
                    >
                      <span className="absolute inset-0 w-full h-full transition-all duration-200 ease-out bg-gradient-to-r from-white/10 to-transparent opacity-0 group-hover:opacity-100"></span>
                      <span className="absolute inset-0 w-full bg-white/20 transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-200 ease-out"></span>
                      {loading ? (
                        <>
                          <div className="h-4 w-4 animate-spin rounded-full border-2 border-black border-t-transparent mr-2"></div>
                          Processing...
                        </>
                      ) : (
                        <>
                          {isLogin ? (
                            <>
                              <Lock className="h-4 w-4 mr-2 transition-transform duration-200 group-hover:rotate-12 text-black" />
                              Sign in
                            </>
                          ) : (
                            <>
                              <User className="h-4 w-4 mr-2 transition-transform duration-200 group-hover:rotate-12 text-black" />
                              Create account
                            </>
                          )}
                        </>
                      )}
                    </button>
                  </div>
                </form>

                <div className="mt-6 text-center">
                  <button
                    type="button"
                    onClick={() => {
                      setIsLogin(!isLogin);
                      setError(null);
                    }}
                    className="text-sm font-medium text-cyan-400 hover:text-purple-400 transition-colors"
                  >
                    {isLogin ? "Don't have an account? Register" : "Already have an account? Sign in"}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-center">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-full bg-gray-800 text-cyan-400 border border-cyan-500/50 hover:bg-gray-700 transition-colors"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // If logged in, show the task management interface
  return (
    <div className="min-h-screen">
      <header className="nav-header">
        <div className="nav-container">
          <div className="nav-brand">
            <div className="nav-brand-icon">
              <CheckCircle className="h-6 w-6 text-primary" />
            </div>
            <h1 className="nav-brand-title">
              Todo App
            </h1>
          </div>

          <div className="nav-actions">
            <button
              onClick={toggleTheme}
              className="nav-action-button"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
            <button
              onClick={handleLogout}
              className="nav-button secondary"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="container mt-8">
        <div className="todo-form-container">
          {/* Task Creation Form */}
          <div className="mb-10">
            <div className="todo-form-header">
              <div className="todo-form-title-icon">
                <Plus className="h-5 w-5 text-primary" />
              </div>
              <h2 className="todo-form-title">Create New Task</h2>
            </div>

            {error && (
              <div className="todo-form-error" role="alert">
                <AlertCircle className="todo-form-error-icon" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleCreateTask} className="todo-form">
              <div className="todo-form-group">
                <label htmlFor="title" className="todo-form-label required">
                  <Edit3 />
                  Title
                </label>
                <input
                  type="text"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                  className="todo-form-input"
                  placeholder="What needs to be done?"
                />
              </div>

              <div className="todo-form-group">
                <label htmlFor="description" className="todo-form-label">
                  <Edit3 />
                  Description
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="todo-form-textarea"
                  placeholder="Add details about the task (optional)"
                  rows={3}
                />
              </div>

              <div className="todo-form-row">
                <div className="todo-form-group">
                  <label htmlFor="priority" className="todo-form-label">
                    <Flag />
                    Priority
                  </label>
                  <select
                    id="priority"
                    value={priority}
                    onChange={(e) => setPriority(e.target.value as 'low' | 'medium' | 'high')}
                    className="todo-form-select"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>

                <div className="todo-form-group">
                  <label htmlFor="due-date" className="todo-form-label">
                    <Calendar />
                    Due Date (optional)
                  </label>
                  <input
                    type="date"
                    id="due-date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="todo-form-input"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="todo-form-submit"
              >
                {loading ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent"></div>
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus />
                    Create Task
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Task List */}
          <div className="todo-list-container">
            <div className="todo-list-header">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <CheckCircle className="h-5 w-5 text-primary" />
                </div>
                <h2 className="text-xl font-semibold text-foreground">Your Tasks</h2>
              </div>

              <div className="todo-list-count">
                {tasks.length} {tasks.length === 1 ? 'task' : 'tasks'}
              </div>
            </div>

            {tasks.length === 0 ? (
              <div className="todo-list-empty">
                <div className="todo-list-empty-icon">
                  <CheckCircle className="h-12 w-12 text-primary/50" />
                </div>
                <h3 className="todo-list-empty-title">No tasks yet</h3>
                <p className="todo-list-empty-description">
                  Get started by creating your first task. Your tasks will appear here once you create them.
                </p>
              </div>
            ) : (
              <ul className="todo-list">
                {tasks.map((task) => (
                  <li
                    key={task.id}
                    className="todo-item"
                  >
                    <div className="todo-item-content">
                      <div className="todo-item-checkbox">
                        <button
                          onClick={() => toggleTaskCompletion(task.id, task.completed)}
                          className={`todo-item-checkbox-btn ${task.completed ? 'checked' : ''}`}
                          aria-label={task.completed ? "Mark as incomplete" : "Mark as complete"}
                        >
                          <Check />
                        </button>
                      </div>

                      <div className="todo-item-details">
                        <h3 className={`todo-item-title ${
                          task.completed ? 'completed' : ''
                        }`}>
                          {task.title}
                        </h3>
                        {task.description && (
                          <p className={`todo-item-description ${
                            task.completed ? 'completed' : ''
                          }`}>
                            {task.description}
                          </p>
                        )}

                        <div className="todo-item-meta">
                          <span className={`todo-item-priority ${task.priority}`}>
                            <Flag />
                            {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                          </span>

                          {task.due_date && (
                            <span className="todo-item-due-date">
                              <Calendar />
                              {new Date(task.due_date).toLocaleDateString()}
                            </span>
                          )}

                          <span className="todo-item-created-date">
                            {new Date(task.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>

                      <div className="todo-item-actions">
                        <button
                          onClick={() => deleteTask(task.id)}
                          className="todo-item-action-btn delete"
                          aria-label="Delete task"
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </main>

      {/* Chatbot Toggle Button - Positioned in the top-right corner */}
      <button
        className="fixed top-6 right-6 z-50 bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-4 rounded-full shadow-lg hover:from-blue-600 hover:to-indigo-700 transition-all duration-300 flex items-center justify-center animate-pulse hover:animate-none chatbot-button"
        onClick={() => setShowChatbot(!showChatbot)}
        aria-label={showChatbot ? "Close Todo Assistant" : "Open Todo Assistant"}
      >
        <Bot className="w-6 h-6 text-white" style={{display: 'block', strokeWidth: '2'}} />
      </button>

      {/* Chatbot Panel - Appears directly below the icon when opened */}
      {showChatbot && (
        <div className="fixed top-[calc(3rem+3.5rem)] right-6 z-40 w-96 chatbot-panel-open chatbot-panel-container">
          <div className="!bg-gradient-to-b from-gray-800 to-gray-900 rounded-2xl shadow-2xl border border-cyan-500 flex flex-col chatbot-content">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-3 rounded-t-2xl flex items-center justify-between chatbot-header">
              <div className="flex items-center gap-2">
                <div className="p-1 rounded-full bg-cyan-500/20">
                  <Bot className="w-5 h-5 text-white" style={{display: 'block', strokeWidth: '2'}} />
                </div>
                <h3 className="font-semibold">Todo Assistant</h3>
              </div>
              <button
                className="text-white/80 hover:text-white"
                onClick={() => setShowChatbot(false)}
                aria-label="Close chat"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto max-h-96 chatbot-messages !bg-gray-800/90 p-3">
              <Chatbot onRefreshTasks={fetchUserData} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}