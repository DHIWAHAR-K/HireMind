import { apiClient } from './api'

export interface User {
  id: number
  email: string
  username: string
  first_name: string
  last_name: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  company_name?: string
  job_title?: string
  bio?: string
}

export interface AuthResponse {
  success: boolean
  message: string
  user: User
  token: string
}

export interface LoginRequest {
  email_or_username: string
  password: string
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  first_name: string
  last_name: string
  company_name?: string
  job_title?: string
}

export interface ProfileUpdateRequest {
  first_name?: string
  last_name?: string
  company_name?: string
  job_title?: string
  bio?: string
}

export interface PasswordChangeRequest {
  current_password: string
  new_password: string
}

class AuthAPI {
  private baseURL = '/auth'

  // Set authorization token
  setAuthToken(token: string) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  // Remove authorization token
  removeAuthToken() {
    delete apiClient.defaults.headers.common['Authorization']
  }

  // Register new user
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post(`${this.baseURL}/register`, data)
    return response.data
  }

  // Login user
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post(`${this.baseURL}/login`, data)
    return response.data
  }

  // Get current user info
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get(`${this.baseURL}/me`)
    return response.data
  }

  // Update user profile
  async updateProfile(data: ProfileUpdateRequest): Promise<User> {
    const response = await apiClient.put(`${this.baseURL}/profile`, data)
    return response.data
  }

  // Change password
  async changePassword(data: PasswordChangeRequest): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post(`${this.baseURL}/change-password`, data)
    return response.data
  }

  // Logout user
  async logout(): Promise<{ success: boolean; message: string }> {
    const response = await apiClient.post(`${this.baseURL}/logout`)
    return response.data
  }

  // Validate token
  async validateToken(): Promise<{ success: boolean; message: string; user_id: number; username: string }> {
    const response = await apiClient.get(`${this.baseURL}/validate-token`)
    return response.data
  }
}

export const authAPI = new AuthAPI()