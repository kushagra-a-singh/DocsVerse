import React from 'react';
import { Link } from 'react-router-dom';
import { Box, Card, CardContent, Typography, Grid, Button, useTheme } from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import CategoryIcon from '@mui/icons-material/Category';
import ChatIcon from '@mui/icons-material/Chat';
import { useQuery } from 'react-query';
import documentService from '../api/documentService';
import themeService from '../api/themeService';

export default function Dashboard() {
  const theme = useTheme();

  const { data: documents } = useQuery('documents', documentService.getAllDocuments);
  const totalDocuments = documents ? documents.length : 0;

  const { data: themes } = useQuery('themes', themeService.getAllThemes);
  const totalThemes = themes?.themes ? themes.themes.length : 0; 

  return (
    <Box
      sx={{
        p: 3,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-start',
        alignItems: 'center',
        minHeight: 'calc(100vh - 64px - 48px)',
        width: '100%',
        boxSizing: 'border-box',
        pt: 5,
      }}
    >
      <Typography variant="h4" fontWeight={700} mb={4} sx={{ textAlign: 'center' }}>Dashboard</Typography>

      <Grid container spacing={3} justifyContent="center">
        
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <DescriptionIcon sx={{ fontSize: 48, color: theme.palette.primary.main }} />
              <Typography variant="h6" mt={1}>Total Documents</Typography>
              <Typography variant="h3" fontWeight={700} color="primary.main">{totalDocuments}</Typography>
            </CardContent>
          </Card>
        </Grid>

        
        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <CardContent sx={{ textAlign: 'center' }}>
              <CategoryIcon sx={{ fontSize: 48, color: theme.palette.secondary.main }} />
              <Typography variant="h6" mt={1}>Identified Themes</Typography>
              <Typography variant="h3" fontWeight={700} color="secondary.main">{totalThemes}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', textAlign: 'center' }}>
            <CardContent>
                <ChatIcon sx={{ fontSize: 48, color: theme.palette.info.main }} />
                <Typography variant="h6" mt={1}>Chat Interface</Typography>
                <Button component={Link} to="/chat" variant="contained" sx={{ mt: 2 }}>
                    Start Chatting
                </Button>
            </CardContent>
          </Card>
        </Grid>

         <Grid item xs={12} md={6}>
            <Card sx={{ height: '100%' }}>
                <CardContent>
                    <Typography variant="h6" mb={2}>Quick Actions</Typography>
                    <Grid container spacing={2} direction="column">
                         <Grid item>
                            <Button component={Link} to="/documents" variant="outlined" startIcon={<DescriptionIcon />}>
                                Manage Documents
                            </Button>
                         </Grid>
                         <Grid item>
                            <Button component={Link} to="/themes" variant="outlined" startIcon={<CategoryIcon />}>
                                View Themes
                            </Button>
                         </Grid>
                    </Grid>
                </CardContent>
            </Card>
         </Grid>

      </Grid>
    </Box>
  );
}