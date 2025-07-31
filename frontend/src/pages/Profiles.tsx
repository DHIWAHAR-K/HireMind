import React from 'react'
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  TextField,
  InputAdornment,
} from '@mui/material'
import {
  Add as AddIcon,
  Search as SearchIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  Menu as MenuIcon,
} from '@mui/icons-material'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { useDispatch } from 'react-redux'
import { profilesAPI } from '../services/api'
import { toggleSidebar } from '../store/uiSlice'
import { useSnackbar } from 'notistack'

export default function Profiles() {
  const navigate = useNavigate()
  const dispatch = useDispatch()
  const { enqueueSnackbar } = useSnackbar()
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = React.useState('')

  const { data: profilesData, isLoading } = useQuery(
    'profiles',
    () => profilesAPI.list(20),
    {
      select: (response) => response.data,
    }
  )

  const deleteMutation = useMutation(
    (sessionId: string) => profilesAPI.delete(sessionId),
    {
      onSuccess: () => {
        queryClient.invalidateQueries('profiles')
        enqueueSnackbar('Profile deleted successfully', { variant: 'success' })
      },
      onError: () => {
        enqueueSnackbar('Failed to delete profile', { variant: 'error' })
      },
    }
  )

  const handleDelete = (sessionId: string) => {
    if (window.confirm('Are you sure you want to delete this profile?')) {
      deleteMutation.mutate(sessionId)
    }
  }

  const filteredProfiles = profilesData?.profiles?.filter((profile: any) =>
    profile.role_title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    profile.department?.toLowerCase().includes(searchTerm.toLowerCase())
  ) || []

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
              Hiring Profiles
            </Typography>
            <Typography variant="body2" color="text.secondary">
              View and manage all hiring profiles
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
        p: 2,
        width: '100%',
      }}>

      {/* Search and Filters */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                placeholder="Search profiles..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <SearchIcon />
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Chip label="All" variant="filled" color="primary" />
                <Chip label="Active" variant="outlined" />
                <Chip label="Completed" variant="outlined" />
                <Chip label="Draft" variant="outlined" />
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

        {/* Profiles List */}
        <Card>
          <CardContent>
            {isLoading ? (
              <Typography>Loading profiles...</Typography>
            ) : filteredProfiles.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                  No hiring profiles found
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {searchTerm ? 'Try adjusting your search terms' : 'Start your first hiring process to see it here'}
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => navigate('/new-hiring')}
                >
                  Start New Hiring
                </Button>
              </Box>
            ) : (
              <List>
                {filteredProfiles.map((profile: any, index: number) => (
                  <React.Fragment key={profile.session_id}>
                    <ListItem
                      sx={{
                        py: 2,
                        cursor: 'pointer',
                        '&:hover': { backgroundColor: 'action.hover' },
                      }}
                      onClick={() => navigate(`/hiring/${profile.session_id}`)}
                    >
                      <Avatar
                        sx={{
                          bgcolor: 'primary.light',
                          color: 'primary.main',
                          mr: 2,
                        }}
                      >
                        {profile.role_title?.charAt(0) || 'R'}
                      </Avatar>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                            <Typography variant="subtitle1" fontWeight="medium">
                              {profile.role_title || 'Unknown Role'}
                            </Typography>
                            <Chip
                              label={profile.status}
                              size="small"
                              color={
                                profile.status === 'active'
                                  ? 'primary'
                                  : profile.status === 'completed'
                                  ? 'success'
                                  : 'default'
                              }
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Department: {profile.department || 'Not specified'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              Created: {profile.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Unknown'}
                            </Typography>
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          onClick={(e) => {
                            e.stopPropagation()
                            navigate(`/hiring/${profile.session_id}`)
                          }}
                          size="small"
                        >
                          <VisibilityIcon />
                        </IconButton>
                        <IconButton
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDelete(profile.session_id)
                          }}
                          size="small"
                          color="error"
                          disabled={deleteMutation.isLoading}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                    {index < filteredProfiles.length - 1 && <Box sx={{ borderBottom: 1, borderColor: 'divider' }} />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </CardContent>
        </Card>
      </Box>
    </Box>
  )
}