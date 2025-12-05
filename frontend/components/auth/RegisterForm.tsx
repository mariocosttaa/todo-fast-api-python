import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Button, Input, InputError } from '../UI';
import { api, setAuthToken, NEXT_PATH_KEY } from '../../services/api';
import { useAuth } from '../../providers/AuthProvider';

interface RegisterFormProps {
  onSuccess?: () => void;
  onLoginClick?: () => void;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess, onLoginClick }) => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();

  const [name, setName] = useState('');
  const [surname, setSurname] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordConfirm, setPasswordConfirm] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formInputError, setFormInputError] = useState<Record<string, string>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    try {
      const response = await api.post('/auth/register', {
        name,
        surname,
        email,
        password,
        password_confirm: passwordConfirm,
      });

      const { access_token } = response.data;
      if (access_token) {
        localStorage.setItem('access_token', access_token);
        setAuthToken(access_token);
      }
      
      if (onSuccess) {
        onSuccess();
      }

      const nextFromQuery = searchParams.get('next') || undefined;
      const storedNext = localStorage.getItem(NEXT_PATH_KEY) || undefined;
      const target = nextFromQuery || storedNext;

      login(target);
    } catch (err: any) {
      const erros = err.response?.data?.detail;
      
      if (Array.isArray(erros)) {
        const fieldErrors: Record<string, string> = {};
        erros.forEach((error: any) => {
          const field = error.loc?.[1];
          if (field) {
            fieldErrors[field] = error.msg;
          }
        });
        setFormInputError(fieldErrors);
      } else {
         setError('Authentication failed. Please check your details and try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Input
            placeholder="First name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="bg-white/50 backdrop-blur-sm border-gray-200 focus:bg-white transition-all duration-300"
          />
          <Input
            placeholder="Surname"
            type="text"
            value={surname}
            onChange={(e) => setSurname(e.target.value)}
            required
            className="bg-white/50 backdrop-blur-sm border-gray-200 focus:bg-white transition-all duration-300"
          />
        </div>
        <InputError message={formInputError} field="surname" />
        <Input 
          placeholder="Email address" 
          type="email" 
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="bg-white/50 backdrop-blur-sm border-gray-200 focus:bg-white transition-all duration-300"
        />
        <InputError message={formInputError} field="email" />
        <Input 
          placeholder="Password" 
          type="password" 
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="bg-white/50 backdrop-blur-sm border-gray-200 focus:bg-white transition-all duration-300"
        />
        <InputError message={formInputError} field="password" />
        <Input
          placeholder="Confirm password"
          type="password"
          value={passwordConfirm}
          onChange={(e) => setPasswordConfirm(e.target.value)}
          required
          className="bg-white/50 backdrop-blur-sm border-gray-200 focus:bg-white transition-all duration-300"
        />
        <InputError message={formInputError} field="password_confirm" />
        
        <Button type="submit" className="w-full py-3 text-lg font-medium shadow-lg shadow-primary-500/30 hover:shadow-primary-500/40 transition-all duration-300 transform hover:-translate-y-0.5" isLoading={isLoading}>
          Create Account
        </Button>
      </form>

      {error && (
        <div className="mt-4 text-sm text-red-600 bg-red-50/80 backdrop-blur-sm border border-red-100 rounded-xl px-4 py-2 animate-fade-in">
          {error}
        </div>
      )}

      <div className="mt-8 text-center text-sm text-gray-600">
        {"Already have an account? "}
        <button 
          onClick={onLoginClick ? onLoginClick : () => navigate('/login')}
          className="font-semibold text-primary-700 hover:text-primary-800 transition-colors"
        >
          Sign in
        </button>
      </div>
    </div>
  );
};
