import React from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import Footer from './Footer';

interface BaseTemplateProps {
  title: string;
  description?: string;
  isSettingsRoute: boolean;
  children: React.ReactNode;
  showSearch?: boolean;
  searchValue?: string;
  onSearchChange?: (value: string) => void;
}

const BaseTemplate: React.FC<BaseTemplateProps> = ({
  title,
  description,
  isSettingsRoute,
  children,
  showSearch,
  searchValue,
  onSearchChange,
}) => {
  return (
    <div className="min-h-screen flex flex-col md:flex-row font-sans">
      <Sidebar />

      <main className="flex-1 p-4 md:p-10 w-full overflow-y-auto h-screen relative scroll-smooth">
        <div className="max-w-4xl mx-auto flex flex-col min-h-full">
          <Navbar
            title={title}
            description={description}
            showSearch={showSearch}
            searchValue={searchValue}
            onSearchChange={onSearchChange}
          />
          <div className="mt-8 flex-1 animate-fade-in">
            {children}
          </div>
          <Footer />
        </div>
      </main>
    </div>
  );
};

export default BaseTemplate;
