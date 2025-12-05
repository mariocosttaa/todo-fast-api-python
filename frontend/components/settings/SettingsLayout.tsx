import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import BaseTemplate from '../template/BaseTemplate';
import { useAuth } from '../../providers/AuthProvider';

interface SettingsLayoutProps {
  activeTab: 'profile' | 'security' | 'time';
  children: React.ReactNode;
}

export const SettingsLayout: React.FC<SettingsLayoutProps> = ({ activeTab, children }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();

  if (!user) return null;

  const firstName = (user.name || '').split(' ')[0] || 'there';
  const title = 'Settings';
  const description = `Manage your profile and preferences, ${firstName}.`;

  const go = (path: string) => {
    if (location.pathname !== path) {
      navigate(path);
    }
  };

  return (
    <BaseTemplate title={title} description={description} isSettingsRoute={true}>
      <div className="max-w-3xl mx-auto space-y-8">
        <header className="flex flex-col gap-4 animate-slide-up">
          <div className="inline-flex items-center p-1 bg-white/50 backdrop-blur-sm rounded-2xl shadow-sm border border-white/60">
            <button
              type="button"
              onClick={() => go('/settings/profile')}
              className={`px-6 py-2 text-sm font-medium rounded-xl transition-all duration-300 ${
                activeTab === 'profile' 
                  ? 'bg-white text-primary-700 shadow-md shadow-primary-500/10' 
                  : 'text-gray-600 hover:bg-white/50'
              }`}
            >
              Profile
            </button>
            <button
              type="button"
              onClick={() => go('/settings/security')}
              className={`px-6 py-2 text-sm font-medium rounded-xl transition-all duration-300 ${
                activeTab === 'security' 
                  ? 'bg-white text-primary-700 shadow-md shadow-primary-500/10' 
                  : 'text-gray-600 hover:bg-white/50'
              }`}
            >
              Security
            </button>
            <button
              type="button"
              onClick={() => go('/settings/time')}
              className={`px-6 py-2 text-sm font-medium rounded-xl transition-all duration-300 ${
                activeTab === 'time' 
                  ? 'bg-white text-primary-700 shadow-md shadow-primary-500/10' 
                  : 'text-gray-600 hover:bg-white/50'
              }`}
            >
              Time & Date
            </button>
          </div>
        </header>

        {children}
      </div>
    </BaseTemplate>
  );
};
