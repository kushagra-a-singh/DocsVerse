import React from 'react';
import { Box, CssBaseline, AppBar, Toolbar, Typography, IconButton, useTheme } from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import Sidebar from './Sidebar';

const drawerWidth = 240;

export default function Layout({ children, darkMode, onToggleDarkMode }) {
  const theme = useTheme();

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
          zIndex: (theme) => theme.zIndex.drawer + 1, 
          bgcolor: theme.palette.background.paper, 
          color: theme.palette.text.primary, 
          boxShadow: 'none', 
          borderBottom: `1px solid ${theme.palette.divider}`, 
        }}
      >
        <Toolbar>
          <Typography
            variant="h4" 
            noWrap
            component="div"
            sx={{
              flexGrow: 1, 
              textAlign: 'center', 
              fontWeight: 700, 
              color: theme.palette.primary.main, 
              ml: { sm: `-120px` }, 
              mr: { sm: `-157px` },  
            }}
          >
            DocsVerse 
          </Typography>
           <IconButton color="inherit" onClick={onToggleDarkMode}>
               {darkMode ? '🌞' : '🌙'} 
           </IconButton>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
        aria-label="mailbox folders"
      >
        <Sidebar darkMode={darkMode} />
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: '64px',
          bgcolor: theme.palette.background.default,
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
} 