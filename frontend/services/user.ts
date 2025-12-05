import { api } from './api';
import type { User } from '../types';

export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get<User>('/auth/me');
  return response.data;
};

export interface UpdateProfilePayload {
  name: string;
  surname: string;
  email: string;
}

export const updateProfile = async (payload: UpdateProfilePayload): Promise<User> => {
  const response = await api.put<User>('/profile/update', payload);
  return response.data;
};

export interface UpdatePasswordPayload {
  old_password: string;
  password: string;
  password_confirm: string;
}

export const updatePassword = async (payload: UpdatePasswordPayload): Promise<void> => {
  await api.put('/profile/password/update', payload);
};
