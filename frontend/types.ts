export interface User {
  id: string;
  name: string;
  email: string;
}

export type Priority = 'low' | 'medium' | 'high';

export interface Todo {
  id: string;
  text: string;
  completed: boolean;
  createdAt: number;
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