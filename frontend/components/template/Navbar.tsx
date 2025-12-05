import React from 'react';

interface NavbarProps {
  title: string;
  description?: string;
  showSearch?: boolean;
  searchValue?: string;
  onSearchChange?: (value: string) => void;
}

const Navbar: React.FC<NavbarProps> = ({ title, description, showSearch, searchValue, onSearchChange }) => {
  return (
    <header className="mb-4 md:mb-6 flex flex-col gap-2 animate-fade-in">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">{title}</h1>
          {description && (
            <p className="text-gray-500 text-sm md:text-base mt-1">{description}</p>
          )}
        </div>
        <div className="flex items-center gap-3">
          {showSearch && (
            <div className="w-full md:w-72">
              <div className="relative group">
                <input
                  type="text"
                  value={searchValue || ''}
                  onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
                  placeholder="Search tasks..."
                  className="w-full px-4 py-2.5 rounded-2xl border border-white/60 bg-white/50 backdrop-blur-sm text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-300 focus:bg-white transition-all duration-300 shadow-sm group-hover:shadow-md group-hover:border-primary-200"
                />
                <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Navbar;