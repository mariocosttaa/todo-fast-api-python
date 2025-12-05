export interface User {
  id: string;
  name: string;
  email: string;
}

export type Priority = 'low' | 'medium' | 'high';

export interface Todo {
  id: string;
  // Main title of the task (mapped from backend title)
  text: string;
  completed: boolean;
  createdAt: number;
  // Optional richer fields used by the backend
  title?: string;
  description?: string | null;
  dueDate?: string | null;
  order?: number;
  category?: 'work' | 'personal' | 'urgent';
  priority: Priority;
  aiGenerated?: boolean;
}

export enum FilterType {
  ALL = 'ALL',
  ACTIVE = 'ACTIVE',
  COMPLETED = 'COMPLETED'
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
}

export type ViewState = 'login' | 'register' | 'app';