import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Avatar, Icons } from '../UI';
import { useAuth } from '../../providers/AuthProvider';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const isDashboardRoute = location.pathname.startsWith('/dashboard');
  const isTodayRoute = location.pathname.startsWith('/today');
  const isSettingsRoute = location.pathname.startsWith('/settings');

  const goDashboard = () => navigate('/dashboard');
  const goDashboardWithPriority = (priority: 'low' | 'medium' | 'high') => {
    navigate(`/dashboard?priority=${priority}`);
  };
  const goToday = () => navigate('/today');
  const goSettings = () => navigate('/settings/profile');

  return (
    <aside className="w-full md:w-72 glass-panel border-r border-white/40 flex flex-col justify-between h-auto md:h-screen sticky top-0 z-30">
      <div className="p-6">
        <div className="flex items-center space-x-3 mb-10 animate-fade-in">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center text-white shadow-lg shadow-primary-500/30 animate-float">
            <Icons.Sparkles />
          </div>
          <span className="text-2xl font-bold text-gray-900 tracking-tight">MarTaks</span>
        </div>

        <nav className="space-y-2 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4 px-4">Menu</div>
          <button
            onClick={goDashboard}
            className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-300 ${
              isDashboardRoute 
                ? 'bg-primary-50/80 text-primary-700 shadow-sm backdrop-blur-sm' 
                : 'text-gray-600 hover:bg-white/50 hover:text-primary-600'
            }`}
          >
            <Icons.List />
            <span className="ml-3">My Tasks</span>
          </button>
          
          <div className="mt-4 ml-4 border-l border-gray-200/60 pl-3 space-y-1 text-xs text-gray-500">
            <p className="text-[11px] font-semibold text-gray-400 uppercase mb-2 pl-2">By priority</p>
            <button
              onClick={() => goDashboardWithPriority('high')}
              className="w-full flex items-center gap-2 text-gray-600 hover:text-red-600 hover:bg-red-50/50 rounded-lg px-2 py-1.5 transition-all duration-200 group"
            >
              <span className="w-2 h-2 rounded-full bg-red-400 group-hover:bg-red-500 shadow-sm" />
              <span>High priority</span>
            </button>
            <button
              onClick={() => goDashboardWithPriority('medium')}
              className="w-full flex items-center gap-2 text-gray-600 hover:text-amber-600 hover:bg-amber-50/50 rounded-lg px-2 py-1.5 transition-all duration-200 group"
            >
              <span className="w-2 h-2 rounded-full bg-amber-400 group-hover:bg-amber-500 shadow-sm" />
              <span>Medium priority</span>
            </button>
            <button
              onClick={() => goDashboardWithPriority('low')}
              className="w-full flex items-center gap-2 text-gray-600 hover:text-sky-600 hover:bg-sky-50/50 rounded-lg px-2 py-1.5 transition-all duration-200 group"
            >
              <span className="w-2 h-2 rounded-full bg-sky-400 group-hover:bg-sky-500 shadow-sm" />
              <span>Low priority</span>
            </button>
          </div>

          <button
            onClick={goToday}
            className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-300 ${
              isTodayRoute 
                ? 'bg-primary-50/80 text-primary-700 shadow-sm backdrop-blur-sm' 
                : 'text-gray-600 hover:bg-white/50 hover:text-primary-600'
            }`}
          >
            <Icons.Flag />
            <span className="ml-3">Today</span>
          </button>
          <button
            onClick={goSettings}
            className={`w-full flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all duration-300 ${
              isSettingsRoute 
                ? 'bg-primary-50/80 text-primary-700 shadow-sm backdrop-blur-sm' 
                : 'text-gray-600 hover:bg-white/50 hover:text-primary-600'
            }`}
          >
            <Icons.Settings />
            <span className="ml-3">Settings</span>
          </button>
        </nav>
      </div>

      <div className="p-4 border-t border-white/40 bg-white/10 backdrop-blur-md">
        <div className="flex items-center gap-3 mb-4 p-2 rounded-xl bg-white/40 border border-white/50 shadow-sm">
          <Avatar name={user.name} size="sm" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-bold text-gray-900 truncate">{user.name}</p>
            <p className="text-xs text-gray-500 truncate">{user.email}</p>
          </div>
        </div>
        
        <div className="space-y-2">
          <button
            onClick={() => navigate('/')}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-white/50 rounded-lg transition-all duration-200"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
            Back to Home
          </button>
          <button
            onClick={logout}
            className="w-full flex items-center gap-2 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <Icons.LogOut />
            Sign Out
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;