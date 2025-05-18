import React, { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from 'react-query';
import { Box, Card, CardContent, Typography, Button, CircularProgress, Snackbar, Alert, Checkbox, List, ListItem, ListItemText, Grid, Chip, Stack, TextField, Avatar, styled } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import TagIcon from '@mui/icons-material/Tag';
import ChatInterface from '../components/ChatInterface';
import documentService from '../api/documentService';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ClearIcon from '@mui/icons-material/Clear';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';

//chat container to manage layout
const ChatContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: 'calc(100vh - 180px)',
  [theme.breakpoints.up('md')]: {
    flexDirection: 'row', 
  },
}));

const ChatArea = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  display: 'flex',
  flexDirection: 'column',
  minWidth: 0,
  [theme.breakpoints.up('md')]: {
    marginRight: theme.spacing(3),
  },
}));

const DocumentsSidebar = styled(Box)(({ theme }) => ({
  width: '100%',
  [theme.breakpoints.up('md')]: {
    width: 300, 
    flexShrink: 0,
  },
}));

export default function Chat() {
  const [selectedDocuments, setSelectedDocuments] = useState([]);
  //const [identifiedThemes, setIdentifiedThemes] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  //const [selectedTheme, setSelectedTheme] = useState(null);
  //const [showThemes, setShowThemes] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [selectAllChecked, setSelectAllChecked] = useState(false);

  const queryClient = useQueryClient();
  const { data: documents, isLoading, error, refetch } = useQuery('documents', documentService.getAllDocuments, {
    refetchInterval: 5000,
    onError: (err) => {
      setUploadError(err.message || 'Failed to fetch documents');
    }
  });

  //initialize chat messages from localStorage
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatMessages');
    if (savedMessages) {
      queryClient.setQueryData('chatMessages', JSON.parse(savedMessages));
    }
  }, [queryClient]);

  //save chat messages to localStorage when they change
  useEffect(() => {
    const messages = queryClient.getQueryData('chatMessages');
    if (messages) {
      localStorage.setItem('chatMessages', JSON.stringify(messages));
    }
  }, [queryClient.getQueryData('chatMessages')]);

  useEffect(() => {
    if (documents && documents.length > 0) {
      setSelectAllChecked(selectedDocuments.length === documents.length);
    } else {
      setSelectAllChecked(false);
    }
  }, [documents, selectedDocuments]);

  const theme = useTheme();

  const handleMultipleFileUpload = async (formData) => {
    setUploading(true);
    setUploadError('');
    try {
      await documentService.uploadDocuments(formData);
      setUploadError('');
      setSnackbar({ open: true, message: 'Documents uploaded successfully!', severity: 'success' });
      await refetch();
    } catch (err) {
      setUploadError(err.message || 'Failed to upload documents');
      setSnackbar({ open: true, message: 'Error uploading documents', severity: 'error' });
    } finally {
      setUploading(false);
    }
  };

  const handleDocumentSelect = (document) => {
    setSelectedDocuments(prev => {
      const isSelected = prev.some(doc => doc.id === document.id);
      let newSelectedDocuments;
      if (isSelected) {
        newSelectedDocuments = prev.filter(doc => doc.id !== document.id);
      } else {
        newSelectedDocuments = [...prev, document];
      }
      if (documents && documents.length > 0) {
         setSelectAllChecked(newSelectedDocuments.length === documents.length);
      }
      return newSelectedDocuments;
    });
  };

  // const handleThemeIdentified = (themes) => {
  //   setIdentifiedThemes(themes);
  // };

  // const handleThemeSelect = (theme) => {
  //   setSelectedTheme(theme);
  //   setShowThemes(false);
  // };

  // const handleThemeToggle = () => {
  //   setShowThemes(!showThemes);
  // };

  const handleFileUpload = async (event) => {
    const files = Array.from(event.target.files);
    if (files.length === 0) return;
    
    setUploading(true);
    setUploadError('');
    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      await documentService.uploadDocuments(formData);
      setUploadError('');
      setSnackbar({ open: true, message: 'Documents uploaded successfully!', severity: 'success' });
      await refetch();
    } catch (err) {
      setUploadError(err.message || 'Failed to upload documents');
      setSnackbar({ open: true, message: 'Error uploading documents', severity: 'error' });
    } finally {
      setUploading(false);
      event.target.value = '';
    }
  };

  const handleSelectAll = () => {
    if (selectAllChecked) {
      setSelectedDocuments([]);
    } else {
      setSelectedDocuments(documents || []);
    }
    setSelectAllChecked(!selectAllChecked);
  };

  return (
    <Box sx={{ p: 3 }}> 
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Stack direction="row" spacing={2} alignItems="center">
          {/*
          <Button
            variant="contained"
            startIcon={<TagIcon />}
            onClick={handleThemeToggle}
            sx={{ minWidth: 160 }}
          >
            {selectedTheme ? selectedTheme.name : 'Select Theme'}
          </Button>
          {showThemes && (
            <Card sx={{ position: 'absolute', zIndex: 10, mt: 6, minWidth: 200 }}>
              <List>
                {identifiedThemes.map((theme) => (
                  <ListItem button key={theme.id} onClick={() => handleThemeSelect(theme)}>
                    <ListItemText primary={theme.name} />
                  </ListItem>
                ))}
              </List>
            </Card>
          )}
          */}
          <Button
            variant="contained"
            startIcon={<UploadFileIcon />}
            component="label"
            disabled={uploading}
          >
            {uploading ? 'Uploading...' : 'Upload Document'}
            <input
              type="file"
              hidden
              multiple
              accept=".pdf,.png,.jpg,.jpeg"
              onChange={handleFileUpload}
            />
          </Button>
        </Stack>
      </Box>
      {uploadError && (
        <Alert severity="error" sx={{ mb: 2 }}>{uploadError}</Alert>
      )}

      <ChatContainer>
        <ChatArea component={Card} sx={{ display: 'flex', flexDirection: 'column' }}>
           
            <ChatInterface
                  selectedDocuments={selectedDocuments}
                  // onThemeIdentified={handleThemeIdentified}
                  
                />
        </ChatArea>

        <DocumentsSidebar>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
                 <Typography variant="h6">
                    My Documents ({documents ? documents.length : 0})
                 </Typography>
                 {documents && documents.length > 0 && (
                    <Stack direction="row" alignItems="center" spacing={0.5}>
                        <Checkbox
                            edge="start"
                            checked={selectAllChecked}
                            onChange={handleSelectAll}
                            inputProps={{ 'aria-label': 'select all documents' }}
                            size="small"
                         />
                         <Typography variant="body2" color="text.secondary">Select All</Typography>
                    </Stack>
                 )}
              </Box>
              {isLoading ? (
                <Box display="flex" justifyContent="center" alignItems="center" minHeight={80}>
                  <CircularProgress />
                </Box>
              ) : error ? (
                <Alert severity="error">Error loading documents: {error.message}</Alert>
              ) : documents && Array.isArray(documents) && documents.length > 0 ? (
                <List dense> 
                  {documents.map((document, index) => {
                    const docId = document.id;
                    const title = document.name || `Document ${index + 1}`;
                    const filename = document.name || document.file_path?.split('/').pop() || 'Unknown file';
                    const pageCount = document.page_count || document.total_pages || 0;
                    const uploadDate = document.upload_date || document.created_at || document.timestamp || new Date().toISOString();
                    const status = document.status || 'processing';
                    return (
                      <ListItem
                        key={docId}
                        button
                        selected={selectedDocuments.some(doc => doc.id === docId)}
                        onClick={() => handleDocumentSelect({ ...document, id: docId })} 
                        sx={{ borderRadius: 1, mb: 0.5 }} 
                      >
                        
                        <ListItemText
                          primary={title}
                          primaryTypographyProps={{ variant: 'body2', fontWeight: selectedDocuments.some(doc => doc.id === docId) ? 'bold' : 'normal' }} 
                          secondary={
                            <span style={{ display: 'inline-flex', alignItems: 'center' }}>
                              <span style={{ marginRight: 8, color: theme.palette.text.secondary }}>
                                {filename} • {pageCount > 0 ? `${pageCount} pages` : 'Not available'} • {new Date(uploadDate).toLocaleDateString()}
                              </span>
                              <span style={{ marginLeft: 8 }}>
                                <Chip
                                  label={status.charAt(0).toUpperCase() + status.slice(1)}
                                  size="small"
                                  color={status === 'processed' ? 'success' : status === 'error' ? 'error' : 'warning'}
                                />
                              </span>
                            </span>
                          }
                        />
                         <Checkbox
                            edge="end"
                            checked={selectedDocuments.some(doc => doc.id === docId)}
                            disableRipple
                            onClick={(event) => { 
                                event.stopPropagation(); 
                                handleDocumentSelect({ ...document, id: docId });
                            }}
                         />
                      </ListItem>
                    );
                  })}
                </List>
              ) : (
                <Typography color="text.secondary" variant="body2">No documents uploaded yet</Typography>
              )}
            </CardContent>
          </Card>
          <Card>
            <CardContent>
              <Typography variant="h6">
                Selected Documents ({selectedDocuments.length})
              </Typography>
              {isLoading ? (
                <Box display="flex" justifyContent="center" alignItems="center" minHeight={60}>
                  <CircularProgress />
                </Box>
              ) : error ? (
                <Alert severity="error">Error loading documents: {error.message}</Alert>
              ) : (
                <List dense>
                  {selectedDocuments.length === 0 ? (
                    <Typography color="text.secondary" variant="body2">Select documents to query</Typography>
                  ) : (
                    selectedDocuments.map((document) => (
                      <ListItem key={document.id} sx={{ mb: 0.5 }}>
                        <ListItemText primary={document.name} primaryTypographyProps={{ variant: 'body2' }} />
                      </ListItem>
                    ))
                  )}
                </List>
              )}
            </CardContent>
          </Card>
          
          {/*
          {identifiedThemes.length > 0 && (
            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" mb={2}>Identified Themes</Typography>
                <Grid container columns={12} spacing={1}>
                  {identifiedThemes.map((theme) => (
                    <Grid span={{ xs: 12, sm: 6 }} key={theme.id}>
                      <Card variant="outlined" sx={{ p: 1 }}>
                        <Typography variant="subtitle2" fontWeight={600}>{theme.name}</Typography>
                        <Chip
                          label={`${Math.round(theme.confidence_score * 100)}%`}
                          size="small"
                          color="success"
                          sx={{ ml: 1 }}
                        />
                        <Typography variant="caption" color="text.secondary">
                          {theme.description || 'No description'}
                        </Typography>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          )}
          */}
        </DocumentsSidebar>
      </ChatContainer>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setSnackbar({ ...snackbar, open: false })} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}
