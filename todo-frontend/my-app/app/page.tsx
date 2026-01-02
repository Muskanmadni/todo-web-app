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
  Flag
} from 'lucide-react';

// Import the professional UI CSS
import './styles/professional-ui.css';

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
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');

  useEffect(() => {
    // Check for saved theme preference or system preference
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (savedTheme) {
      setTheme(savedTheme);
    } else {
      setTheme(systemPrefersDark ? 'dark' : 'light');
    }
  }, []);

  useEffect(() => {
    // Apply theme to document
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
      document.documentElement.style.colorScheme = 'dark';
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.style.colorScheme = 'light';
    }

    // Save theme preference
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
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
  const router = useRouter();
  const { theme, toggleTheme } = useTheme();

  // Check if user is logged in on component mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      fetchUserData();
    }
  }, []);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const response = await fetch('https://todo-web-app-nvu7.onrender.com/health', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        localStorage.removeItem('access_token');
        return;
      }

      // Fetch user tasks
      const tasksResponse = await fetch('https://todo-web-app-nvu7.onrender.com/tasks', {
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
      const response = await fetch('https://todo-web-app-nvu7.onrender.com/auth/register', {
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

      // Automatically log in after registration
      handleLogin(e);
    } catch (err: any) {
      setError(err.message || 'Registration failed');
      setLoading(false);
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('https://todo-web-app-nvu7.onrender.com/auth/login', {
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

      // Update authentication state
      setIsLoggedIn(true);

      // Fetch user data after login
      fetchUserData();
    } catch (err: any) {
      setError(err.message || 'Login failed');
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    setTasks([]);
    setIsLoggedIn(false);
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

      const response = await fetch('https://todo-web-app-nvu7.onrender.com/tasks', {
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
      if (!token) return;

      const response = await fetch(`https://todo-web-app-nvu7.onrender.com/tasks/${taskId}`, {
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
      if (!token) return;

      const response = await fetch(`https://todo-web-app-nvu7.onrender.com/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            <div className="p-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-600">
              <div className="bg-white rounded-xl p-8">
                <div className="text-center">
                  <div className="mx-auto bg-gradient-to-r from-indigo-500 to-purple-600 w-16 h-16 rounded-full flex items-center justify-center">
                    <CheckCircle className="h-8 w-8 text-white" />
                  </div>
                  <h2 className="mt-6 text-2xl font-extrabold text-gray-900">
                    {isLogin ? 'Welcome Back!' : 'Create Account'}
                  </h2>
                  <p className="mt-2 text-sm text-gray-500">
                    {isLogin ? 'Sign in to continue' : 'Get started with us today'}
                  </p>
                </div>

                {error && (
                  <div className="mt-6 bg-red-50 border-l-4 border-red-500 p-4 rounded">
                    <div className="flex">
                      <div className="flex-shrink-0">
                        <AlertCircle className="h-5 w-5 text-red-400" />
                      </div>
                      <div className="ml-3">
                        <p className="text-sm text-red-700">{error}</p>
                      </div>
                    </div>
                  </div>
                )}

                <form className="mt-8 space-y-6" onSubmit={isLogin ? handleLogin : handleRegister}>
                  {!isLogin && (
                    <div>
                      <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
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
                        className="appearance-none block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base"
                        placeholder="you@example.com"
                      />
                    </div>
                  )}

                  {isLogin && (
                    <div>
                      <label htmlFor="login-email" className="block text-sm font-medium text-gray-700 mb-1">
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
                        className="appearance-none block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base"
                        placeholder="you@example.com"
                      />
                    </div>
                  )}

                  <div>
                    <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
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
                      className="appearance-none block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base"
                      placeholder="••••••••"
                    />
                  </div>

                  {!isLogin && (
                    <div>
                      <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-700 mb-1">
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
                        className="appearance-none block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-base"
                        placeholder="••••••••"
                      />
                    </div>
                  )}

                  <div>
                    <button
                      type="submit"
                      disabled={loading}
                      className="w-1/2 mx-auto flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-md text-base font-medium text-white bg-gradient-to-r from-blue-500 to-blue-700 hover:from-blue-600 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-300 transition-all duration-200 transform hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-75 relative overflow-hidden group"
                    >
                      <span className="absolute inset-0 w-full h-full transition-all duration-200 ease-out bg-gradient-to-r from-white/10 to-transparent opacity-0 group-hover:opacity-100"></span>
                      <span className="absolute inset-0 w-full bg-white/20 transform scale-x-0 group-hover:scale-x-100 transition-transform origin-left duration-200 ease-out"></span>
                      {loading ? (
                        <>
                          <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent mr-2"></div>
                          Processing...
                        </>
                      ) : (
                        <>
                          {isLogin ? (
                            <>
                              <Lock className="h-4 w-4 mr-2 transition-transform duration-200 group-hover:rotate-12" />
                              Sign in
                            </>
                          ) : (
                            <>
                              <User className="h-4 w-4 mr-2 transition-transform duration-200 group-hover:rotate-12" />
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
                    className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
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
              className="p-2 rounded-full bg-gray-200 text-gray-700 hover:bg-gray-300 transition-colors"
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
    </div>
  );
}