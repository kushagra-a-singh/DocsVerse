import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const documentService = {
  getAllDocuments: async () => {
    try {
      const response = await axios.get(`${API_URL}/api/documents/`);
      const documents = response.data.documents || [];
      const validDocuments = documents.filter(doc =>
        doc.id && doc.name && doc.upload_date
      );

      return validDocuments;
    } catch (error) {
      console.error('Error fetching documents:', error);
      throw error;
    }
  },

  getDocumentById: async (id) => {
    try {
      const response = await axios.get(`${API_URL}/api/documents/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching document ${id}:`, error);
      throw error;
    }
  },

  uploadDocuments: async (formData) => {
    try {
      const response = await axios.post(`${API_URL}/api/documents/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('Error uploading documents:', error);
      throw error;
    }
  },

  deleteDocument: async (id) => {
    try {
      const response = await axios.delete(`${API_URL}/api/documents/${id}`);
      return response.data;
    } catch (error) {
      console.error(`Error deleting document ${id}:`, error);
      throw error;
    }
  },
};

export default documentService;