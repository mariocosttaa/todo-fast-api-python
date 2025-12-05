import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Icons } from '../components/UI';
import { AuthModal } from '../components/auth/AuthModal';
import { useAuth } from '../providers/AuthProvider';

export const IndexPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authView, setAuthView] = useState<'login' | 'register'>('login');

  const openAuth = (view: 'login' | 'register') => {
    setAuthView(view);
    setIsAuthModalOpen(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 font-sans text-gray-900 overflow-x-hidden">
      <AuthModal 
        isOpen={isAuthModalOpen} 
        onClose={() => setIsAuthModalOpen(false)} 
        initialView={authView}
      />

      {/* Navigation */}
      <nav className="w-full max-w-7xl mx-auto px-6 py-6 flex items-center justify-between animate-fade-in">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-700 rounded-lg flex items-center justify-center text-white shadow-lg shadow-primary-500/30">
            <Icons.Sparkles />
          </div>
          <span className="text-xl font-bold tracking-tight text-gray-900">MarTaks</span>
        </div>
        <div className="flex items-center gap-4">
          {isAuthenticated ? (
            <button
              onClick={() => navigate('/dashboard')}
              className="px-5 py-2.5 rounded-xl bg-gray-900 text-white text-sm font-medium hover:bg-black transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 flex items-center gap-2"
            >
              <Icons.List />
              Dashboard
            </button>
          ) : (
            <>
              <button
                onClick={() => openAuth('login')}
                className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
              >
                Sign in
              </button>
              <button
                onClick={() => openAuth('register')}
                className="px-5 py-2.5 rounded-xl bg-gray-900 text-white text-sm font-medium hover:bg-black transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5"
              >
                Get Started
              </button>
            </>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-6 pt-20 pb-32 md:pt-32 md:pb-48 text-center">
        <div className="max-w-3xl mx-auto space-y-8 animate-slide-up">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-50 text-primary-700 text-xs font-semibold border border-primary-100 mb-4">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-primary-500"></span>
            </span>
            v2.0 is now live
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-gray-900 leading-tight">
            Organize your life with <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-primary-400">MarTaks</span>
          </h1>
          
          <p className="text-xl text-gray-500 leading-relaxed max-w-2xl mx-auto">
            The premium task management tool designed for clarity and focus. 
            Experience a beautiful, distraction-free environment for your daily goals.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            {isAuthenticated ? (
              <button
                onClick={() => navigate('/dashboard')}
                className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-primary-600 to-primary-700 text-white font-semibold text-lg shadow-xl shadow-primary-500/30 hover:shadow-2xl hover:shadow-primary-500/40 hover:-translate-y-1 transition-all duration-300 flex items-center justify-center gap-2"
              >
                <Icons.List />
                Go to Dashboard
              </button>
            ) : (
              <>
                <button
                  onClick={() => openAuth('register')}
                  className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-primary-600 to-primary-700 text-white font-semibold text-lg shadow-xl shadow-primary-500/30 hover:shadow-2xl hover:shadow-primary-500/40 hover:-translate-y-1 transition-all duration-300"
                >
                  Start for free
                </button>
                <button
                  onClick={() => openAuth('login')}
                  className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-white text-gray-700 font-semibold text-lg border border-gray-200 shadow-sm hover:bg-gray-50 hover:border-gray-300 transition-all duration-300"
                >
                  Live Demo
                </button>
              </>
            )}
          </div>
        </div>

        {/* Floating Cards / Visuals */}
        <div className="mt-24 relative max-w-5xl mx-auto animate-fade-in" style={{ animationDelay: '0.3s' }}>
          <div className="absolute inset-0 bg-gradient-to-t from-gray-50 via-transparent to-transparent z-10"></div>
          
          {/* Mockup Container */}
          <div className="glass-panel p-4 rounded-3xl shadow-2xl border-white/60 bg-white/40 backdrop-blur-xl transform rotate-1 hover:rotate-0 transition-transform duration-700 relative z-0">
            <div className="bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100">
              {/* Fake Header */}
              <div className="h-12 border-b border-gray-100 flex items-center px-4 gap-2 bg-gray-50/50">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-400"></div>
                  <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                  <div className="w-3 h-3 rounded-full bg-green-400"></div>
                </div>
              </div>
              {/* Fake Content */}
              <div className="p-8 space-y-4">
                <div className="flex items-center gap-4 p-4 rounded-xl border border-gray-100 bg-white shadow-sm">
                  <div className="w-6 h-6 rounded-full border-2 border-emerald-500 bg-emerald-50 text-emerald-600 flex items-center justify-center">✓</div>
                  <div className="flex-1">
                    <div className="h-2.5 w-32 bg-gray-200 rounded-full"></div>
                    <div className="h-2 w-20 bg-gray-100 rounded-full mt-2"></div>
                  </div>
                  <div className="px-2 py-1 rounded-md bg-red-50 text-red-600 text-xs font-bold">HIGH</div>
                </div>
                <div className="flex items-center gap-4 p-4 rounded-xl border border-gray-100 bg-white shadow-sm opacity-75">
                  <div className="w-6 h-6 rounded-full border-2 border-gray-300"></div>
                  <div className="flex-1">
                    <div className="h-2.5 w-48 bg-gray-200 rounded-full"></div>
                    <div className="h-2 w-24 bg-gray-100 rounded-full mt-2"></div>
                  </div>
                  <div className="px-2 py-1 rounded-md bg-amber-50 text-amber-600 text-xs font-bold">MED</div>
                </div>
                <div className="flex items-center gap-4 p-4 rounded-xl border border-gray-100 bg-white shadow-sm opacity-50">
                  <div className="w-6 h-6 rounded-full border-2 border-gray-300"></div>
                  <div className="flex-1">
                    <div className="h-2.5 w-40 bg-gray-200 rounded-full"></div>
                  </div>
                  <div className="px-2 py-1 rounded-md bg-sky-50 text-sky-600 text-xs font-bold">LOW</div>
                </div>
              </div>
            </div>
          </div>

          {/* Floating Elements - Increased z-index */}
          <div className="absolute -top-12 -left-12 p-4 glass-panel rounded-2xl animate-float shadow-lg z-20">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600">
                <Icons.Check />
              </div>
              <div>
                <p className="text-xs text-gray-500 font-medium">Tasks Completed</p>
                <p className="text-lg font-bold text-gray-900">1,248</p>
              </div>
            </div>
          </div>

          <div className="absolute -bottom-8 -right-8 p-4 glass-panel rounded-2xl animate-float shadow-lg z-20" style={{ animationDelay: '1.5s' }}>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600">
                <Icons.Sparkles />
              </div>
              <div>
                <p className="text-xs text-gray-500 font-medium">Productivity</p>
                <p className="text-lg font-bold text-gray-900">+145%</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Features Grid */}
      <section className="py-24 bg-white/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-8 rounded-3xl bg-white border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
              <div className="w-12 h-12 rounded-2xl bg-primary-50 flex items-center justify-center text-primary-600 mb-6">
                <Icons.List />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Smart Lists</h3>
              <p className="text-gray-500 leading-relaxed">
                Automatically organize your tasks by priority, date, or project. Keep your workspace clean and focused.
              </p>
            </div>
            <div className="p-8 rounded-3xl bg-white border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
              <div className="w-12 h-12 rounded-2xl bg-amber-50 flex items-center justify-center text-amber-600 mb-6">
                <Icons.Sparkles />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Premium Design</h3>
              <p className="text-gray-500 leading-relaxed">
                A user interface crafted with glassmorphism and smooth animations that makes planning a joy.
              </p>
            </div>
            <div className="p-8 rounded-3xl bg-white border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300">
              <div className="w-12 h-12 rounded-2xl bg-sky-50 flex items-center justify-center text-sky-600 mb-6">
                <Icons.Settings />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Customizable</h3>
              <p className="text-gray-500 leading-relaxed">
                Tailor your experience with settings for timezones, notifications, and profile management.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 text-center text-gray-400 text-sm">
        <p>&copy; {new Date().getFullYear()} MarTaks. All rights reserved.</p>
      </footer>
    </div>
  );
};
