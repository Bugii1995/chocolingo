const API_BASE_URL = 'http://localhost:8000';

let authToken = null;

export function setAuthToken(token) {
  authToken = token;
  if (token) {
    localStorage.setItem('auth_token', token);
  } else {
    localStorage.removeItem('auth_token');
  }
}

export function getAuthToken() {
  if (!authToken) {
    authToken = localStorage.getItem('auth_token');
  }
  return authToken;
}

async function apiRequest(endpoint, options = {}) {
  const token = getAuthToken();
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

// Auth API
export const authAPI = {
  async register(username, email, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('email', email);
    formData.append('password', password);
    
    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, email, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Registration failed' }));
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  },

  async login(username, password) {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    setAuthToken(data.access_token);
    return data;
  },

  async getCurrentUser() {
    return apiRequest('/api/auth/me');
  },
};

// Topics API
export const topicsAPI = {
  async list() {
    return apiRequest('/api/topics/');
  },

  async get(topicId) {
    return apiRequest(`/api/topics/${topicId}`);
  },
};

// Quiz API
export const quizAPI = {
  async createSession(topicId, mode = 'normal') {
    return apiRequest('/api/quiz/sessions', {
      method: 'POST',
      body: JSON.stringify({ topic_id: topicId, mode }),
    });
  },

  async getSession(sessionId) {
    return apiRequest(`/api/quiz/sessions/${sessionId}`);
  },

  async submitAnswers(sessionId, answers) {
    return apiRequest(`/api/quiz/sessions/${sessionId}/answers`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    });
  },

  async getResults(sessionId) {
    return apiRequest(`/api/quiz/sessions/${sessionId}/results`);
  },
};

// Progress API
export const progressAPI = {
  async getDashboard() {
    return apiRequest('/api/progress/dashboard');
  },

  async getTopicProgress(topicId) {
    return apiRequest(`/api/progress/topics/${topicId}`);
  },

  async getMap() {
    return apiRequest('/api/progress/map');
  },
};
