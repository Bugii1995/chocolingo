import { writable } from 'svelte/store';
import { getAuthToken, setAuthToken } from './api.js';
import { authAPI } from './api.js';

export const user = writable(null);
export const isAuthenticated = writable(false);

// Initialize auth state from localStorage
export function initAuth() {
  const token = getAuthToken();
  if (token) {
    // Verify token by fetching user
    authAPI.getCurrentUser()
      .then((userData) => {
        user.set(userData);
        isAuthenticated.set(true);
      })
      .catch(() => {
        // Token invalid, clear it
        setAuthToken(null);
        user.set(null);
        isAuthenticated.set(false);
      });
  }
}

export async function login(username, password) {
  try {
    const data = await authAPI.login(username, password);
    const userData = await authAPI.getCurrentUser();
    user.set(userData);
    isAuthenticated.set(true);
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

export async function register(username, email, password) {
  try {
    await authAPI.register(username, email, password);
    // Auto-login after registration
    return await login(username, password);
  } catch (error) {
    return { success: false, error: error.message };
  }
}

export function logout() {
  setAuthToken(null);
  user.set(null);
  isAuthenticated.set(false);
}

// Initialize on import
initAuth();
