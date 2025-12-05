import React from 'react';
import { LoginForm } from '../components/auth/LoginForm';
import { Icons } from '../components/UI';

export const Login: React.FC = () => {
  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4">
      <div className="w-full max-w-md glass-panel rounded-2xl p-8 animate-slide-up">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary-100 text-primary-600 mb-6 shadow-lg shadow-primary-500/20 animate-float">
            <Icons.Sparkles />
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to MarTaks</h1>
          <p className="text-gray-600">Your powerful, simple, and free to-do app.</p>
        </div>

        <LoginForm />
      </div>
    </div>
  );
};
