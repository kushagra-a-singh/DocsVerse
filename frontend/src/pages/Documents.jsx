import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { 
  Box, 
  Button, 
  Card, 
  CardContent, 
  Typography, 
  Snackbar, 
  Alert, 
  CircularProgress, 
  Dialog, 
  DialogTitle, 
  DialogContent, 
  DialogActions, 
  Chip, 
  Stack, 
  Grid,
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import CloseIcon from '@mui/icons-material/Close';
import { DataGrid } from '@mui/x-data-grid';
import DocumentUpload from '../components/DocumentUpload';
import { documentService, themeService } from '../api/services';

export default function Documents() {
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState(null);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [filterStatus, setFilterStatus] = useState('');
  const [filterType, setFilterType] = useState('');
  const [filterDate, setFilterDate] = useState('');
  
  const queryClient = useQueryClient();
  const { data: documents, isLoading } = useQuery('documents', documentService.getAllDocuments);

  const deleteMutation = useMutation((id) => documentService.deleteDocument(id), {
      onSuccess: () => {
        queryClient.invalidateQueries('documents');
      setSnackbar({ open: true, message: 'Document deleted successfully.', severity: 'success' });
      setDeleteDialogOpen(false);
      setDocumentToDelete(null);
    },
    onError: (error) => {
      console.error('Delete error:', error);
      setSnackbar({
        open: true,
        message: error.response?.data?.detail || 'Failed to delete document. Please try again.',
        severity: 'error'
      });
      setDeleteDialogOpen(false);
      setDocumentToDelete(null);
    }
  });

  const handleDeleteClick = (document) => {
    setDocumentToDelete(document);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = () => {
    if (documentToDelete) {
      deleteMutation.mutate(documentToDelete.id);
    }
  };
  
  const handleUpload = async (files) => {
    try {
      const formData = new FormData();
      files.forEach((file) => formData.append('files', file));
      await documentService.uploadDocuments(formData);
      queryClient.invalidateQueries('documents');
      setSnackbar({ open: true, message: 'Documents uploaded successfully.', severity: 'success' });
      setUploadDialogOpen(false);
    } catch {
      setSnackbar({ open: true, message: 'Failed to upload documents.', severity: 'error' });
    }
  };
  
  const handleAnalyzeThemes = async () => {
    if (!documents || documents.length === 0) {
      setSnackbar({ open: true, message: 'No documents available for analysis.', severity: 'warning' });
      return;
    }
    setIsAnalyzing(true);
    try {
      const documentIds = documents.map((doc) => doc.id);
      await themeService.analyzeThemes({ document_ids: documentIds });
      queryClient.invalidateQueries('themes');
      setSnackbar({ open: true, message: 'Theme analysis started.', severity: 'success' });
    } catch {
      setSnackbar({ open: true, message: 'Failed to analyze themes.', severity: 'error' });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbar({ ...snackbar, open: false });
  };

  const filteredDocuments = (documents || []).filter(doc => {
    if (!doc) return false;
    const statusMatch = filterStatus === '' || doc.status === filterStatus;
    const typeMatch = filterType === '' || (doc.file_type?.toUpperCase() || 'UNKNOWN') === filterType.toUpperCase();
    let dateMatch = true;
    if (filterDate !== '') {
      const uploadDate = new Date(doc.upload_date);
      const now = new Date();
      now.setHours(0, 0, 0, 0);

      if (filterDate === 'today') {
        const today = new Date(now);
        dateMatch = uploadDate >= today;
      } else if (filterDate === 'last7days') {
        const sevenDaysAgo = new Date(now);
        sevenDaysAgo.setDate(now.getDate() - 7);
        dateMatch = uploadDate >= sevenDaysAgo;
      } else if (filterDate === 'last30days') {
        const thirtyDaysAgo = new Date(now);
        thirtyDaysAgo.setDate(now.getDate() - 30);
        dateMatch = uploadDate >= thirtyDaysAgo;
      }
    }
    return statusMatch && typeMatch && dateMatch;
  });

  const columns = [
    { 
      field: 'name', 
      headerName: 'Name', 
      flex: 1,
      minWidth: 250,
      renderCell: (params) => (
        <Tooltip title={params.value}>
          <Typography variant="body2" sx={{ 
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {params.value}
          </Typography>
        </Tooltip>
      )
    },
    { 
      field: 'status', 
      headerName: 'Status', 
      width: 130, 
      renderCell: (params) => (
        <Chip 
          label={params.value} 
          color={params.value === 'PROCESSED' ? 'success' : params.value === 'ERROR' ? 'error' : 'warning'} 
          size="small" 
        />
      ) 
    },
    { 
      field: 'author', 
      headerName: 'Author', 
      width: 140,
      renderCell: (params) => (
        <Typography variant="body2" color="text.secondary">
          {params.value || 'Unknown'}
        </Typography>
      )
    },
    { 
      field: 'upload_date', 
      headerName: 'Uploaded', 
      width: 160,
      renderCell: (params) => {
        const dateString = params.row?.upload_date;

        if (!dateString) {
          return <Typography variant="body2" color="text.secondary"></Typography>;
        }
        try {
          const date = new Date(dateString);
          if (isNaN(date.getTime())) {
            console.error('Invalid date received in RenderCell:', dateString);
            return <Typography variant="body2" color="error">Invalid Date</Typography>;
          }
          const options = { year: 'numeric', month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric' };
          return (
            <Typography variant="body2" color="text.secondary">
              {date.toLocaleString(undefined, options)}
            </Typography>
          );
        } catch (e) {
          console.error('Error processing date in RenderCell:', dateString, e);
          return <Typography variant="body2" color="error">Error</Typography>;
        }
      }
    },
    { 
      field: 'file_type', 
      headerName: 'Type', 
      width: 100,
      renderCell: (params) => (
        <Typography variant="body2" color="text.secondary">
          {params.value?.toUpperCase() || 'Unknown'}
        </Typography>
      )
    },
    { 
      field: 'actions', 
      headerName: 'Actions', 
      width: 100, 
      sortable: false, 
      renderCell: (params) => (
        <Tooltip title="Delete document">
          <IconButton
            color="error"
            size="small"
            onClick={() => handleDeleteClick(params.row)}
            disabled={deleteMutation.isLoading && documentToDelete?.id === params.row.id}
          >
            {deleteMutation.isLoading && documentToDelete?.id === params.row.id ? (
              <CircularProgress size={20} />
            ) : (
              <DeleteIcon />
            )}
          </IconButton>
        </Tooltip>
      ) 
    },
  ];
  
  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ maxWidth: 1200, margin: '0 auto' }}>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
          <Typography variant="h4" fontWeight={700} color="primary.main">Documents</Typography>
          <Stack direction="row" spacing={2}>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => setUploadDialogOpen(true)}>
              Upload
            </Button>
            <Button 
              variant="outlined" 
              startIcon={<AutoAwesomeIcon />} 
              onClick={handleAnalyzeThemes}
              disabled={isAnalyzing || !documents || documents.length === 0}
            >
              {isAnalyzing ? <CircularProgress size={20} /> : 'Analyze Themes'}
            </Button>
          </Stack>
        </Box>

        <Box mb={3}>
          <Stack direction="row" spacing={2}>
            <FormControl sx={{ minWidth: 120 }} size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                label="Status"
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="UPLOADED">UPLOADED</MenuItem>
                <MenuItem value="PROCESSED">PROCESSED</MenuItem>
                <MenuItem value="ERROR">ERROR</MenuItem>
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 120 }} size="small">
              <InputLabel>Type</InputLabel>
              <Select
                value={filterType}
                label="Type"
                onChange={(e) => setFilterType(e.target.value)}
              >
                <MenuItem value="">All</MenuItem>
                <MenuItem value="PDF">PDF</MenuItem>
              </Select>
            </FormControl>
            <FormControl sx={{ minWidth: 120 }} size="small">
              <InputLabel>Uploaded</InputLabel>
              <Select
                value={filterDate}
                label="Uploaded"
                onChange={(e) => setFilterDate(e.target.value)}
              >
                <MenuItem value="">All Time</MenuItem>
                <MenuItem value="today">Today</MenuItem>
                <MenuItem value="last7days">Last 7 Days</MenuItem>
                <MenuItem value="last30days">Last 30 Days</MenuItem>
              </Select>
            </FormControl>
          </Stack>
        </Box>

        <Grid container columns={12} spacing={3}>
          <Grid item xs={12}>
            <Card>
              <CardContent>
                {isLoading ? (
                  <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
                    <CircularProgress />
                  </Box>
                ) : (
                  <div style={{ width: '100%' }}>
                    <DataGrid
                      autoHeight
                      rows={filteredDocuments}
                      columns={columns}
                      pageSize={8}
                      rowsPerPageOptions={[8, 16, 32]}
                      getRowId={(row) => row.id}
                      disableSelectionOnClick
                      sx={{
                        '& .MuiDataGrid-cell': {
                          display: 'flex',
                          alignItems: 'center',
                          borderColor: 'divider'
                        },
                        '& .MuiDataGrid-columnHeaders': {
                          backgroundColor: 'background.default',
                          borderBottom: 2,
                          borderColor: 'divider'
                        }
                      }}
                    />
                  </div>
                )}
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload Documents</DialogTitle>
        <DialogContent>
          <DocumentUpload onUpload={handleUpload} isUploading={false} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
        </DialogActions>
      </Dialog>

      <Dialog 
        open={deleteDialogOpen} 
        onClose={() => {
          setDeleteDialogOpen(false);
          setDocumentToDelete(null);
        }}
      >
        <DialogTitle>Delete Document</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete "{documentToDelete?.name}"? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => {
              setDeleteDialogOpen(false);
              setDocumentToDelete(null);
            }}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleDeleteConfirm}
            color="error"
            variant="contained"
            disabled={deleteMutation.isLoading}
          >
            {deleteMutation.isLoading ? <CircularProgress size={20} /> : 'Delete'}
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbar.severity}
          sx={{
            width: '100%',
            p: 0.8,
            fontSize: '1.1rem',
            ...(snackbar.severity === 'success' && {
              backgroundColor: '#46a049',
              color: '#FFFFFF',
              '.MuiAlert-icon': {
                color: '#FFFFFF',
              },
            }),
            ...(snackbar.severity === 'error' && {
              backgroundColor: '#f43325',
              color: '#FFFFFF',
              '.MuiAlert-icon': {
                color: '#FFFFFF',
              },
            }),
          }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
}