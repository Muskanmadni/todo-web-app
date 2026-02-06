'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { 
  User, 
  Lock, 
  Mail, 
  Eye, 
  EyeOff, 
  CheckCircle, 
  Sun, 
  Moon, 
  AlertCircle 
} from 'lucide-react';

// Import the professional UI CSS
import '../styles/professional-ui.css';

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

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const searchParams = useSearchParams();
  const { theme, toggleTheme } = useTheme();

  // Check if we should default to signup mode
  useEffect(() => {
    const mode = searchParams.get('mode');
    if (mode === 'signup') {
      setIsLogin(false);
    }
  }, [searchParams]);

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

      // Redirect to dashboard after successful login
      router.push('/dashboard');
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

      // Redirect to dashboard after successful login
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Login failed');
      setLoading(false);
    } finally {
      setLoading(false);
    }
  };

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
                    className="w-full flex justify-center items-center py-2.5 px-4 border border-transparent rounded-lg shadow-md text-base font-medium text-black bg-gradient-to-r from-cyan-400 to-blue-500 hover:from-cyan-300 hover:to-blue-400 focus:outline-none focus:ring-2 focus:ring-cyan-300 transition-all duration-200 transform hover:-translate-y-0.5 hover:shadow-lg disabled:opacity-75 relative overflow-hidden group neon-glow button-primary"
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