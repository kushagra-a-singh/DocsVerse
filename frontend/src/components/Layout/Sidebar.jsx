import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Box, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Typography, Divider, useTheme } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import DescriptionIcon from '@mui/icons-material/Description';
import ChatIcon from '@mui/icons-material/Chat';
import CategoryIcon from '@mui/icons-material/Category';

const navItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Documents', icon: <DescriptionIcon />, path: '/documents' },
  { text: 'Themes', icon: <CategoryIcon />, path: '/themes' },
  { text: 'Chat', icon: <ChatIcon />, path: '/chat' },
];

export default function Sidebar() {
  const location = useLocation();
  const theme = useTheme();

  return (
    <Box
      sx={{
        width: 240,
        flexShrink: 0,
        bgcolor: theme.palette.background.paper,
        borderRight: `1px solid ${theme.palette.divider}`,
        height: '100vh',
        position: 'fixed',
        zIndex: theme.zIndex.drawer,
        pt: '64px',
      }}
    >
      <Box sx={{ px: 2, py: 1 }}>
        {/* <Typography variant="h6" fontWeight={700} color="primary.main">App Name</Typography> */}
      </Box>
      <Divider />
      <List sx={{ pt: 1 }}>
        {navItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              component={Link}
              to={item.path}
              selected={location.pathname === item.path}
              sx={{
                borderRadius: 2,
                mx: 1,
                my: 0.5,
                '&.Mui-selected': {
                  bgcolor: theme.palette.primary.light + '15',
                  color: theme.palette.primary.main,
                  fontWeight: 600,
                  borderLeft: `3px solid ${theme.palette.primary.main}`,
                  pl: '13px',
                },
                '&:hover': {
                    bgcolor: theme.palette.action.hover,
                }
              }}
            >
              <ListItemIcon sx={{ color: 'inherit' }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} primaryTypographyProps={{ fontWeight: 'inherit' }} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );
} 