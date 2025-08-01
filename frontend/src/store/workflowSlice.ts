import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import { workflowAPI, agentAPI } from '../services/api'

export interface WorkflowState {
  sessionId: string | null
  status: 'idle' | 'loading' | 'succeeded' | 'failed'
  currentStage: string | null
  completedStages: string[]
  results: any
  error: string | null
}

const initialState: WorkflowState = {
  sessionId: null,
  status: 'idle',
  currentStage: null,
  completedStages: [],
  results: null,
  error: null,
}

// Async thunks
export const startWorkflow = createAsyncThunk(
  'workflow/start',
  async (params: { description: string; company_name: string; department?: string }) => {
    const response = await workflowAPI.start(params)
    return response.data
  }
)

export const getWorkflowStatus = createAsyncThunk(
  'workflow/getStatus',
  async (sessionId: string) => {
    const response = await workflowAPI.getStatus(sessionId)
    return response.data
  }
)

export const runAgent = createAsyncThunk(
  'workflow/runAgent',
  async ({ agentType, inputText, sessionId }: { 
    agentType: string; 
    inputText: string; 
    sessionId?: string 
  }) => {
    const response = await agentAPI.run(agentType, inputText, sessionId)
    return response.data
  }
)

const workflowSlice = createSlice({
  name: 'workflow',
  initialState,
  reducers: {
    clearWorkflow: (state) => {
      state.sessionId = null
      state.status = 'idle'
      state.currentStage = null
      state.completedStages = []
      state.results = null
      state.error = null
    },
    setSessionId: (state, action: PayloadAction<string>) => {
      state.sessionId = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      // Start workflow
      .addCase(startWorkflow.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(startWorkflow.fulfilled, (state, action) => {
        state.status = 'loading' // Keep loading status while processing
        state.sessionId = action.payload.session_id
        state.currentStage = action.payload.current_stage
        state.completedStages = action.payload.completed_stages
        state.results = action.payload.results
        state.error = action.payload.error
      })
      .addCase(startWorkflow.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.error.message || 'Failed to start workflow'
      })
      
      // Get workflow status
      .addCase(getWorkflowStatus.fulfilled, (state, action) => {
        state.currentStage = action.payload.current_stage
        state.completedStages = action.payload.completed_stages
        state.results = action.payload.results
        state.error = action.payload.error
        // Update status based on workflow state
        if (action.payload.status === 'completed') {
          state.status = 'succeeded'
        } else if (action.payload.status === 'failed') {
          state.status = 'failed'
        } else {
          state.status = 'loading' // Keep loading status while processing
        }
      })
      
      // Run agent
      .addCase(runAgent.pending, (state) => {
        state.status = 'loading'
        state.error = null
      })
      .addCase(runAgent.fulfilled, (state, action) => {
        state.status = 'succeeded'
        if (action.payload.session_id && !state.sessionId) {
          state.sessionId = action.payload.session_id
        }
        state.error = action.payload.error
      })
      .addCase(runAgent.rejected, (state, action) => {
        state.status = 'failed'
        state.error = action.error.message || 'Failed to run agent'
      })
  },
})

export const { clearWorkflow, setSessionId } = workflowSlice.actions
export default workflowSlice.reducer