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
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  Download as DownloadIcon,
  Share as ShareIcon,
} from '@mui/icons-material'
import { useParams } from 'react-router-dom'
import { useQuery } from 'react-query'
import { profilesAPI } from '../services/api'
import ReactMarkdown from 'react-markdown'

export default function HiringDetails() {
  const { sessionId } = useParams<{ sessionId: string }>()

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
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <Typography>Loading hiring details...</Typography>
      </Box>
    )
  }

  if (error || !profile) {
    return (
      <Box sx={{ mt: 4 }}>
        <Typography color="error">Failed to load hiring details</Typography>
      </Box>
    )
  }

  const results = profile.results || profile

  return (
    <Box>
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Hiring Plan Details
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Session: {sessionId}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button startIcon={<ShareIcon />} variant="outlined">
            Share
          </Button>
          <Button startIcon={<DownloadIcon />} variant="contained">
            Export PDF
          </Button>
        </Box>
      </Box>

      {/* Status Overview */}
      <Card sx={{ mb: 4 }}>
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
                    <ReactMarkdown>
                      {results.role_definition.output || results.role_definition}
                    </ReactMarkdown>
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
                    <ReactMarkdown>
                      {results.job_description}
                    </ReactMarkdown>
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
                    <ReactMarkdown>
                      {results.interview_plan.output || results.interview_plan}
                    </ReactMarkdown>
                  </CardContent>
                </Card>
              </AccordionDetails>
            </Accordion>
          </Grid>
        )}

        {/* Timeline */}
        {results.timeline && (
          <Grid item xs={12} md={6}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Timeline Estimation</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Card variant="outlined">
                  <CardContent>
                    <ReactMarkdown>
                      {results.timeline.output || results.timeline}
                    </ReactMarkdown>
                  </CardContent>
                </Card>
              </AccordionDetails>
            </Accordion>
          </Grid>
        )}

        {/* Salary Benchmark */}
        {results.salary_benchmark && (
          <Grid item xs={12} md={6}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="h6">Salary Benchmark</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Card variant="outlined">
                  <CardContent>
                    <ReactMarkdown>
                      {results.salary_benchmark.output || results.salary_benchmark}
                    </ReactMarkdown>
                  </CardContent>
                </Card>
              </AccordionDetails>
            </Accordion>
          </Grid>
        )}

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
                      {results.offer_letter}
                    </Box>
                  </CardContent>
                </Card>
              </AccordionDetails>
            </Accordion>
          </Grid>
        )}
      </Grid>
    </Box>
  )
}