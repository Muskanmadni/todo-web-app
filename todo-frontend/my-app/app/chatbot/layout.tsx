'use client';

import { useEffect } from 'react';
import { Bot, LogOut } from 'lucide-react';
import { useRouter } from 'next/navigation';

const ChatLayout = ({ children }: { children: React.ReactNode }) => {
  const router = useRouter();

  // Set neon theme as default and prevent changes
  useEffect(() => {
    // Apply neon theme
    document.documentElement.classList.remove('light', 'dark');
    document.documentElement.classList.add('neon-theme');
    document.documentElement.style.colorScheme = 'dark';

    // Save neon theme preference
    localStorage.setItem('theme', 'neon');
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    router.push('/');
  };

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-100 overflow-hidden">
      {/* Header */}
      <header className="nav-header">
        <div className="nav-container">
          <div className="nav-brand">
            <div className="nav-brand-icon">
              <Bot className="h-6 w-6 text-primary" />
            </div>
            <h1 className="nav-brand-title">
              Todo Assistant
            </h1>
          </div>

          <div className="nav-actions">
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

      {/* Chat content */}
      <div className="flex-1 overflow-hidden">
        {children}
      </div>
    </div>
  );
};

export default ChatLayout;