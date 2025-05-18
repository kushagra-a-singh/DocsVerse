import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const themeService = {
  analyzeThemes: async (analysisData) => {
    try {
      const response = await axios.post(`${API_URL}/api/themes/analyze`, analysisData);
      return response.data;
    } catch (error) {
      console.error('Error analyzing themes:', error);
      throw error;
    }
  },

  getAllThemes: async () => {
    try {
      const response = await axios.get(`${API_URL}/api/themes/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching themes:', error);
      throw error;
    }
  },

  getThemeById: async (id) => {
    try {
      const response = await axios.get(`${API_URL}/api/themes/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching theme ${id}:`, error);
      throw error;
    }
  },

  createTheme: async (themeData) => {
    try {
      const response = await axios.post(`${API_URL}/api/themes/`, themeData);
      return response.data;
    } catch (error) {
      console.error('Error creating theme:', error);
      throw error;
    }
  },
};

export default themeService;