import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Workflow API
export const workflowAPI = {
  start: (params: { description: string; company_name: string; department?: string }, sessionId?: string) =>
    api.post('/api/workflow/start', { ...params, session_id: sessionId }),
  
  getStatus: (sessionId: string) =>
    api.get(`/api/workflow/${sessionId}`),
}

// Agent API
export const agentAPI = {
  run: (agentType: string, inputText: string, sessionId?: string) =>
    api.post('/api/agent/run', {
      agent_type: agentType,
      input_text: inputText,
      session_id: sessionId,
    }),
}

// Profiles API
export const profilesAPI = {
  list: (limit = 10) =>
    api.get('/api/profiles', { params: { limit } }),
  
  get: (sessionId: string) =>
    api.get(`/api/profiles/${sessionId}`),
  
  delete: (sessionId: string) =>
    api.delete(`/api/profiles/${sessionId}`),
}

// Health check
export const healthAPI = {
  check: () => api.get('/health'),
}

export default api