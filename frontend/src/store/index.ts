import { configureStore } from '@reduxjs/toolkit'
import workflowReducer from './workflowSlice'
import uiReducer from './uiSlice'
import authReducer from './authSlice'

export const store = configureStore({
  reducer: {
    workflow: workflowReducer,
    ui: uiReducer,
    auth: authReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch