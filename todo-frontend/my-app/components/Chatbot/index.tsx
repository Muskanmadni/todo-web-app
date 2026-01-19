'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Home } from 'lucide-react';
import { useRouter } from 'next/navigation';

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
  const router = useRouter();
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
        } else {
          // If on the chatbot page, provide option to go back to tasks
          const userMessage: ChatMessage = {
            id: `msg-${Date.now()}-navigate`,
            content: "Task updated successfully! Would you like to go back to your tasks?",
            role: 'assistant',
            timestamp: new Date(),
          };

          setMessages(prev => [...prev, userMessage]);
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
    <div className="flex flex-col h-full max-w-full sm:max-w-4xl mx-auto bg-gradient-to-b from-gray-800 to-gray-900 rounded-t-2xl flex-grow flex-col justify-between min-h-[250px] overflow-hidden">
      <div className="p-3 sm:p-4 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-t-2xl">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-3 h-3 bg-green-400 rounded-full absolute bottom-0 left-3 transform translate-y-1"></div>
              <Bot className="w-7 h-7 sm:w-8 sm:h-8 text-white" />
            </div>
            <div className="text-center sm:text-left">
              <h2 className="text-base sm:text-lg font-bold">Todo Assistant</h2>
              <p className="text-xs opacity-80">AI-powered todo management</p>
            </div>
          </div>
          <button
            onClick={() => router.push('/')}
            className="flex items-center gap-1 text-xs bg-white/10 hover:bg-white/20 px-2 sm:px-3 py-1 sm:py-1.5 rounded-lg transition-colors w-full sm:w-auto justify-center"
            aria-label="Go back to tasks"
          >
            <Home className="w-3 h-3" />
            <span className="hidden sm:inline">Back to Tasks</span>
            <span className="sm:hidden">Back</span>
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 bg-gray-800/90 chatbot-messages-container flex-grow">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-gray-400 py-8 sm:py-10">
            <Bot className="w-10 h-10 sm:w-12 sm:h-12 mb-2 sm:mb-3 opacity-60" />
            <p className="text-center text-sm">How can I help you manage your tasks today?</p>
            <div className="grid grid-cols-1 gap-2 mt-3 sm:mt-4 w-full max-w-[90%] sm:max-w-xs">
              <button
                className="text-left text-xs bg-blue-900/50 hover:bg-blue-800/50 text-blue-200 p-2 rounded-lg transition-colors border border-blue-700/50 break-words"
                onClick={() => setInputValue("Add a todo: Buy groceries")}
              >
                Add a todo: Buy groceries
              </button>
              <button
                className="text-left text-xs bg-blue-900/50 hover:bg-blue-800/50 text-blue-200 p-2 rounded-lg transition-colors border border-blue-700/50 break-words"
                onClick={() => setInputValue("Show my todos")}
              >
                Show my todos
              </button>
              <button
                className="text-left text-xs bg-blue-900/50 hover:bg-blue-800/50 text-blue-200 p-2 rounded-lg transition-colors border border-blue-700/50 break-words"
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
                  className={`max-w-[85%] rounded-2xl p-3 sm:p-4 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-tr-none'
                      : 'bg-gradient-to-r from-gray-700 to-gray-800 text-gray-100 rounded-tl-none border border-gray-600/50'
                  }`}
                >
                  <div className="flex items-start gap-1 sm:gap-2">
                    {message.role !== 'user' && (
                      <div className="flex-shrink-0 pt-0.5">
                        <Bot className="w-3 h-3 sm:w-4 sm:h-4 text-blue-300" />
                      </div>
                    )}
                    <div className="text-xs sm:text-sm break-words max-w-[200px] sm:max-w-[300px]">{message.content}</div>
                    {message.role === 'user' && (
                      <div className="flex-shrink-0 pt-0.5">
                        <User className="w-3 h-3 sm:w-4 sm:h-4" />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="max-w-[85%] bg-gradient-to-r from-gray-700 to-gray-800 text-gray-100 rounded-2xl p-3 sm:p-4 rounded-tl-none border border-gray-600/50">
                  <div className="flex items-center gap-1 sm:gap-2">
                    <Bot className="w-3 h-3 sm:w-4 sm:h-4 text-blue-300" />
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
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Message Todo Assistant..."
            className="flex-1 bg-gray-700/80 text-white rounded-full px-3 sm:px-4 py-2 sm:py-3 focus:outline-none focus:ring-1 focus:ring-blue-500 text-xs sm:text-sm border border-gray-600/50 min-h-[40px]"
            disabled={isLoading}
            aria-label="Type your message to the Todo Assistant"
            autoComplete="off"
          />
          <button
            type="submit"
            className={`p-2 sm:p-3 rounded-full ${
              isLoading || !inputValue.trim()
                ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                : 'bg-gradient-to-r from-blue-600 to-indigo-700 text-white hover:from-blue-500 hover:to-indigo-600 active:scale-95'
            } transition-all duration-200 ease-in-out min-h-[40px]`}
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