import axios from 'axios';

const PROTOCOL = import.meta.env.VITE_APP_ENV === "production" ? "https" : "http";
const API_URL = `${PROTOCOL}://${import.meta.env.VITE_BACKEND_PUBLIC_DOMAIN}${import.meta.env.VITE_BACKEND_PATH}`;

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

async function loginWithPassword(username: string, password: string) {
  const response = await api.post('/auth/login', { username, password }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.data;
};

async function loginWithEmail(email: string) {
  const response = await api.post('/auth/login-with-email', { email }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.data;
};

async function register(email: string, username: string, password?: string) {
  const response = await api.post('/auth/register', { email, username, password }, {
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': document.cookie.split('; ').find(row => row.startsWith('csrf='))?.split('=')[1] || '',
    },
  });
  return response.data;
};

async function verifyEmail(code: string) {
  const response = await api.post('/auth/confirm-email', { code }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.data;
};

async function getCSRFToken() {
  const response = await api.get('/auth/csrf');
  return response.status === 200;
}

export {
  loginWithPassword,
  loginWithEmail,
  register,
  verifyEmail,
  getCSRFToken
};
