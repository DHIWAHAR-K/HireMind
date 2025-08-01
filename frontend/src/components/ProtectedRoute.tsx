import React, { useEffect } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { Box, CircularProgress, Typography } from '@mui/material'
import { RootState, AppDispatch } from '../store'
import { validateToken } from '../store/authSlice'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const dispatch = useDispatch<AppDispatch>()
  const location = useLocation()
  const { isAuthenticated, loading, token } = useSelector((state: RootState) => state.auth)

  useEffect(() => {
    // If we have a token in localStorage but not authenticated, validate it
    if (token && !isAuthenticated && !loading) {
      dispatch(validateToken())
    }
  }, [dispatch, token, isAuthenticated, loading])

  // Show loading spinner while validating token
  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2,
        }}
      >
        <CircularProgress size={48} />
        <Typography variant="body1" color="text.secondary">
          Authenticating...
        </Typography>
      </Box>
    )
  }

  // If not authenticated, redirect to login with the current location
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // If authenticated, render the children
  return <>{children}</>
}