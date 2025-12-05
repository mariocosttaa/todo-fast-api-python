import React from 'react';
import { AuthProvider } from './providers/AuthProvider';
import { AppRouter } from './router';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
};

export default App;
