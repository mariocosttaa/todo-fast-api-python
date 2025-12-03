import axios from 'axios';

// Central Axios instance for talking to the FastAPI backend
// Configure the base URL via Vite env: VITE_API_URL
// Example: VITE_API_URL=http://localhost:8000/v1
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/v1',
  withCredentials: false,
});

// Optional helper to set/remove auth token
export const setAuthToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};
