import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'

import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import NewHiring from './pages/NewHiring'
import HiringDetails from './pages/HiringDetails'
import Profiles from './pages/Profiles'
import AgentPlayground from './pages/AgentPlayground'

function App() {
  return (
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
  )
}

export default App