import React, { useState, useRef, useEffect } from 'react';
import { useMutation, useQueryClient } from 'react-query';
import { Box, Paper, Avatar, Typography, IconButton, CircularProgress, InputBase, useTheme, Button } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ClearIcon from '@mui/icons-material/Clear';
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline';
import { TextField } from '@mui/material';
import ReactMarkdown from 'react-markdown';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ChatInterface({ selectedDocuments, onThemeIdentified }) {
  const queryClient = useQueryClient();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const theme = useTheme();

  const messages = queryClient.getQueryData('chatMessages') || [];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessageMutation = useMutation(
    async (message) => {
      const response = await fetch(`${API_URL}/api/queries/with-themes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: message,
          document_ids: selectedDocuments.map(doc => doc.id),
        }),
      });
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to send message');
      }
      const data = await response.json();
      return data;
    },
    {
      onSuccess: (data) => {
        const assistantResponse = data.document_responses && data.document_responses.length > 0
          ? data.document_responses.map(dr => dr.extracted_answer).join('\n\n')
          : 'Could not get a response from the model.';
      
        queryClient.setQueryData('chatMessages', prev => [
          ...(prev || []),
          { 
            role: 'assistant', 
            content: assistantResponse, 
            timestamp: new Date(),
            themes: data.synthesized_response?.themes || [] 
          }
        ]);
      
        if (data.synthesized_response?.themes && data.synthesized_response.themes.length > 0 && onThemeIdentified) {
          onThemeIdentified(data.synthesized_response.themes);
        }
      },
      onError: (error) => {
        queryClient.setQueryData('chatMessages', prev => [
          ...(prev || []),
          {
            role: 'assistant',
            content: 'Sorry, I encountered an error processing your request. Please try again.',
            timestamp: new Date()
          }
        ]);
        console.error('Error sending message:', error);
      },
    }
  );

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    const userMessage = { role: 'user', content: input, timestamp: new Date() };
    
    const updatedMessages = [...(messages || []), userMessage];
    queryClient.setQueryData('chatMessages', updatedMessages);
    localStorage.setItem('chatMessages', JSON.stringify(updatedMessages));
    
    sendMessageMutation.mutate(input);
    setInput('');
  };

  const handleClearChat = () => {
    queryClient.setQueryData('chatMessages', []);
    localStorage.removeItem('chatMessages');
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100%',
      bgcolor: 'background.paper',
      borderRadius: 1,
      overflow: 'hidden'
    }}>
      <Box sx={{ 
        p: 2, 
        borderBottom: 1, 
        borderColor: 'divider',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        bgcolor: 'background.default'
      }}>
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          Chat
        </Typography>
        <Button
          variant="outlined"
          size="small"
          onClick={handleClearChat}
          startIcon={<DeleteOutlineIcon />}
          sx={{ 
            color: 'text.secondary',
            borderColor: 'divider',
            '&:hover': {
              borderColor: 'error.main',
              color: 'error.main',
              bgcolor: 'error.lighter'
            }
          }}
        >
          Clear Chat
        </Button>
      </Box>

      <Box sx={{ 
        flexGrow: 1, 
        overflow: 'auto',
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}>
        {messages.map((message, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
              mb: 2
            }}
          >
            <Box
              sx={{
                maxWidth: '80%',
                p: 2,
                borderRadius: 2,
                bgcolor: message.role === 'user' ? 'primary.main' : 'background.default',
                color: message.role === 'user' ? 'primary.contrastText' : 'text.primary',
                boxShadow: 1,
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  [message.role === 'user' ? 'right' : 'left']: -8,
                  width: 0,
                  height: 0,
                  borderTop: '8px solid transparent',
                  borderBottom: '8px solid transparent',
                  [message.role === 'user' ? 'borderLeft' : 'borderRight']: `8px solid ${message.role === 'user' ? theme.palette.primary.main : theme.palette.background.default}`
                }
              }}
            >
              <Box sx={{ 
                '& .markdown-body': {
                  color: 'inherit',
                  '& h1, & h2, & h3, & h4, & h5, & h6': {
                    color: 'inherit',
                    marginTop: 1,
                    marginBottom: 1
                  },
                  '& p': {
                    marginTop: 0.5,
                    marginBottom: 0.5
                  },
                  '& ul, & ol': {
                    marginTop: 0.5,
                    marginBottom: 0.5,
                    paddingLeft: 2
                  },
                  '& code': {
                    backgroundColor: 'rgba(0, 0, 0, 0.1)',
                    padding: '0.2em 0.4em',
                    borderRadius: 1,
                    fontSize: '0.9em'
                  },
                  '& pre': {
                    backgroundColor: 'rgba(0, 0, 0, 0.1)',
                    padding: 1,
                    borderRadius: 1,
                    overflow: 'auto',
                    '& code': {
                      backgroundColor: 'transparent',
                      padding: 0
                    }
                  },
                  '& blockquote': {
                    borderLeft: '4px solid',
                    borderColor: 'divider',
                    paddingLeft: 1,
                    marginLeft: 0,
                    marginRight: 0,
                    fontStyle: 'italic'
                  }
                }
              }}>
                <ReactMarkdown className="markdown-body">
                  {message.content}
                </ReactMarkdown>
              </Box>
            </Box>
          </Box>
        ))}
        {sendMessageMutation.isLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
      </Box>

      <Box sx={{ 
        p: 2, 
        borderTop: 1, 
        borderColor: 'divider',
        bgcolor: 'background.default'
      }}>
        <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '8px' }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder={selectedDocuments.length > 0 
              ? "Type your message..." 
              : "Select one or more documents to start chatting"}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={selectedDocuments.length === 0 || sendMessageMutation.isLoading}
            multiline
            maxRows={4}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: 'background.paper',
                '&:hover': {
                  '& > fieldset': { borderColor: 'primary.main' }
                }
              }
            }}
          />
          <Button
            type="submit"
            variant="contained"
            disabled={selectedDocuments.length === 0 || !input.trim() || sendMessageMutation.isLoading}
            sx={{ 
              minWidth: 100,
              height: 56,
              boxShadow: 2
            }}
          >
            {sendMessageMutation.isLoading ? <CircularProgress size={24} /> : 'Send'}
          </Button>
        </form>
      </Box>
    </Box>
  );
}