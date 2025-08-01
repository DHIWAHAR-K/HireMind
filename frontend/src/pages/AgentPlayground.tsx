import React, { useState } from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Paper,
  CircularProgress,
  Alert,
  Divider,
  IconButton,
} from '@mui/material'
import {
  Send as SendIcon,
  Clear as ClearIcon,
  Psychology as PsychologyIcon,
  Menu as MenuIcon,
} from '@mui/icons-material'
import { useDispatch, useSelector } from 'react-redux'
import { RootState } from '../store'
import { runAgent } from '../store/workflowSlice'
import { toggleSidebar } from '../store/uiSlice'
import { AppDispatch } from '../store'

// Helper function to clean markdown symbols
const cleanMarkdownText = (text: string): string => {
  if (!text) return ''
  // Remove # headers, * bullets, ** bold, etc
  return text
    .replace(/#{1,6}\s/g, '') // Remove headers
    .replace(/\*{1,2}/g, '')   // Remove * and **
    .replace(/^\s*[-*+]\s/gm, '') // Remove bullet points
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Convert links to plain text
    .trim()
}

const agents = [
  { value: 'role_definition', label: 'Role Definition Agent', description: 'Define job roles and requirements' },
  { value: 'jd_generator', label: 'JD Generator Agent', description: 'Create compelling job descriptions' },
  { value: 'interview_planner', label: 'Interview Planner Agent', description: 'Design interview processes' },
]

const examples = {
  role_definition: [
    "Define a Senior Software Engineer role for a fintech startup",
    "Help me scope a Product Manager position for our e-commerce team",
    "What should I look for in a Data Scientist for AI/ML projects?",
  ],
  jd_generator: [
    "Create a JD for: Senior Backend Engineer, Python/AWS, 5+ years experience, fintech domain",
    "Write a job description for a UX Designer position at a B2B SaaS company",
    "Generate JD for Marketing Manager role focusing on digital marketing and growth",
  ],
  interview_planner: [
    "Plan interview stages for a Senior Full-Stack Developer position",
    "Design interview process for VP of Engineering role",
    "Create evaluation criteria for a Data Science Manager interview",
  ],
}

export default function AgentPlayground() {
  const [selectedAgent, setSelectedAgent] = useState('')
  const [inputText, setInputText] = useState('')
  const [responses, setResponses] = useState<Array<{
    agent: string
    input: string
    output: string
    timestamp: string
  }>>([])

  const dispatch = useDispatch<AppDispatch>()
  const { status, error } = useSelector((state: RootState) => state.workflow)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedAgent || !inputText.trim()) return

    try {
      const result = await dispatch(runAgent({
        agentType: selectedAgent,
        inputText: inputText.trim(),
      }))

      if (runAgent.fulfilled.match(result)) {
        const newResponse = {
          agent: selectedAgent,
          input: inputText.trim(),
          output: result.payload.output,
          timestamp: new Date().toISOString(),
        }
        setResponses(prev => [newResponse, ...prev])
        setInputText('')
      }
    } catch (error) {
      console.error('Failed to run agent:', error)
    }
  }

  const handleExampleClick = (example: string) => {
    setInputText(example)
  }

  const handleClear = () => {
    setResponses([])
  }

  const currentAgent = agents.find(agent => agent.value === selectedAgent)

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
              Agent Playground
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Test individual agents and interactions
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
        <Grid container spacing={3} sx={{ height: 'calc(100vh - 140px)' }}>
        {/* Input Section */}
        <Grid item xs={12} md={6} sx={{ height: '100%' }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', gap: 3 }}>
            <Card sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
              <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                <Typography variant="h6" gutterBottom>
                  Agent Input
                </Typography>
                
                <form onSubmit={handleSubmit} style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <FormControl fullWidth sx={{ mb: 3 }}>
                    <InputLabel>Select Agent</InputLabel>
                    <Select
                      value={selectedAgent}
                      label="Select Agent"
                      onChange={(e) => setSelectedAgent(e.target.value)}
                    >
                      {agents.map((agent) => (
                        <MenuItem key={agent.value} value={agent.value}>
                          <Box>
                            <Typography variant="subtitle2">{agent.label}</Typography>
                            <Typography variant="caption" color="text.secondary">
                              {agent.description}
                            </Typography>
                          </Box>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  <TextField
                    fullWidth
                    multiline
                    rows={8}
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="Enter your request for the agent..."
                    disabled={status === 'loading' || !selectedAgent}
                    sx={{ 
                      mb: 3, 
                      flex: 1,
                      '& .MuiInputBase-root': {
                        maxHeight: '300px',
                        overflow: 'auto',
                        scrollBehavior: 'smooth',
                        '&::-webkit-scrollbar': {
                          width: '6px',
                        },
                        '&::-webkit-scrollbar-track': {
                          backgroundColor: '#f1f1f1',
                          borderRadius: '3px',
                        },
                        '&::-webkit-scrollbar-thumb': {
                          backgroundColor: '#c1c1c1',
                          borderRadius: '3px',
                          '&:hover': {
                            backgroundColor: '#a8a8a8',
                          },
                        },
                        '&::-webkit-scrollbar-corner': {
                          backgroundColor: 'transparent',
                        },
                        // Firefox scrollbar styling
                        scrollbarWidth: 'thin',
                        scrollbarColor: '#c1c1c1 #f1f1f1',
                      }
                    }}
                  />

                  <Box sx={{ display: 'flex', gap: 2, mt: 'auto' }}>
                    <Button
                      type="submit"
                      variant="contained"
                      startIcon={status === 'loading' ? <CircularProgress size={20} /> : <SendIcon />}
                      disabled={!selectedAgent || !inputText.trim() || status === 'loading'}
                    >
                      {status === 'loading' ? 'Processing...' : 'Run Agent'}
                    </Button>
                    <Button
                      variant="outlined"
                      startIcon={<ClearIcon />}
                      onClick={handleClear}
                      disabled={responses.length === 0}
                    >
                      Clear History
                    </Button>
                  </Box>
                </form>

                {error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {error}
                  </Alert>
                )}
              </CardContent>
            </Card>

            {/* Examples */}
            {selectedAgent && examples[selectedAgent as keyof typeof examples] && (
              <Card sx={{ maxHeight: '250px', overflow: 'hidden' }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Example Prompts for {currentAgent?.label}
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, maxHeight: '180px', overflowY: 'auto' }}>
                    {examples[selectedAgent as keyof typeof examples].map((example, index) => (
                      <Paper
                        key={index}
                        sx={{
                          p: 2,
                          cursor: 'pointer',
                          border: 1,
                          borderColor: 'divider',
                          '&:hover': {
                            borderColor: 'primary.main',
                            backgroundColor: 'action.hover',
                          },
                        }}
                        onClick={() => handleExampleClick(example)}
                      >
                        <Typography variant="body2">{example}</Typography>
                      </Paper>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            )}
          </Box>
        </Grid>

        {/* Responses Section */}
        <Grid item xs={12} md={6} sx={{ height: '100%' }}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <CardContent sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <PsychologyIcon color="primary" />
                <Typography variant="h6">Agent Responses</Typography>
              </Box>

              {responses.length === 0 ? (
                <Box sx={{ textAlign: 'center', py: 4, flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    No responses yet. Select an agent and ask a question to get started.
                  </Typography>
                </Box>
              ) : (
                <Box sx={{ 
                  flex: 1, 
                  overflowY: 'auto',
                  overflowX: 'hidden', // Prevent horizontal scroll
                  pr: 1,
                  minHeight: 0, // Important: allows flex child to shrink below content size
                  maxHeight: '100%', // Ensure it doesn't exceed container
                  scrollBehavior: 'smooth', // Smooth scrolling
                  '&::-webkit-scrollbar': {
                    width: '8px',
                  },
                  '&::-webkit-scrollbar-track': {
                    backgroundColor: '#f1f1f1',
                    borderRadius: '4px',
                  },
                  '&::-webkit-scrollbar-thumb': {
                    backgroundColor: '#c1c1c1',
                    borderRadius: '4px',
                    '&:hover': {
                      backgroundColor: '#a8a8a8',
                    },
                  },
                  '&::-webkit-scrollbar-corner': {
                    backgroundColor: 'transparent',
                  },
                  // Firefox scrollbar styling
                  scrollbarWidth: 'thin',
                  scrollbarColor: '#c1c1c1 #f1f1f1',
                }}>
                  {responses.map((response, index) => (
                    <Box key={index} sx={{ mb: 3 }}>
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="subtitle2" color="primary">
                          {agents.find(a => a.value === response.agent)?.label}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {new Date(response.timestamp).toLocaleString()}
                        </Typography>
                      </Box>
                      
                      <Paper
                        sx={{
                          p: 2,
                          mb: 1,
                          backgroundColor: 'grey.50',
                          borderLeft: 3,
                          borderColor: 'primary.main',
                        }}
                      >
                        <Typography variant="body2" fontWeight="medium" gutterBottom>
                          Input:
                        </Typography>
                        <Typography variant="body2" sx={{ wordBreak: 'break-word' }}>
                          {response.input}
                        </Typography>
                      </Paper>
                      
                      <Paper
                        sx={{
                          p: 2,
                          backgroundColor: 'background.paper',
                          border: 1,
                          borderColor: 'divider',
                          minHeight: '300px', // Ensure minimum height
                          display: 'flex',
                          flexDirection: 'column',
                        }}
                      >
                        <Typography variant="body2" fontWeight="medium" gutterBottom>
                          Response:
                        </Typography>
                        <Box 
                          component="div"
                          sx={{ 
                            whiteSpace: 'pre-wrap',
                            fontFamily: 'inherit',
                            fontSize: 'inherit',
                            m: 0,
                            flex: 1, // Take up remaining space
                            overflowY: 'auto',
                            overflowX: 'hidden', // Prevent horizontal scroll
                            wordBreak: 'break-word',
                            lineHeight: 1.6,
                            padding: 1,
                            backgroundColor: '#fafafa',
                            borderRadius: 1,
                            border: '1px solid #e0e0e0',
                            minHeight: '250px', // Ensure content area has good height
                            maxHeight: '400px', // Add max height to trigger scroll when needed
                            scrollBehavior: 'smooth', // Smooth scrolling
                            cursor: 'text', // Show text cursor for better UX
                            '&::-webkit-scrollbar': {
                              width: '6px',
                            },
                            '&::-webkit-scrollbar-track': {
                              backgroundColor: '#f1f1f1',
                              borderRadius: '3px',
                            },
                            '&::-webkit-scrollbar-thumb': {
                              backgroundColor: '#c1c1c1',
                              borderRadius: '3px',
                              '&:hover': {
                                backgroundColor: '#a8a8a8',
                              },
                            },
                            '&::-webkit-scrollbar-corner': {
                              backgroundColor: 'transparent',
                            },
                            // Firefox scrollbar styling
                            scrollbarWidth: 'thin',
                            scrollbarColor: '#c1c1c1 #f1f1f1',
                            // Hover effects for better interaction feedback
                            '&:hover': {
                              backgroundColor: '#f5f5f5',
                            },
                            // Focus styling for accessibility
                            '&:focus-within': {
                              outline: '2px solid #1976d2',
                              outlineOffset: '2px',
                            },
                          }}
                        >
                          {cleanMarkdownText(response.output)}
                        </Box>
                      </Paper>
                      
                      {index < responses.length - 1 && <Divider sx={{ mt: 2 }} />}
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
          </Grid>
        </Grid>
      </Box>
    </Box>
  )
}