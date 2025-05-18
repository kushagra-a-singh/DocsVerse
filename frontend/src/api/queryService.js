import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const queryService = {
  processQuery: async (queryData) => {
    try {
      const response = await axios.post(`${API_URL}/api/queries/`, queryData);
      return response.data;
    } catch (error) {
      console.error('Error processing query:', error);
      throw error;
    }
  },

  processQueryWithThemes: async (queryData) => {
    try {
      const response = await axios.post(`${API_URL}/api/queries/with-themes`, queryData);
      return response.data;
    } catch (error) {
      console.error('Error processing query with themes:', error);
      throw error;
    }
  },
};

export default queryService;