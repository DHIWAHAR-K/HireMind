import React, { useState } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  Button,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  CircularProgress,
  Alert,
  Fade,
  Chip,
  LinearProgress,
  IconButton,
} from '@mui/material'
import { 
  Send as SendIcon, 
  AutoAwesome as AutoAwesomeIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  PlayCircle as PlayCircleIcon,
  Menu as MenuIcon
} from '@mui/icons-material'
import { useDispatch, useSelector } from 'react-redux'
import { useNavigate } from 'react-router-dom'
import { RootState } from '../store'
import { startWorkflow, getWorkflowStatus } from '../store/workflowSlice'
import { toggleSidebar } from '../store/uiSlice'
import { AppDispatch } from '../store'

const steps = [
  { 
    label: 'Role Definition',
    description: 'Analyzing role requirements and defining the position'
  },
  { 
    label: 'Job Description',
    description: 'Creating comprehensive job description and requirements'
  },
  { 
    label: 'Interview Planning',
    description: 'Designing interview process and assessment criteria'
  },
  { 
    label: 'Timeline Estimation',
    description: 'Calculating hiring timeline and key milestones'
  },
  { 
    label: 'Salary Benchmarking',
    description: 'Researching market salary ranges and compensation'
  },
  { 
    label: 'Offer Generation',
    description: 'Generating professional offer letter template'
  },
]

