import React from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
  Divider,
  IconButton,
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
  Menu as MenuIcon,
} from '@mui/icons-material'
import { useParams } from 'react-router-dom'
import { useQuery } from 'react-query'
import { useDispatch } from 'react-redux'
import { profilesAPI } from '../services/api'
import { toggleSidebar } from '../store/uiSlice'
import ReactMarkdown from 'react-markdown'

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

export default function HiringDetails() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const dispatch = useDispatch()

  const { data: profile, isLoading, error } = useQuery(
    ['profile', sessionId],
    () => profilesAPI.get(sessionId!),
    {
      enabled: !!sessionId,
      select: (response) => response.data,
    }
  )

  if (isLoading) {
    return (
      <Box sx={{ 
        width: '100%',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
      }}>
        <Typography>Loading hiring details...</Typography>
      </Box>
    )
  }

  if (error || !profile) {
    return (
      <Box sx={{ 
        width: '100%',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: 'background.default',
      }}>
        <Typography color="error">Failed to load hiring details</Typography>
      </Box>
    )
  }

  const results = profile.results || profile

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
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton
              edge="start"
              color="inherit"
              onClick={() => dispatch(toggleSidebar())}
              sx={{ mr: 1 }}
            >
              <MenuIcon />
            </IconButton>
            <Box>
              <Typography variant="h1" component="h1" sx={{ mb: 0.5 }}>
                Hiring Plan Details
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Session: {sessionId}
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button startIcon={<ShareIcon />} variant="outlined" size="small">
              Share
            </Button>
            <Button startIcon={<DownloadIcon />} variant="contained" size="small">
              Export PDF
            </Button>
          </Box>
        </Box>
      </Box>

      {/* Scrollable Content */}
      <Box sx={{ 
        flex: 1,
        overflow: 'auto',
        p: 2,
        width: '100%',
      }}>

        {/* Status Overview */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Process Overview
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {results.completed_stages?.map((stage: string) => (
                <Chip
                  key={stage}
                  label={stage.replace('_', ' ').toUpperCase()}
                  color="success"
                  variant="filled"
                />
              ))}
            </Box>
          </CardContent>
        </Card>

        <Grid container spacing={3}>
        {/* Role Definition */}
        {results.role_definition && (
          <Grid item xs={12}>
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Role Definition</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Card variant="outlined">
                  <CardContent>
                    <Box component="pre" sx={{ 
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'inherit',
                      fontSize: 'inherit',
                      m: 0
                    }}>
                      {cleanMarkdownText(results.role_definition.output || results.role_definition)}
                    </Box>
                  </CardContent>
                </Card>
              </AccordionDetails>
            </Accordion>
          </Grid>
        )}

        {/* Job Description */}
        {results.job_description && (
          <Grid item xs={12}>
            <Accordion defaultExpanded>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Job Description</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Card variant="outlined">
                  <CardContent>
                    <Box component="pre" sx={{ 
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'inherit',
                      fontSize: 'inherit',
                      m: 0
                    }}>
                      {cleanMarkdownText(results.job_description)}
                    </Box>
                  </CardContent>
                </Card>
              </AccordionDetails>
            </Accordion>
          </Grid>
        )}

        {/* Interview Plan */}
        {results.interview_plan && (
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Interview Plan</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Card variant="outlined">
                  <CardContent>
                    <Box component="pre" sx={{ 
                      whiteSpace: 'pre-wrap',
                      fontFamily: 'inherit',
                      fontSize: 'inherit',
                      m: 0
                    }}>
                      {cleanMarkdownText(results.interview_plan.output || results.interview_plan)}
                    </Box>
                  </CardContent>
                </Card>
              </AccordionDetails>
            </Accordion>
          </Grid>
        )}

        {/* Timeline and Salary - Equal Height */}
        <Grid item xs={12}>
          <Grid container spacing={3}>
            {/* Timeline */}
            {results.timeline && (
              <Grid item xs={12} md={6}>
                <Accordion sx={{ height: '100%' }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">Timeline Estimation</Typography>
                  </AccordionSummary>
                  <AccordionDetails sx={{ height: 'calc(100% - 48px)' }}>
                    <Card variant="outlined" sx={{ height: '100%' }}>
                      <CardContent sx={{ 
                        height: '100%',
                        maxHeight: '400px',
                        overflow: 'auto'
                      }}>
                        <Box component="pre" sx={{ 
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'inherit',
                          fontSize: 'inherit',
                          m: 0
                        }}>
                          {cleanMarkdownText(results.timeline.output || results.timeline)}
                        </Box>
                      </CardContent>
                    </Card>
                  </AccordionDetails>
                </Accordion>
              </Grid>
            )}

            {/* Salary Benchmark */}
            {results.salary_benchmark && (
              <Grid item xs={12} md={6}>
                <Accordion sx={{ height: '100%' }}>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography variant="h6">Salary Benchmark</Typography>
                  </AccordionSummary>
                  <AccordionDetails sx={{ height: 'calc(100% - 48px)' }}>
                    <Card variant="outlined" sx={{ height: '100%' }}>
                      <CardContent sx={{ 
                        height: '100%',
                        maxHeight: '400px',
                        overflow: 'auto'
                      }}>
                        <Box component="pre" sx={{ 
                          whiteSpace: 'pre-wrap',
                          fontFamily: 'inherit',
                          fontSize: 'inherit',
                          m: 0
                        }}>
                          {cleanMarkdownText(results.salary_benchmark.output || results.salary_benchmark)}
                        </Box>
                      </CardContent>
                    </Card>
                  </AccordionDetails>
                </Accordion>
              </Grid>
            )}
          </Grid>
        </Grid>

        {/* Offer Letter */}
        {results.offer_letter && (
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Offer Letter Template</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ fontFamily: 'monospace', whiteSpace: 'pre-wrap' }}>
                      {cleanMarkdownText(results.offer_letter)}
                    </Box>
                  </CardContent>
                </Card>
              </AccordionDetails>
            </Accordion>
          </Grid>
        )}
        </Grid>
      </Box>
    </Box>
  )
}