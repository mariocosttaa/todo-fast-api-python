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

const ACCESS_TOKEN_KEY = 'access_token';
export const NEXT_PATH_KEY = 'auth_next_path';

const existingToken = localStorage.getItem(ACCESS_TOKEN_KEY);
if (existingToken) {
  setAuthToken(existingToken);
}

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    if (status === 401) {
      const requestUrl: string | undefined = error?.config?.url;

      // Do NOT auto-logout for profile-related endpoints; let the UI handle these as
      // validation/auth errors so the user stays on the page (e.g. wrong old password).
      if (requestUrl && requestUrl.startsWith('/profile/')) {
        return Promise.reject(error);
      }

      const currentPath = window.location.pathname + window.location.search;
      localStorage.setItem(NEXT_PATH_KEY, currentPath);
      localStorage.removeItem(ACCESS_TOKEN_KEY);

      if (!window.location.pathname.startsWith('/login')) {
        window.location.href = `/login?next=${encodeURIComponent(currentPath)}`;
      }
    }

    return Promise.reject(error);
  }
);
