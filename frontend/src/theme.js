import { createTheme } from '@mui/material/styles';

export const getTheme = (mode) => createTheme({
    palette: {
        mode,
        ...(mode === 'light'
            ? {
                primary: {
                    main: '#1976d2',
                    light: '#42a5f5',
                    dark: '#1565c0',
                    contrastText: '#fff',
                },
                secondary: {
                    main: '#dc004e', 
                    light: '#ff5a8d',
                    dark: '#c51162',
                    contrastText: '#fff',
                },
                background: {
                    default: '#f4f6f8',
                    paper: '#ffffff', 
                },
                text: {
                    primary: '#212121',
                    secondary: '#5f6368',
                },
                divider: '#e0e0e0',
                grey: {
                    300: '#e0e0ee',
                    700: '#616161',
                    800: '#424242'
                }
            }
            : {
                primary: {
                    main: '#90caf9',
                    light: '#e3f2fd',
                    dark: '#42a5f5',
                    contrastText: '#000',
                },
                secondary: {
                    main: '#f48fb1',
                    light: '#ffc1e3',
                    dark: '#c51162',
                    contrastText: '#000',
                },
                background: {
                    default: '#121212',
                    paper: '#1e1e1e',
                },
                text: {
                    primary: '#e0eeef',
                    secondary: '#bdc1c6',
                },
                divider: '#3c4043',
                grey: {
                    300: '#e0e0ee',
                    700: '#616161',
                    800: '#424242'
                }
            }),
    },
    typography: {
        fontFamily: ['Roboto', '"Helvetica Neue"', 'Arial', 'sans-serif'].join(','),
        h4: {
            fontWeight: 700,
            fontSize: '1.8rem',
        },
        h6: {
            fontWeight: 600,
            fontSize: '1.2rem',
        },
        body2: {
            fontSize: '0.875rem',
        }
    },
    spacing: 8,
    shape: {
        borderRadius: 8,
    },
    components: {
        MuiCard: {
            styleOverrides: {
                root: {
                    boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                    borderRadius: 8,
                },
            },
        },
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    borderRadius: 8,
                },
            },
        },
        MuiTabs: {
            styleOverrides: {
                indicator: {
                    height: 3,
                },
            },
        },
        MuiTab: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    fontWeight: 600,
                },
            },
        }
    }
});

const theme = getTheme('light');
export default theme;