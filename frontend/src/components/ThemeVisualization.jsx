import React from 'react';
import { useState, useEffect, useRef } from 'react';
import { Chart } from 'chart.js/auto';
import { 
  Box, 
  Typography, 
  Paper,
  useTheme,
  alpha
} from '@mui/material';
import TagIcon from '@mui/icons-material/Tag';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';

export default function ThemeVisualization({ themes }) {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);
  const [error, setError] = useState(false);
  const theme = useTheme();
  
  useEffect(() => {
    setError(false);
    
    if (!themes || themes.length === 0 || !chartRef.current) return;
    
    try {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
      
      const validThemes = themes.filter(theme => 
        theme && 
        typeof theme === 'object' && 
        theme.name && 
        typeof theme.confidence_score === 'number'
      );
      
      if (validThemes.length === 0) {
        setError(true);
        return;
      }
      
      const sortedThemes = [...validThemes].sort((a, b) => b.confidence_score - a.confidence_score);
      const topThemes = sortedThemes.slice(0, 8);
      
      const data = {
        labels: topThemes.map(theme => theme.name),
        datasets: [
          {
            label: 'Confidence Score',
            data: topThemes.map(theme => Math.round(theme.confidence_score * 100)),
            backgroundColor: alpha(theme.palette.primary.main, 0.6),
            borderColor: theme.palette.primary.main,
            borderWidth: 1,
          },
          {
            label: 'Document Count',
            data: topThemes.map(theme => theme.document_ids ? theme.document_ids.length : 0),
            backgroundColor: alpha(theme.palette.success.main, 0.6),
            borderColor: theme.palette.success.main,
            borderWidth: 1,
          },
        ],
      };
      
      const ctx = chartRef.current.getContext('2d');
      chartInstance.current = new Chart(ctx, {
        type: 'bar',
        data: data,
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          layout: {
            padding: {
              top: 10,
              right: 25,
              bottom: 10,
              left: 10
            }
          },
          scales: {
            x: {
              beginAtZero: true,
              max: 100,
              grid: {
                display: true,
                color: alpha(theme.palette.divider, 0.5)
              },
              title: {
                display: true,
                text: 'Confidence Score (%)',
                font: {
                  size: 12,
                  weight: 500
                },
                color: theme.palette.text.secondary
              },
              ticks: {
                font: {
                  size: 11
                },
                color: theme.palette.text.secondary
              }
            },
            y: {
              ticks: {
                autoSkip: false,
                font: {
                  size: 11
                },
                color: theme.palette.text.primary
              },
              grid: {
                display: false
              }
            },
          },
          plugins: {
            legend: {
              display: true,
              position: 'top',
              align: 'end',
              labels: {
                usePointStyle: true,
                pointStyle: 'circle',
                padding: 20,
                font: {
                  size: 11
                },
                color: theme.palette.text.secondary
              }
            },
            tooltip: {
              backgroundColor: theme.palette.background.paper,
              titleColor: theme.palette.text.primary,
              bodyColor: theme.palette.text.secondary,
              borderColor: theme.palette.divider,
              borderWidth: 1,
              padding: 12,
              titleFont: {
                size: 12,
                weight: 600
              },
              bodyFont: {
                size: 11
              },
              callbacks: {
                label: function(context) {
                  return `${context.dataset.label}: ${context.raw}%`;
                }
              }
            }
          },
        },
      });
    } catch (err) {
      console.error('Error creating chart:', err);
      setError(true);
    }
    
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [themes, theme]);
  
  return (
    <Box sx={{ height: '100%' }}>
      {error ? (
        <Paper
          elevation={0}
          sx={{
            p: 4,
            textAlign: 'center',
            border: 1,
            borderColor: 'divider',
            borderRadius: 2
          }}
        >
          <TagIcon sx={{ 
            fontSize: 48, 
            color: 'error.main',
            opacity: 0.5,
            mb: 2
          }} />
          <Typography variant="h6" color="error" gutterBottom>
            Error Visualizing Themes
          </Typography>
          <Typography variant="body2" color="text.secondary">
            There was a problem visualizing the theme data
          </Typography>
        </Paper>
      ) : !themes || themes.length === 0 ? (
        <Paper
          elevation={0}
          sx={{
            p: 4,
            textAlign: 'center',
            border: 1,
            borderColor: 'divider',
            borderRadius: 2
          }}
        >
          <AutoGraphIcon sx={{ 
            fontSize: 48, 
            color: 'text.secondary',
            opacity: 0.5,
            mb: 2
          }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No themes available
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Upload documents and analyze them to identify themes
          </Typography>
        </Paper>
      ) : (
        <Paper
          elevation={0}
          sx={{
            p: 3,
            border: 1,
            borderColor: 'divider',
            borderRadius: 2,
            height: 400
          }}
        >
          <canvas ref={chartRef} />
        </Paper>
      )}
    </Box>
  );
}