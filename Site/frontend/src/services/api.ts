import axios from 'axios';

const API_URL = '/api'; // Replace with your actual API URL

const api = axios.create({
  baseURL: API_URL,
});

export const loginWithPassword = async (username, password) => {
  // In a real app, you'd make a POST request to your API
  console.log('Logging in with:', { username, password });
  // Mock response
  return { success: true, token: 'mock-jwt-token' };
};

export const loginWithEmail = async (email) => {
  // In a real app, you'd make a POST request to your API
  console.log('Sending magic link to:', email);
  // Mock response
  return { success: true };
};

export const register = async (email, username, password) => {
  // In a real app, you'd make a POST request to your API
  console.log('Registering with:', { email, username, password });
  // Mock response
  return { success: true };
};

export const verifyEmail = async (code) => {
  // In a real app, you'd make a POST request to your API
  console.log('Verifying email with code:', code);
  // Mock response
  return { success: true, token: 'mock-jwt-token' };
};

export default api;
