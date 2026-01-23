import axios from 'axios';

const API_URL = `${import.meta.env.VITE_BACKEND_DOMAIN}${import.meta.env.VITE_BACKEND_PATH}`;

const api = axios.create({
  baseURL: API_URL,
});

async function loginWithPassword(username: string, password: string) {
  const response = await api.post('/auth/login', { username, password });
  return response.data;
};

async function loginWithEmail(email: string) {
  const response = await api.post('/auth/login-with-email', { email });
  return response.data;
};

async function register(email: string, username: string, password: string) {
  const response = await api.post('/auth/register', { email, username, password });
  return response.data;
};

async function verifyEmail(code: string) {
  const response = await api.post('/auth/confirm-email', { code });
  return response.data;
};

export {
  loginWithPassword,
  loginWithEmail,
  register,
  verifyEmail
};
