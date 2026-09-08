import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('smartcart_access');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('smartcart_access');
      localStorage.removeItem('smartcart_refresh');
      localStorage.removeItem('smartcart_user');
    }
    return Promise.reject(error);
  }
);

export default api;
