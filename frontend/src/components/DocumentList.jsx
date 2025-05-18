import { useState } from 'react';
import { Link } from 'react-router-dom';
import { DocumentTextIcon, TrashIcon } from '@heroicons/react/24/outline';

export default function DocumentList({ documents, onDelete, isLoading }) {
  const [selectedDocuments, setSelectedDocuments] = useState([]);

  const toggleSelect = (id) => {
    if (selectedDocuments.includes(id)) {
      setSelectedDocuments(selectedDocuments.filter(docId => docId !== id));
    } else {
      setSelectedDocuments([...selectedDocuments, id]);
    }
  };

  const handleDeleteSelected = () => {
    if (window.confirm(`Delete ${selectedDocuments.length} selected documents?`)) {
      selectedDocuments.forEach(id => onDelete(id));
      setSelectedDocuments([]);
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-48">
        <div className="animate-spin rounded-full h-6 w-6 border-t-2 border-b-2 border-sky-500"></div>
      </div>
    );
  }

  if (!documents || documents.length === 0) {
    return (
      <div className="text-center py-8">
        <DocumentTextIcon className="mx-auto h-8 w-8 text-gray-400" />
        <h3 className="mt-1.5 text-xs font-medium text-gray-900">No documents</h3>
        <p className="mt-1 text-xs text-gray-500">Get started by uploading a document.</p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden bg-white shadow-sm sm:rounded-md">
      {selectedDocuments.length > 0 && (
        <div className="bg-gray-50 px-3 py-2 text-right sm:px-4">
          <button
            type="button"
            onClick={handleDeleteSelected}
            className="inline-flex items-center rounded-md border border-transparent bg-red-600 px-2.5 py-1.5 text-xs font-medium leading-4 text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          >
            <TrashIcon className="-ml-0.5 mr-1.5 h-3.5 w-3.5" aria-hidden="true" />
            Delete Selected ({selectedDocuments.length})
          </button>
        </div>
      )}
      <ul className="divide-y divide-gray-200">
        {documents.map((document) => {
          const isSelected = selectedDocuments.includes(document.id);
          return (
            <li key={document.id}>
              <div className="flex items-center px-3 py-3 sm:px-4">
                <div className="flex min-w-0 flex-1 items-center">
                  <div className="flex-shrink-0">
                    <input
                      type="checkbox"
                      className="h-3 w-3 rounded border-gray-300 text-sky-600 focus:ring-sky-500"
                      checked={isSelected}
                      onChange={() => toggleSelect(document.id)}
                    />
                  </div>
                  <div className="min-w-0 flex-1 px-3">
                    <Link to={`/documents/${document.id}`} className="block">
                      <p className="truncate text-xs font-medium text-sky-600">{document.title || document.filename}</p>
                      <p className="mt-0.5 truncate text-xs text-gray-500">
                        {document.file_type} • {document.file_size} • Uploaded on {new Date(document.created_at).toLocaleDateString()}
                      </p>
                    </Link>
                  </div>
                </div>
                <div>
                  <button
                    onClick={() => onDelete(document.id)}
                    className="inline-flex items-center rounded-md border border-gray-300 bg-white px-2 py-1 text-xs font-medium leading-4 text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2"
                  >
                    <TrashIcon className="h-3.5 w-3.5 text-gray-500" />
                  </button>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}