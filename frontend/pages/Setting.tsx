import React from 'react';
import { Navigate } from 'react-router-dom';

// Legacy Setting component: keep path but redirect to new structured settings.
export const Setting: React.FC = () => {
  return <Navigate to="/settings/profile" replace />;
};