'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';

interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: Date;
}

interface ChatbotProps {
  onRefreshTasks?: () => void; // Callback to refresh tasks after chatbot interactions
}

const Chatbot: React.FC<ChatbotProps> = ({ onRefreshTasks }) => {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const messagesEndRef = useRef<null | HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    setIsLoading(true);

    // Create a unique ID for the message
    const userMessageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Add user message to UI immediately
    const userMessage: ChatMessage = {
      id: userMessageId,
      content: inputValue,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);

    try {
      // Clear input
      setInputValue('');

      // Get the auth token from localStorage
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

      // Send to backend API
      const response = await fetch('/api/chat/conversation', { // Updated to match backend endpoint
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: JSON.stringify({
          message: inputValue,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from chatbot');
      }

      const data = await response.json();

      // Create assistant message
      const assistantMessageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const assistantMessage: ChatMessage = {
        id: assistantMessageId,
        content: data.response,
        role: 'assistant',
        timestamp: new Date(),
      };

      // Add assistant response to UI
      setMessages(prev => [...prev, assistantMessage]);

      // Check if the action involves creating, updating, or deleting a todo
      if (data.action && (
        data.action === 'todo_created' ||
        data.action === 'todo_completed' ||
        data.action === 'todo_deleted' ||
        data.action === 'todo_updated'
      )) {
        // Trigger refresh of tasks if callback is provided
        if (onRefreshTasks) {
          onRefreshTasks();
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);

      // Create error message
      const errorMessageId = `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const errorMessage: ChatMessage = {
        id: errorMessageId,
        content: 'Sorry, I encountered an error processing your request.',
        role: 'assistant',
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto bg-gradient-to-b from-gray-800 to-gray-900 rounded-t-2xl flex-grow flex-col justify-between">
      <div className="p-4 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-t-2xl">
        <div className="flex items-center gap-3">
          <div className="relative">
            <div className="w-3 h-3 bg-green-400 rounded-full absolute bottom-0 left-3 transform translate-y-1"></div>
            <Bot className="w-8 h-8 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold">Todo Assistant</h2>
            <p className="text-xs opacity-80">AI-powered todo management</p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-[300px] bg-gray-800/90">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 py-10">
            <Bot className="w-12 h-12 mb-3 opacity-60" />
            <p className="text-center text-sm">How can I help you manage your tasks today?</p>
            <div className="grid grid-cols-1 gap-2 mt-4 w-full max-w-xs">
              <button
                className="text-left text-xs bg-blue-900/50 hover:bg-blue-800/50 text-blue-200 p-2 rounded-lg transition-colors border border-blue-700/50"
                onClick={() => setInputValue("Add a todo: Buy groceries")}
              >
                Add a todo: Buy groceries
              </button>
              <button
                className="text-left text-xs bg-blue-900/50 hover:bg-blue-800/50 text-blue-200 p-2 rounded-lg transition-colors border border-blue-700/50"
                onClick={() => setInputValue("Show my todos")}
              >
                Show my todos
              </button>
              <button
                className="text-left text-xs bg-blue-900/50 hover:bg-blue-800/50 text-blue-200 p-2 rounded-lg transition-colors border border-blue-700/50"
                onClick={() => setInputValue("Mark 'Buy groceries' as complete")}
              >
                Mark 'Buy groceries' as complete
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl p-4 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-tr-none'
                      : 'bg-gradient-to-r from-gray-700 to-gray-800 text-gray-100 rounded-tl-none border border-gray-600/50'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    {message.role !== 'user' && (
                      <div className="flex-shrink-0 pt-0.5">
                        <Bot className="w-4 h-4 text-blue-300" />
                      </div>
                    )}
                    <div className="text-sm">{message.content}</div>
                    {message.role === 'user' && (
                      <div className="flex-shrink-0 pt-0.5">
                        <User className="w-4 h-4" />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[85%] bg-gradient-to-r from-gray-700 to-gray-800 text-gray-100 rounded-2xl p-4 rounded-tl-none border border-gray-600/50">
                  <div className="flex items-center gap-2">
                    <Bot className="w-4 h-4 text-blue-300" />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-75"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce delay-150"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-3 bg-gray-800/90 border-t border-gray-700/50">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Message Todo Assistant..."
            className="flex-1 bg-gray-700/80 text-white rounded-full px-4 py-3 focus:outline-none focus:ring-1 focus:ring-blue-500 text-sm border border-gray-600/50"
            disabled={isLoading}
            aria-label="Type your message to the Todo Assistant"
            autoComplete="off"
          />
          <button
            type="submit"
            className={`p-3 rounded-full ${
              isLoading || !inputValue.trim()
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-600 to-indigo-700 text-white hover:from-blue-500 hover:to-indigo-600 active:scale-95'
            } transition-all duration-200 ease-in-out`}
            disabled={isLoading || !inputValue.trim()}
            aria-label={isLoading ? "Sending message..." : "Send message"}
          >
            {isLoading ? (
              <div className="w-4 h-4 border-t-2 border-r-2 border-white rounded-full animate-spin"></div>
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chatbot;