export default function NewHiring() {
  const [description, setDescription] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [department, setDepartment] = useState('')
  const [currentStep, setCurrentStep] = useState(0)
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null)
  const dispatch = useDispatch<AppDispatch>()
  const navigate = useNavigate()
  const { status, error, sessionId, completedStages } = useSelector(
    (state: RootState) => state.workflow
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!description.trim() || !companyName.trim()) return

    try {
      const result = await dispatch(startWorkflow({
        description,
        company_name: companyName,
        department: department || undefined
      }))
      if (startWorkflow.fulfilled.match(result)) {
        // Clear any existing polling interval
        if (pollingInterval) {
          clearInterval(pollingInterval)
        }
        // Start polling for progress updates
        const sessionId = result.payload.session_id
        const interval = startProgressPolling(sessionId)
        setPollingInterval(interval)
      }
    } catch (error) {
      console.error('Failed to start workflow:', error)
    }
  }

  const startProgressPolling = (sessionId: string) => {
    let pollCount = 0
    const maxPolls = 90 // Maximum 90 polls (3 minutes at 2s intervals)
    
    const pollInterval = setInterval(async () => {
      try {
        pollCount++
        
        // Stop polling if we've exceeded max polls
        if (pollCount > maxPolls) {
          console.log('Max polling attempts reached, stopping...')
          clearInterval(pollInterval)
          return
        }
        
        const statusResult = await dispatch(getWorkflowStatus(sessionId))
        if (getWorkflowStatus.fulfilled.match(statusResult)) {
          const { status: workflowStatus, completed_stages } = statusResult.payload
          
          // Update current step based on completed stages
          if (completed_stages && completed_stages.length >= 0) {
            setCurrentStep(completed_stages.length)
          }
          
          // If workflow is completed or failed, stop polling
          if (workflowStatus === 'completed' || workflowStatus === 'failed') {
            console.log(`Workflow ${workflowStatus}, stopping polling...`)
            clearInterval(pollInterval)
            setPollingInterval(null)
            
            if (workflowStatus === 'completed') {
              console.log('Navigating to results page...')
              navigate(`/hiring/${sessionId}`)
            }
            return
          }
        }
      } catch (error) {
        console.error('Error polling workflow status:', error)
        clearInterval(pollInterval)
      }
    }, 2000) // Poll every 2 seconds for responsive updates

    // Store interval reference for cleanup
    return pollInterval
  }

  // Update current step based on completed stages
  React.useEffect(() => {
    if (completedStages.length > 0) {
      setCurrentStep(completedStages.length)
    }
  }, [completedStages])

  // Cleanup polling interval on component unmount
  React.useEffect(() => {
    return () => {
      if (pollingInterval) {
        console.log('Cleaning up polling interval on unmount')
        clearInterval(pollingInterval)
      }
    }
  }, [pollingInterval])

  // Stop polling and navigate when workflow succeeds
  React.useEffect(() => {
    if (status === 'succeeded' && sessionId && pollingInterval) {
      console.log('Workflow succeeded, stopping polling and navigating...')
      clearInterval(pollingInterval)
      setPollingInterval(null)
      navigate(`/hiring/${sessionId}`)
    }
  }, [status, sessionId, pollingInterval, navigate])

  const examples = [
    "We need a Senior Backend Engineer for our fintech startup. Should have 5+ years experience with Python, AWS, and microservices. Will lead our payment processing team.",
    "Looking for a Product Manager to drive our mobile app strategy. Need someone with B2C experience, data-driven mindset, and strong stakeholder management skills.",
    "Hiring a Data Scientist for our AI/ML team. Requirements: PhD or Masters in relevant field, experience with deep learning, and Python/TensorFlow expertise.",
    "Need a Frontend Engineer to build our React dashboard. Looking for someone with 3+ years React experience, TypeScript, and design system knowledge."
  ]

  const handleExampleClick = (example: string) => {
    setDescription(example)
  }

  return (
    <Box sx={{ 
      width: '100%',
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      bgcolor: 'background.default',
      overflow: 'hidden',
    }}>
      {/* Header Section */}
      <Box sx={{ 
        px: 2,
        py: 2,
        borderBottom: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
        flexShrink: 0,
        width: '100%',
      }}>
        <Box sx={{ 
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          width: '100%',
        }}>
          <IconButton
            edge="start"
            color="inherit"
            onClick={() => dispatch(toggleSidebar())}
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          <Box>
            <Typography variant="h1" component="h1" sx={{ mb: 0.5 }}>
              Start New Hiring Process
            </Typography>
            <Typography variant="body2" color="text.secondary">
              AI-powered hiring process planning
            </Typography>
          </Box>
          <Box sx={{ minWidth: 120 }} />
        </Box>
      </Box>

      {/* Scrollable Content */}
      <Box sx={{ 
        flex: 1,
        overflow: 'auto',
        p: 2,
        width: '100%',
      }}>

      {status === 'loading' && (
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <CircularProgress size={24} />
              <Box>
                <Typography variant="h6">
                  Processing your hiring request...
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {currentStep < steps.length ? steps[currentStep].description : 'Finalizing results...'}
                </Typography>
              </Box>
            </Box>
            
            <LinearProgress 
              variant="determinate" 
              value={(currentStep / steps.length) * 100} 
              sx={{ mb: 3, height: 8, borderRadius: 4 }}
            />
            
            <Stepper activeStep={currentStep} orientation="vertical">
              {steps.map((step, index) => (
                <Step key={step.label}>
                  <StepLabel 
                    StepIconComponent={() => {
                      if (index < currentStep) {
                        return <CheckCircleIcon color="success" />
                      } else if (index === currentStep) {
                        return <CircularProgress size={20} />
                      } else {
                        return <ScheduleIcon color="disabled" />
                      }
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="subtitle1">{step.label}</Typography>
                      {index < currentStep && (
                        <Chip 
                          label="Completed" 
                          size="small" 
                          color="success" 
                          variant="outlined"
                        />
                      )}
                      {index === currentStep && (
                        <Chip 
                          label="In Progress" 
                          size="small" 
                          color="primary" 
                          variant="outlined"
                        />
                      )}
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      {step.description}
                    </Typography>
                  </StepLabel>
                </Step>
              ))}
            </Stepper>
          </CardContent>
        </Card>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
      )}

      <Card>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <Typography variant="h6" gutterBottom>
              Company & Role Information
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Start by providing your company details and a detailed description of the role you want to hire for.
            </Typography>
            
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <TextField
                fullWidth
                label="Company Name"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                placeholder="e.g., Acme Corp"
                disabled={status === 'loading'}
                required
              />
              <TextField
                fullWidth
                label="Department (Optional)"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                placeholder="e.g., Engineering, Marketing"
                disabled={status === 'loading'}
              />
            </Box>

            <Typography variant="subtitle1" gutterBottom>
              Role Description
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={6}
              label="Describe the Role"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Example: We need a Senior Software Engineer for our e-commerce platform. Looking for someone with 5+ years of experience in React, Node.js, and AWS. The role involves leading a team of 3 developers and architecting scalable solutions for high-traffic applications..."
              disabled={status === 'loading'}
              sx={{ mb: 3 }}
              required
            />

            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                startIcon={status === 'loading' ? <CircularProgress size={20} /> : <AutoAwesomeIcon />}
                disabled={!description.trim() || !companyName.trim() || status === 'loading'}
              >
                {status === 'loading' ? 'Processing...' : 'Generate Hiring Plan'}
              </Button>
            </Box>
          </form>
        </CardContent>
      </Card>

        {/* Examples Section */}
        <Card sx={{ mt: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Need inspiration? Try these examples:
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {examples.map((example, index) => (
                <Box
                  key={index}
                  sx={{
                    p: 2,
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    cursor: 'pointer',
                    transition: 'all 0.2s',
                    '&:hover': {
                      borderColor: 'primary.main',
                      backgroundColor: 'action.hover',
                    },
                  }}
                  onClick={() => handleExampleClick(example)}
                >
                  <Typography variant="body2" color="text.secondary">
                    {example}
                  </Typography>
                </Box>
              ))}
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Box>
  )
}