import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Button, Input } from '../UI';
import { api, setAuthToken, NEXT_PATH_KEY } from '../../services/api';
import { useNotification } from '../Notifications';
import { useAuth } from '../../providers/AuthProvider';

interface LoginFormProps {
  onSuccess?: () => void;
  onRegisterClick?: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess, onRegisterClick }) => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { showNotification } = useNotification();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      const response = await api.post('/auth/login', {
        email,
        password,
      });

      const { access_token } = response.data;
      if (access_token) {
        localStorage.setItem('access_token', access_token);
        setAuthToken(access_token);
      }

      showNotification({
        title: 'Logged in successfully',
        type: 'success',
      });
      
      if (onSuccess) {
        onSuccess();
      }

      const nextFromQuery = searchParams.get('next') || undefined;
      const storedNext = localStorage.getItem(NEXT_PATH_KEY) || undefined;
      const target = nextFromQuery || storedNext;

      login(target);
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail?.[0]?.msg || 'Login failed';
      setError(errorMessage);

      showNotification({
        title: 'Login failed',
        type: 'error',
        description: errorMessage,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input 
          placeholder="Email address" 
          type="email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="bg-white/50 backdrop-blur-sm border-gray-200 focus:bg-white transition-all duration-300"
        />
        <Input 
          placeholder="Password" 
          type="password" 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="bg-white/50 backdrop-blur-sm border-gray-200 focus:bg-white transition-all duration-300"
        />
        
        <Button type="submit" className="w-full py-3 text-lg font-medium shadow-lg shadow-primary-500/30 hover:shadow-primary-500/40 transition-all duration-300 transform hover:-translate-y-0.5" isLoading={isLoading}>
          Sign In
        </Button>
      </form>

      {error && (
        <div className="mt-4 text-sm text-red-600 bg-red-50/80 backdrop-blur-sm border border-red-100 rounded-xl px-4 py-2 animate-fade-in">
          {error}
        </div>
      )}

      <div className="mt-8 text-center text-sm text-gray-600">
        {"Don't have an account? "}
        <button 
          onClick={onRegisterClick ? onRegisterClick : () => navigate('/register')}
          className="font-semibold text-primary-700 hover:text-primary-800 transition-colors"
        >
          Sign up for free
        </button>
      </div>
    </div>
  );
};
