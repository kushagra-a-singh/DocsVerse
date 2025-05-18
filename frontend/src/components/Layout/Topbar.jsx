import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import InputBase from '@mui/material/InputBase';
import IconButton from '@mui/material/IconButton';
import SearchIcon from '@mui/icons-material/Search';
import Avatar from '@mui/material/Avatar';
import Switch from '@mui/material/Switch';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';

export default function Topbar({ darkMode, onToggleDarkMode }) {
  return (
    <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', backgroundColor: 'primary.main' }}>
      <Typography variant="h6" noWrap component="div" sx={{ fontWeight: 700, letterSpacing: 1 }}>
        DocThemes
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Box sx={{ background: 'rgba(255,255,255,0.15)', borderRadius: 2, px: 2, display: 'flex', alignItems: 'center' }}>
          <SearchIcon sx={{ color: 'white', mr: 1 }} />
          <InputBase placeholder="Search…" sx={{ color: 'white', width: 180 }} inputProps={{ 'aria-label': 'search' }} />
        </Box>
        <IconButton color="inherit" onClick={onToggleDarkMode} sx={{ ml: 1 }}>
          {darkMode ? <Brightness7Icon /> : <Brightness4Icon />}
        </IconButton>
        <Switch checked={darkMode} onChange={onToggleDarkMode} color="default" />
        <IconButton color="inherit">
          <Avatar sx={{ bgcolor: 'secondary.main' }}>U</Avatar>
        </IconButton>
      </Box>
    </Toolbar>
  );
} 