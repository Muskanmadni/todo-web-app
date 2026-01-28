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
    <div className="chatbot-container">
      <div className="chatbot-messages-container">
        {messages.length === 0 ? (
          <div className="welcome-container">
            <div className="p-3 sm:p-4 bg-gray-700/50 rounded-full mb-4 sm:mb-6">
              <Bot className="w-10 h-10 sm:w-12 sm:h-12 text-blue-400" />
            </div>
            <h3 className="welcome-title text-base sm:text-xl">How can I help you today?</h3>
            <p className="welcome-subtitle text-xs sm:text-sm">Ask me to create, update, or manage your todos</p>
            <div className="suggested-prompts grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 mt-4 sm:mt-8">
              <button
                className="prompt-button text-xs sm:text-sm p-2 sm:p-3"
                onClick={() => setInputValue("Add a todo: Buy groceries")}
              >
                Add a todo: Buy groceries
              </button>
              <button
                className="prompt-button text-xs sm:text-sm p-2 sm:p-3"
                onClick={() => setInputValue("Show my todos")}
              >
                Show my todos
              </button>
              <button
                className="prompt-button text-xs sm:text-sm p-2 sm:p-3"
                onClick={() => setInputValue("Mark 'Buy groceries' as complete")}
              >
                Mark 'Buy groceries' as complete
              </button>
              <button
                className="prompt-button text-xs sm:text-sm p-2 sm:p-3"
                onClick={() => setInputValue("Delete the 'Buy groceries' todo")}
              >
                Delete the 'Buy groceries' todo
              </button>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`message ${message.role}`}
              >
                <div className="avatar">
                  {message.role !== 'user' ? (
                    <div className="p-1.5 sm:p-2 bg-gradient-to-r from-blue-600 to-indigo-700 rounded-full assistant-avatar">
                      <Bot className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
                    </div>
                  ) : (
                    <div className="p-1.5 sm:p-2 bg-gray-600 rounded-full user-avatar">
                      <User className="w-3 h-3 sm:w-4 sm:h-4 text-gray-300" />
                    </div>
                  )}
                </div>
                <div className="message-content text-xs sm:text-sm p-2 sm:p-3">
                  {message.content.split('\n').map((line, i) => (
                    <p key={i}>{line}</p>
                  ))}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="typing-indicator">
                <div className="p-1.5 sm:p-2 bg-gradient-to-r from-blue-600 to-indigo-700 rounded-full">
                  <Bot className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
                </div>
                <div className="flex space-x-2">
                  <div className="w-2 h-2 sm:w-2 sm:h-2 bg-blue-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 sm:w-2 sm:h-2 bg-blue-400 rounded-full animate-bounce delay-75"></div>
                  <div className="w-2 h-2 sm:w-2 sm:h-2 bg-blue-400 rounded-full animate-bounce delay-150"></div>
                </div>
              </div>
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container p-2 sm:p-4">
        <form onSubmit={handleSubmit} className="chat-input-form flex-col sm:flex-row gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Message Todo Assistant..."
            className="chat-input text-sm p-2 sm:p-3 w-full mb-2 sm:mb-0 sm:mr-0 md:w-[400px] lg:w-[500px] xl:w-[600px]"
            disabled={isLoading}
            aria-label="Type your message to the Todo Assistant"
            autoComplete="off"
          />
          <button
            type="submit"
            className="send-button w-full sm:w-auto"
            disabled={isLoading || !inputValue.trim()}
            aria-label={isLoading ? "Sending message..." : "Send message"}
          >
            {isLoading ? (
              <div className="w-5 h-5 border-t-2 border-r-2 border-white rounded-full animate-spin"></div>
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </form>
        <p className="disclaimer text-xs mt-2">
          Todo Assistant can make mistakes. Consider checking important information.
        </p>
      </div>
    </div>
  );
};

export default Chatbot;