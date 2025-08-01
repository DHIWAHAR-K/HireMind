import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'
import { useDispatch } from 'react-redux'

import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import NewHiring from './pages/NewHiring'
import HiringDetails from './pages/HiringDetails'
import Profiles from './pages/Profiles'
import AgentPlayground from './pages/AgentPlayground'
import { AppDispatch } from './store'
import { validateToken } from './store/authSlice'

function App() {
  const dispatch = useDispatch<AppDispatch>()

  // Check for existing token on app startup
  useEffect(() => {
    const token = localStorage.getItem('hiremind_token')
    if (token) {
      dispatch(validateToken())
    }
  }, [dispatch])

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      {/* Protected Routes */}
      <Route path="/*" element={
        <ProtectedRoute>
          <Box sx={{ display: 'flex', minHeight: '100vh' }}>
            <Layout>
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" />} />
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/new-hiring" element={<NewHiring />} />
                <Route path="/hiring/:sessionId" element={<HiringDetails />} />
                <Route path="/profiles" element={<Profiles />} />
                <Route path="/playground" element={<AgentPlayground />} />
              </Routes>
            </Layout>
          </Box>
        </ProtectedRoute>
      } />
    </Routes>
  )
}

export default App