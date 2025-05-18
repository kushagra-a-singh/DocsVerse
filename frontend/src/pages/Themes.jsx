import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Tabs, 
  Tab, 
  CircularProgress, 
  Alert, 
  Grid,
  Paper,
  Chip,
  Stack,
  useTheme,
  alpha
} from '@mui/material';
import ListAltIcon from '@mui/icons-material/ListAlt';
import BarChartIcon from '@mui/icons-material/BarChart';
import TagIcon from '@mui/icons-material/Tag';
import DescriptionIcon from '@mui/icons-material/Description';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';
import ThemeList from '../components/ThemeList';
import ThemeVisualization from '../components/ThemeVisualization';
import documentService from '../api/documentService';

export default function Themes() {
  const [tab, setTab] = useState(0);
  const theme = useTheme();

  const { data: themes, isLoading: isLoadingThemes, error: errorThemes } = useQuery('themes', async () => {
    const response = await fetch('/api/themes/');
    if (!response.ok) {
      throw new Error('Failed to fetch themes');
    }
    return response.json();
  });

  const { data: documents, isLoading: isLoadingDocuments, error: errorDocuments } = useQuery('documents', documentService.getAllDocuments, {
    refetchInterval: 5000,
  });

  const isLoading = isLoadingThemes || isLoadingDocuments;
  const error = errorThemes || errorDocuments;

  //calculate theme statistics
  const themeStats = {
    total: themes?.themes?.length || 0,
    avgConfidence: themes?.themes?.reduce((acc, theme) => acc + theme.confidence_score, 0) / (themes?.themes?.length || 1) || 0,
    totalDocuments: documents?.length || 0
  };

  return (
    <Box sx={{ maxWidth: '1200px', mx: 'auto', px: 2 }}>
      
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} color="primary.main" gutterBottom>
          Theme Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Explore and analyze themes identified across your documents
        </Typography>

        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={4}>
            <Paper
              elevation={0}
              sx={{
                p: 2,
                bgcolor: alpha(theme.palette.primary.main, 0.1),
                borderRadius: 2,
                height: '100%'
              }}
            >
              <Stack direction="row" spacing={2} alignItems="center">
                <TagIcon sx={{ color: 'primary.main', fontSize: 28 }} />
                <Box>
                  <Typography variant="h4" fontWeight={600} color="primary.main">
                    {themeStats.total}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Themes
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Paper
              elevation={0}
              sx={{
                p: 2,
                bgcolor: alpha(theme.palette.success.main, 0.1),
                borderRadius: 2,
                height: '100%'
              }}
            >
              <Stack direction="row" spacing={2} alignItems="center">
                <AutoGraphIcon sx={{ color: 'success.main', fontSize: 28 }} />
                <Box>
                  <Typography variant="h4" fontWeight={600} color="success.main">
                    {Math.round(themeStats.avgConfidence * 100)}%
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Average Confidence
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={4}>
            <Paper
              elevation={0}
              sx={{
                p: 2,
                bgcolor: alpha(theme.palette.info.main, 0.1),
                borderRadius: 2,
                height: '100%'
              }}
            >
              <Stack direction="row" spacing={2} alignItems="center">
                <DescriptionIcon sx={{ color: 'info.main', fontSize: 28 }} />
                <Box>
                  <Typography variant="h4" fontWeight={600} color="info.main">
                    {themeStats.totalDocuments}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Documents Analyzed
                  </Typography>
                </Box>
              </Stack>
            </Paper>
          </Grid>
        </Grid>

        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'flex-end',
          borderBottom: 1,
          borderColor: 'divider'
        }}>
          <Tabs 
            value={tab} 
            onChange={(_, v) => setTab(v)} 
            textColor="primary" 
            indicatorColor="primary"
            sx={{
              '& .MuiTab-root': {
                minHeight: 48,
                textTransform: 'none',
                fontWeight: 500
              }
            }}
          >
            <Tab 
              icon={<ListAltIcon />} 
              label="List View" 
              iconPosition="start"
            />
            <Tab 
              icon={<BarChartIcon />} 
              label="Visualization" 
              iconPosition="start"
            />
          </Tabs>
        </Box>
      </Box>

      <Card 
        elevation={0}
        sx={{ 
          bgcolor: 'background.paper',
          borderRadius: 2,
          border: 1,
          borderColor: 'divider'
        }}
      >
        <CardContent sx={{ p: 3 }}>
          {isLoading ? (
            <Box display="flex" justifyContent="center" alignItems="center" minHeight={300}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Alert 
              severity="error"
              sx={{ 
                '& .MuiAlert-message': { 
                  fontSize: '0.875rem'
                }
              }}
            >
              Error loading data. Please try again later.
            </Alert>
          ) : (
            <Box>
              {tab === 0 ? (
                <ThemeList themes={themes?.themes} documents={documents} />
              ) : (
                <Box>
                  <ThemeVisualization themes={themes?.themes} documents={documents} />
                </Box>
              )}
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}