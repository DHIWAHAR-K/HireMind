import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { authAPI, User, LoginRequest, RegisterRequest, ProfileUpdateRequest, PasswordChangeRequest } from '../services/authApi'

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
  error: string | null
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('hiremind_token'),
  isAuthenticated: false,
  loading: false,
  error: null,
}

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/login',
  async (loginData: LoginRequest, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(loginData)
      
      // Store token in localStorage
      localStorage.setItem('hiremind_token', response.token)
      
      // Set auth token for future requests
      authAPI.setAuthToken(response.token)
      
      return response
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed'
      return rejectWithValue(message)
    }
  }
)

export const registerUser = createAsyncThunk(
  'auth/register',
  async (registerData: RegisterRequest, { rejectWithValue }) => {
    try {
      const response = await authAPI.register(registerData)
      
      // Store token in localStorage
      localStorage.setItem('hiremind_token', response.token)
      
      // Set auth token for future requests
      authAPI.setAuthToken(response.token)
      
      return response
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Registration failed'
      return rejectWithValue(message)
    }
  }
)

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const user = await authAPI.getCurrentUser()
      return user
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Failed to get user info'
      return rejectWithValue(message)
    }
  }
)

export const updateUserProfile = createAsyncThunk(
  'auth/updateProfile',
  async (profileData: ProfileUpdateRequest, { rejectWithValue }) => {
    try {
      const user = await authAPI.updateProfile(profileData)
      return user
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Profile update failed'
      return rejectWithValue(message)
    }
  }
)

export const changePassword = createAsyncThunk(
  'auth/changePassword',
  async (passwordData: PasswordChangeRequest, { rejectWithValue }) => {
    try {
      const response = await authAPI.changePassword(passwordData)
      return response
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Password change failed'
      return rejectWithValue(message)
    }
  }
)

export const logoutUser = createAsyncThunk(
  'auth/logout',
  async (_, { rejectWithValue }) => {
    try {
      await authAPI.logout()
      
      // Remove token from localStorage
      localStorage.removeItem('hiremind_token')
      
      // Remove auth token from API client
      authAPI.removeAuthToken()
      
      return true
    } catch (error: any) {
      // Still logout locally even if API call fails
      localStorage.removeItem('hiremind_token')
      authAPI.removeAuthToken()
      return true
    }
  }
)

export const validateToken = createAsyncThunk(
  'auth/validateToken',
  async (_, { rejectWithValue }) => {
    try {
      const token = localStorage.getItem('hiremind_token')
      if (!token) {
        throw new Error('No token found')
      }
      
      // Set token for this request
      authAPI.setAuthToken(token)
      
      // Validate token and get user info
      await authAPI.validateToken()
      const user = await authAPI.getCurrentUser()
      
      return { token, user }
    } catch (error: any) {
      // Remove invalid token
      localStorage.removeItem('hiremind_token')
      authAPI.removeAuthToken()
      const message = error.response?.data?.detail || 'Token validation failed'
      return rejectWithValue(message)
    }
  }
)

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null
    },
    clearAuth: (state) => {
      state.user = null
      state.token = null
      state.isAuthenticated = false
      state.loading = false
      state.error = null
      localStorage.removeItem('hiremind_token')
      authAPI.removeAuthToken()
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload.user
        state.token = action.payload.token
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
        state.isAuthenticated = false
      })
      
      // Register
      .addCase(registerUser.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload.user
        state.token = action.payload.token
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
        state.isAuthenticated = false
      })
      
      // Get current user
      .addCase(getCurrentUser.pending, (state) => {
        state.loading = true
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload
        state.error = null
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      
      // Update profile
      .addCase(updateUserProfile.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(updateUserProfile.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload
        state.error = null
      })
      .addCase(updateUserProfile.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      
      // Change password
      .addCase(changePassword.pending, (state) => {
        state.loading = true
        state.error = null
      })
      .addCase(changePassword.fulfilled, (state) => {
        state.loading = false
        state.error = null
      })
      .addCase(changePassword.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      
      // Logout
      .addCase(logoutUser.fulfilled, (state) => {
        state.user = null
        state.token = null
        state.isAuthenticated = false
        state.loading = false
        state.error = null
      })
      
      // Validate token
      .addCase(validateToken.pending, (state) => {
        state.loading = true
      })
      .addCase(validateToken.fulfilled, (state, action) => {
        state.loading = false
        state.user = action.payload.user
        state.token = action.payload.token
        state.isAuthenticated = true
        state.error = null
      })
      .addCase(validateToken.rejected, (state, action) => {
        state.loading = false
        state.user = null
        state.token = null
        state.isAuthenticated = false
        state.error = action.payload as string
      })
  },
})

export const { clearError, clearAuth } = authSlice.actions
export default authSlice.reducer