import React from 'react'
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Avatar,
  Fade,
  IconButton,
} from '@mui/material'
import {
  Add as AddIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  CheckCircle as CheckCircleIcon,
  Rocket as RocketIcon,
  Analytics as AnalyticsIcon,
  Speed as SpeedIcon,
  Star as StarIcon,
  Menu as MenuIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useQuery } from 'react-query'
import { useDispatch } from 'react-redux'
import { profilesAPI } from '../services/api'
import { toggleSidebar } from '../store/uiSlice'

export default function Dashboard() {
  const navigate = useNavigate()
  const dispatch = useDispatch()

  const { data: profilesData, isLoading } = useQuery(
    'recent-profiles',
    () => profilesAPI.list(5),
    {
      select: (response) => response.data,
    }
  )

  const stats = [
    {
      title: 'Active Hirings',
      value: profilesData?.profiles?.filter((p: any) => p.status === 'active')?.length || 12,
      icon: <RocketIcon />,
      trend: '+23%',
    },
    {
      title: 'Completed',
      value: profilesData?.profiles?.filter((p: any) => p.status === 'completed')?.length || 8,
      icon: <CheckCircleIcon />,
      trend: '+18%',
    },
    {
      title: 'In Progress',
      value: profilesData?.profiles?.filter((p: any) => p.status === 'draft')?.length || 5,
      icon: <SpeedIcon />,
      trend: '+12%',
    },
    {
      title: 'Total Profiles',
      value: profilesData?.total || 25,
      icon: <AnalyticsIcon />,
      trend: '+31%',
    },
  ]

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
              Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              AI-powered hiring management
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/new-hiring')}
            sx={{ flexShrink: 0 }}
          >
            New Hiring
          </Button>
        </Box>
      </Box>

      {/* Scrollable Content */}
      <Box sx={{ 
        flex: 1,
        overflow: 'auto',
        p: 0,
        m: 0,
        width: '100%',
      }}>

      {/* Stats Cards */}
      <Grid container spacing={0} sx={{ mb: 3, width: '100%', mx: 0 }}>
        {stats.map((stat, index) => (
          <Grid item xs={3} key={index}>
            <Card sx={{ 
              backgroundColor: 'background.paper',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 0,
              borderRight: index === stats.length - 1 ? '1px solid' : 'none',
              borderRightColor: 'divider',
              p: 3,
              height: '100%',
              minHeight: 140,
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              '&:hover': {
                borderColor: 'primary.main',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                zIndex: 1,
              }
            }}>
              <CardContent sx={{ p: 0 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Box sx={{ 
                    width: 40,
                    height: 40,
                    borderRadius: 2,
                    backgroundColor: 'grey.100',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    '& svg': {
                      fontSize: 20,
                      color: 'primary.main',
                    }
                  }}>
                    {stat.icon}
                  </Box>
                  <Chip 
                    label={stat.trend}
                    size="small"
                    sx={{ 
                      backgroundColor: 'success.main',
                      color: 'white',
                      fontWeight: 500,
                      fontSize: '0.75rem'
                    }}
                  />
                </Box>
                
                <Typography 
                  variant="h4" 
                  sx={{ 
                    fontWeight: 700,
                    color: 'text.primary',
                    mb: 0.5,
                  }}
                >
                  {stat.value}
                </Typography>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: 'text.secondary',
                    fontWeight: 500
                  }}
                >
                  {stat.title}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Main Content Area - Full Width Layout */}
      <Grid container spacing={0} sx={{ width: '100%', mx: 0, height: 'calc(100vh - 260px)' }}>
        
        {/* Recent Hiring Activities - Larger Section */}
        <Grid item xs={4} sx={{ pr: 0 }}>
          <Card sx={{ 
            backgroundColor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 0,
            borderRight: 'none',
            overflow: 'hidden',
            height: '100%'
          }}>
            <Box sx={{ 
              p: 2, 
              borderBottom: '1px solid',
              borderColor: 'divider',
              backgroundColor: 'background.paper'
            }}>
              <Typography variant="h6" fontWeight="600" sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.primary' }}>
                <StarIcon sx={{ color: 'primary.main' }} />
                Recent Hiring Activities
              </Typography>
            </Box>
            <CardContent sx={{ p: 0, height: 'calc(100% - 60px)', overflow: 'auto' }}>
              {isLoading ? (
                <Box sx={{ p: 4, textAlign: 'center' }}>
                  <Typography color="text.secondary">Loading hiring activities...</Typography>
                </Box>
              ) : profilesData?.profiles?.length ? (
                <List sx={{ p: 0 }}>
                  {profilesData?.profiles?.map((profile: any, index: number) => (
                    <Fade in={true} style={{ transitionDelay: `${index * 100}ms` }} key={profile.session_id}>
                      <ListItem
                        sx={{
                          cursor: 'pointer',
                          borderBottom: '1px solid rgba(0,0,0,0.05)',
                          transition: 'all 0.2s ease',
                          '&:hover': { 
                            backgroundColor: 'rgba(99, 102, 241, 0.05)',
                            transform: 'translateX(8px)',
                          },
                        }}
                        onClick={() => navigate(`/hiring/${profile.session_id}`)}
                      >
                        <ListItemIcon>
                          <Avatar sx={{ 
                            backgroundColor: 'primary.main',
                            color: 'white',
                            fontWeight: 'bold',
                            width: 32,
                            height: 32
                          }}>
                            {profile.role_title?.charAt(0) || 'H'}
                          </Avatar>
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                              <Typography variant="subtitle1" fontWeight="600">
                                {profile.role_title || 'New Hiring Process'}
                              </Typography>
                              <Chip
                                label={profile.status || 'Active'}
                                size="small"
                                sx={{
                                  backgroundColor: profile.status === 'completed' 
                                    ? 'success.main'
                                    : 'primary.main',
                                  color: 'white',
                                  fontWeight: 500
                                }}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                                🏢 {profile.department || 'Department not specified'}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                📅 Created: {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : new Date().toLocaleDateString()}
                              </Typography>
                            </Box>
                          }
                        />
                      </ListItem>
                    </Fade>
                  ))}
                </List>
              ) : (
                <Box sx={{ p: 4, textAlign: 'center' }}>
                  <Typography color="text.secondary" sx={{ mb: 2 }}>
                    🎯 No hiring activities yet
                  </Typography>
                  <Button 
                    variant="contained" 
                    onClick={() => navigate('/new-hiring')}
                  >
                    Start Your First Hiring Process
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions & Performance Metrics */}
        <Grid item xs={4} sx={{ px: 0 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
            {/* Quick Actions */}
            <Card sx={{ 
              backgroundColor: 'background.paper',
              border: '1px solid',
              borderColor: 'divider',
              borderRadius: 0,
              borderRight: 'none',
              borderLeft: 'none',
              flex: 1,
              mb: 0,
            }}>
              <Box sx={{ 
                p: 2, 
                borderBottom: '1px solid',
                borderColor: 'divider',
                backgroundColor: 'background.paper'
              }}>
                <Typography variant="h6" fontWeight="600" sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.primary' }}>
                  <RocketIcon sx={{ color: 'primary.main' }} />
                  Quick Actions
                </Typography>
              </Box>
              <CardContent sx={{ p: 2, height: 'calc(100% - 60px)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="contained"
                    fullWidth
                    startIcon={<AddIcon />}
                    onClick={() => navigate('/new-hiring')}
                    sx={{
                      py: 1.5,
                      fontWeight: 600,
                      borderRadius: 2,
                    }}
                  >
                    Start New Hiring Process
                  </Button>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<PeopleIcon />}
                      onClick={() => navigate('/profiles')}
                      sx={{
                        py: 1.5,
                        fontWeight: 600,
                        borderRadius: 2,
                        fontSize: '0.8rem',
                      }}
                    >
                      Profiles  
                    </Button>
                    <Button
                      variant="outlined"
                      fullWidth
                      startIcon={<TrendingUpIcon />}
                      onClick={() => navigate('/playground')}
                      sx={{
                        py: 1.5,
                        fontWeight: 600,
                        borderRadius: 2,
                        fontSize: '0.8rem',
                      }}
                    >
                      Playground
                    </Button>
                  </Box>
                </Box>
                
                {/* Performance Metrics Embedded */}
                <Box sx={{ mt: 3, pt: 3, borderTop: '1px solid', borderColor: 'divider' }}>
                  <Typography variant="h6" fontWeight="600" sx={{ color: 'text.primary', mb: 2 }}>
                    📊 This Month's Performance
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">Avg. Time to Hire</Typography>
                      <Typography variant="subtitle2" fontWeight="700">18 days</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">Success Rate</Typography>
                      <Typography variant="subtitle2" fontWeight="700" color="success.main">94%</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">Cost per Hire</Typography>
                      <Typography variant="subtitle2" fontWeight="700">$2,400</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="body2" color="text.secondary">Quality Score</Typography>
                      <Typography variant="subtitle2" fontWeight="700" color="primary.main">9.2/10</Typography>
                    </Box>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Box>
        </Grid>

        {/* Tips, Insights & Team Activity */}
        <Grid item xs={4} sx={{ pl: 0 }}>
          <Card sx={{ 
            backgroundColor: 'background.paper',
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 0,
            borderLeft: 'none',
            height: '100%',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <Box sx={{ 
              p: 2, 
              borderBottom: '1px solid',
              borderColor: 'divider',
              backgroundColor: 'background.paper'
            }}>
              <Typography variant="h6" fontWeight="600" sx={{ color: 'text.primary' }}>
                💡 AI Tips & Team Activity
              </Typography>
            </Box>
            <CardContent sx={{ p: 2, flex: 1, display: 'flex', flexDirection: 'column' }}>
              {/* AI Tips Section */}
              <Box sx={{ mb: 3 }}>
                <Typography variant="subtitle1" fontWeight="600" sx={{ color: 'text.primary', mb: 2 }}>
                  AI Tips & Insights
                </Typography>
                <List sx={{ p: 0 }}>
                  <ListItem sx={{ px: 0, py: 1 }}>
                    <ListItemIcon>
                      <Box sx={{ 
                        width: 6, 
                        height: 6, 
                        borderRadius: '50%', 
                        backgroundColor: 'primary.main' 
                      }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={<Typography variant="body2" fontWeight="600">🎯 Define clear requirements</Typography>}
                      secondary={<Typography variant="caption">40% more qualified candidates</Typography>}
                    />
                  </ListItem>
                  <ListItem sx={{ px: 0, py: 1 }}>
                    <ListItemIcon>
                      <Box sx={{ 
                        width: 6, 
                        height: 6, 
                        borderRadius: '50%', 
                        backgroundColor: 'primary.main' 
                      }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={<Typography variant="body2" fontWeight="600">📊 Structured interviews</Typography>}
                      secondary={<Typography variant="caption">25% better hiring accuracy</Typography>}
                    />
                  </ListItem>
                  <ListItem sx={{ px: 0, py: 1 }}>
                    <ListItemIcon>
                      <Box sx={{ 
                        width: 6, 
                        height: 6, 
                        borderRadius: '50%', 
                        backgroundColor: 'primary.main' 
                      }} />
                    </ListItemIcon>
                    <ListItemText
                      primary={<Typography variant="body2" fontWeight="600">⚡ Track metrics</Typography>}
                      secondary={<Typography variant="caption">Real-time hiring insights</Typography>}
                    />
                  </ListItem>
                </List>
              </Box>

              {/* Team Activity Section */}
              <Box sx={{ pt: 2, borderTop: '1px solid', borderColor: 'divider', flex: 1 }}>
                <Typography variant="subtitle1" fontWeight="600" sx={{ color: 'text.primary', mb: 2 }}>
                  👥 Team Activity
                </Typography>
                <List sx={{ p: 0 }}>
                  <ListItem sx={{ px: 0, py: 1 }}>
                    <ListItemIcon>
                      <Avatar sx={{ width: 28, height: 28, backgroundColor: 'success.main', fontSize: '0.75rem' }}>
                        JS
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={<Typography variant="body2" fontWeight="600">John completed Senior Dev interview</Typography>}
                      secondary={<Typography variant="caption" color="text.secondary">2 hours ago</Typography>}
                    />
                  </ListItem>
                  <ListItem sx={{ px: 0, py: 1 }}>
                    <ListItemIcon>
                      <Avatar sx={{ width: 28, height: 28, backgroundColor: 'primary.main', fontSize: '0.75rem' }}>
                        AM
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={<Typography variant="body2" fontWeight="600">Alice started Product Manager hiring</Typography>}
                      secondary={<Typography variant="caption" color="text.secondary">5 hours ago</Typography>}
                    />
                  </ListItem>
                  <ListItem sx={{ px: 0, py: 1 }}>
                    <ListItemIcon>
                      <Avatar sx={{ width: 28, height: 28, backgroundColor: 'warning.main', fontSize: '0.75rem' }}>
                        RB
                      </Avatar>
                    </ListItemIcon>
                    <ListItemText
                      primary={<Typography variant="body2" fontWeight="600">Robert approved offer letter</Typography>}
                      secondary={<Typography variant="caption" color="text.secondary">1 day ago</Typography>}
                    />
                  </ListItem>
                </List>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      </Box>
    </Box>
  )
}