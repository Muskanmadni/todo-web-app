'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Bot, User, Send, Home } from 'lucide-react';
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

export default function ChatbotPage() {
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const router = useRouter();

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
      <div className="flex-1 flex items-center justify-center bg-gray-900">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          <p className="mt-4 text-lg text-gray-300">Loading...</p>
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
    <div className="flex-1 flex flex-col bg-gray-900">
      {/* Chat Header */}
      <div className="p-4 border-b border-gray-700 flex items-center gap-3">
        <div className="p-2 bg-gradient-to-r from-blue-600 to-indigo-700 rounded-lg">
          <Bot className="w-5 h-5 text-white" />
        </div>
        <div>
          <h2 className="font-semibold">Todo Assistant</h2>
          <p className="text-xs text-gray-400">AI-powered todo management</p>
        </div>
      </div>

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-3xl mx-auto">
          <Chatbot onRefreshTasks={fetchUserData} />
        </div>
      </div>
    </div>
  );
}