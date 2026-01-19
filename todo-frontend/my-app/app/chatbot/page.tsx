'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Bot, User, X, ArrowLeft, CheckCircle, Sun, Moon } from 'lucide-react';
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

export default function ChatbotPage() {
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();
  const { theme, toggleTheme } = useTheme();

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
            // Optionally fetch user data here if needed
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

  // If not logged in, redirect to home
  if (!isLoggedIn) {
    router.push('/');
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="nav-header py-2 sm:py-4">
        <div className="nav-container flex flex-col sm:flex-row items-center gap-3 sm:gap-0">
          <div className="nav-brand flex-1">
            <button
              onClick={() => router.back()}
              className="flex items-center gap-2 text-foreground hover:text-primary transition-colors w-full justify-center sm:justify-start"
            >
              <ArrowLeft className="h-4 w-4 sm:h-5 sm:w-5" />
              <div className="nav-brand-icon">
                <CheckCircle className="h-5 w-5 sm:h-6 sm:w-6 text-primary" />
              </div>
              <h1 className="nav-brand-title text-sm sm:text-base">
                Todo App
              </h1>
            </button>
          </div>

          <div className="nav-actions">
            <button
              onClick={toggleTheme}
              className="nav-action-button"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun className="h-4 w-4 sm:h-5 sm:w-5" /> : <Moon className="h-4 w-4 sm:h-5 sm:w-5" />}
            </button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-2 sm:px-4 py-4 sm:py-8 max-w-full sm:max-w-4xl chatbot-page-container">
        <div className="bg-card rounded-2xl shadow-lg border border-border flex flex-col min-h-[350px] h-[60vh] sm:h-[65vh] md:h-[70vh] lg:h-[75vh] xl:h-[80vh] 2xl:h-[85vh] chatbot-main-container">
          <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row items-center gap-3">
              <div className="relative">
                <div className="w-4 h-4 bg-green-400 rounded-full absolute bottom-0 left-4 transform translate-y-1"></div>
                <Bot className="w-8 h-8 sm:w-10 sm:h-10 text-white" />
              </div>
              <div className="text-center sm:text-left">
                <h1 className="text-xl sm:text-2xl font-bold">Todo Assistant</h1>
                <p className="text-blue-100 text-xs sm:text-sm">AI-powered todo management</p>
              </div>
            </div>
          </div>

          <div className="p-3 sm:p-4 bg-gray-800/90 flex-1 overflow-y-auto flex flex-col">
            <Chatbot onRefreshTasks={fetchUserData} />
          </div>
        </div>
      </main>
    </div>
  );
}