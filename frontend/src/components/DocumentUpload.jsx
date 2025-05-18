import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { DocumentArrowUpIcon, XMarkIcon } from '@heroicons/react/24/outline';

export default function DocumentUpload({ onUpload, isUploading = false }) {
  const [files, setFiles] = useState([]);
  const [error, setError] = useState('');

  const onDrop = useCallback((acceptedFiles) => {
    setError('');
    const validFiles = acceptedFiles.filter(file => {
      const isValid = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'].includes(file.type);
      if (!isValid) {
        setError('Only PDF, PNG, JPG and JPEG files are supported');
      }
      return isValid;
    });

    if (validFiles.length > 0) {
      setFiles(prev => [...prev, ...validFiles]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg']
    },
    maxSize: 10485760,
  });

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setError('Please select at least one file to upload');
      return;
    }

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      await onUpload(formData);
      setFiles([]);
    } catch (err) {
      setError('Failed to upload files. Please try again.');
      console.error('Upload error:', err);
    }
  };

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-4 text-center cursor-pointer transition-colors ${
          isDragActive ? 'border-sky-500 bg-sky-50' : 'border-gray-300 hover:border-sky-400'
        }`}
      >
        <input {...getInputProps()} />
        <DocumentArrowUpIcon className="mx-auto h-8 w-8 text-gray-400" />
        <p className="mt-1.5 text-xs font-medium text-gray-900">
          {isDragActive ? 'Drop the files here' : 'Drag and drop files here, or click to select files'}
        </p>
        <p className="mt-1 text-xs text-gray-500">
          PDF, PNG, JPG or JPEG (max. 10MB)
        </p>
      </div>

      {error && (
        <div className="mt-2 text-sm text-red-600">
          {error}
        </div>
      )}

      {files.length > 0 && (
        <div className="mt-3">
          <h4 className="text-xs font-medium text-gray-700">Selected files ({files.length}):</h4>
          <ul className="mt-1.5 divide-y divide-gray-200 border border-gray-200 rounded-md">
            {files.map((file, index) => (
              <li key={index} className="flex items-center justify-between py-1.5 px-3 text-xs">
                <div className="flex items-center">
                  <DocumentArrowUpIcon className="h-4 w-4 text-gray-400 mr-1.5" />
                  <span className="truncate max-w-xs">{file.name}</span>
                  <span className="ml-1.5 text-xs text-gray-500">
                    {(file.size / 1024).toFixed(0)} KB
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => removeFile(index)}
                  className="text-gray-400 hover:text-gray-500"
                >
                  <XMarkIcon className="h-4 w-4" />
                </button>
              </li>
            ))}
          </ul>

          <div className="mt-3 flex justify-end">
            <button
              type="button"
              onClick={handleUpload}
              disabled={isUploading}
              className={`inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-sky-600 hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 ${
                isUploading ? 'opacity-75 cursor-not-allowed' : ''
              }`}
            >
              {isUploading ? 'Uploading...' : 'Upload Documents'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}