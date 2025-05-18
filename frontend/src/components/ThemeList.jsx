import React from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Chip, 
  Stack,
  useTheme,
  alpha,
  Tooltip
} from '@mui/material';
import TagIcon from '@mui/icons-material/Tag';
import DescriptionIcon from '@mui/icons-material/Description';
import AutoGraphIcon from '@mui/icons-material/AutoGraph';

export default function ThemeList({ themes, documents }) {
  const muiTheme = useTheme();

  if (!themes || themes.length === 0) {
    return (
      <Box sx={{ 
        textAlign: 'center', 
        py: 8,
        px: 2
      }}>
        <TagIcon sx={{ 
          fontSize: 48, 
          color: 'text.secondary',
          opacity: 0.5,
          mb: 2
        }} />
        <Typography variant="h6" color="text.secondary" gutterBottom>
          No themes found
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Upload and analyze documents to identify themes
        </Typography>
      </Box>
    );
  }

  const getDocumentNames = (documentIds) => {
    if (!documents || !documentIds || documentIds.length === 0) {
      return 'unknown documents';
    }
    const foundDocuments = documents.filter(doc => documentIds.includes(doc.id));
    if (foundDocuments.length === 0) {
      return 'unknown documents';
    }
    return foundDocuments.map(doc => doc.name || 'Unnamed Document').join(', ');
  };

  return (
    <Stack spacing={2}>
      {themes.map((theme) => (
        <Paper
          key={theme.id || theme.name}
          elevation={0}
          sx={{
            p: 2,
            borderRadius: 2,
            border: 1,
            borderColor: 'divider',
            transition: 'all 0.2s ease-in-out',
            '&:hover': {
              borderColor: muiTheme.palette.primary.main,
              bgcolor: alpha(muiTheme.palette.primary.main, 0.02),
              transform: 'translateY(-2px)',
              boxShadow: 1
            }
          }}
        >
          <Stack spacing={2}>
      
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'flex-start',
              gap: 2
            }}>
              <Typography variant="h6" color="primary" sx={{ fontWeight: 600 }}>
                {theme.name}
              </Typography>
              <Chip
                icon={<AutoGraphIcon />}
                label={`${Math.round(theme.confidence_score * 100)}% confidence`}
                color="success"
                size="small"
                sx={{ 
                  fontWeight: 500,
                  '& .MuiChip-icon': {
                    color: 'inherit'
                  }
                }}
              />
            </Box>

            <Typography 
              variant="body2" 
              color="text.secondary"
              sx={{ 
                lineHeight: 1.6,
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}
            >
              {theme.description || 'No description available'}
            </Typography>

            <Box sx={{ 
              display: 'flex', 
              alignItems: 'center',
              gap: 1,
              color: 'text.secondary'
            }}>
              <DescriptionIcon sx={{ fontSize: 16 }} />
              <Tooltip title={getDocumentNames(theme.document_ids)}>
                <Typography variant="caption" sx={{ 
                  color: 'text.secondary',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  Found in {getDocumentNames(theme.document_ids)}
                </Typography>
              </Tooltip>
            </Box>
          </Stack>
        </Paper>
      ))}
    </Stack>
  );
}