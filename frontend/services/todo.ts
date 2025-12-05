import { api } from './api';
import type { Priority } from '../types';

export interface ApiTodo {
  id: string;
  order: number;
  title: string;
  description?: string | null;
  is_completed: boolean;
  due_date?: string | null;
  priority: Priority;
}

export interface TodoListResponse {
  items: ApiTodo[];
  page: number;
  page_size: number;
  total: number;
}

export interface TodoQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  completed?: boolean;
  active?: boolean;
  priority?: Priority;
}

export const fetchTodos = async (params: TodoQueryParams): Promise<TodoListResponse> => {
  const response = await api.get<TodoListResponse>('/todos', { params });
  return response.data;
};

export interface TodayTodoQueryParams {
  priority?: Priority;
  page?: number;
  page_size?: number;
}

export const fetchTodayTodos = async (params: TodayTodoQueryParams = {}): Promise<TodoListResponse> => {
  const response = await api.get<TodoListResponse>('/todos/today', { params });
  return response.data;
};

export interface CreateTodoPayload {
  title: string;
  description?: string;
  priority: Priority;
  due_date?: string | null; // ISO string in UTC
}

export const createTodo = async (payload: CreateTodoPayload): Promise<ApiTodo> => {
  const response = await api.post<{ message: string; todo: ApiTodo }>('/todo/create', payload);
  return response.data.todo;
};

export interface UpdateTodoPayload extends CreateTodoPayload {}

export const updateTodo = async (id: string, payload: UpdateTodoPayload): Promise<ApiTodo> => {
  const response = await api.put<{ message: string; todo: ApiTodo }>(`/todo/update/${id}`, payload);
  return response.data.todo;
};

export const deleteTodo = async (id: string): Promise<void> => {
  await api.delete(`/todo/delete/${id}`);
};

export const updateTodoOrder = async (id: string, order: number): Promise<void> => {
  await api.put(`/todo/order-update/${id}`, { order });
};

export const updateTodoCompleted = async (id: string, is_completed: boolean): Promise<ApiTodo> => {
  const response = await api.put<{ message: string; todo: ApiTodo }>(`/todo/completed/${id}`, { is_completed });
  return response.data.todo;
};
