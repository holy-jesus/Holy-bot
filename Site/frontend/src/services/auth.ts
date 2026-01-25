import axios, { AxiosResponse } from 'axios';

const PROTOCOL = import.meta.env.VITE_APP_ENV === "production" ? "https" : "http";
const API_URL = `${PROTOCOL}://${import.meta.env.VITE_BACKEND_PUBLIC_DOMAIN}${import.meta.env.VITE_BACKEND_PATH}`;

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

async function isLoggedIn() {
  const response = await api.get('/auth/me');
  return response.status === 200;
}

async function loginWithPassword(username: string, password: string) {
  const response = await api.post('/auth/login', { username, password }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.data;
};

async function requestLoginCode(email: string) {
  const response = await api.post('/auth/request-login-code', { email }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.data;
}

async function loginWithCode(code: string) {
  const response = await api.post('/auth/login-with-code', { code }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.data;
};

async function register(email: string, username: string, password?: string): Promise<[number, AxiosResponse]> {
  const response = await api.post('/auth/register', { email, username, password }, {
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': document.cookie.split('; ').find(row => row.startsWith('csrf='))?.split('=')[1] || '',
    },
  });
  return [response.status, response.data];
};

async function verifyEmail(code: string) {
  const response = await api.post('/auth/confirm-email', { code }, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  return response.data;
};

async function logout() {
  await api.post('/auth/logout');
  document.location = '/'
};

async function getCSRFToken() {
  if (document.cookie.includes('csrf=')) {
    return;
  }
  const response = await api.get('/auth/csrf');
  return response.status === 200;
}

export {
  isLoggedIn,
  requestLoginCode,
  loginWithPassword,
  loginWithCode,
  register,
  verifyEmail,
  logout,
  getCSRFToken
};
