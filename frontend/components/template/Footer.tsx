import React from 'react';

const Footer: React.FC = () => {
  const year = new Date().getFullYear();

  return (
    <footer className="mt-10 pt-6 border-t border-gray-200 text-xs text-gray-400 flex items-center justify-between gap-2 w-full">
      <span> {year} MarTaks. All rights reserved.</span>
      <span className="hidden sm:inline">Built with care to keep your tasks organized.</span>
    </footer>
  );
};

export default Footer;