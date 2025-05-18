import { useState } from 'react';
import { ArrowLeftIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { Link } from 'react-router-dom';

export default function DocumentDetail({ document, isLoading }) {
  const [activeTab, setActiveTab] = useState('details');

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (!document) {
    return (
      <div className="text-center py-12">
        <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Document not found</h3>
        <p className="mt-1 text-sm text-gray-500">The document you're looking for doesn't exist or has been removed.</p>
        <div className="mt-6">
          <Link
            to="/documents"
            className="inline-flex items-center rounded-md border border-transparent bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          >
            <ArrowLeftIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
            Back to Documents
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
        <div>
          <h3 className="text-lg leading-6 font-medium text-gray-900">{document.title || document.filename}</h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">
            Uploaded on {new Date(document.created_at).toLocaleDateString()}
          </p>
        </div>
        <Link
          to="/documents"
          className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
        >
          <ArrowLeftIcon className="-ml-0.5 mr-2 h-4 w-4" aria-hidden="true" />
          Back
        </Link>
      </div>

      <div className="border-t border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
            <button
              onClick={() => setActiveTab('details')}
              className={`${activeTab === 'details' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Details
            </button>
            <button
              onClick={() => setActiveTab('content')}
              className={`${activeTab === 'content' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Content
            </button>
            <button
              onClick={() => setActiveTab('themes')}
              className={`${activeTab === 'themes' ? 'border-primary-500 text-primary-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'} whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
            >
              Related Themes
            </button>
          </nav>
        </div>

        <div className="px-4 py-5 sm:p-6">
          {activeTab === 'details' && (
            <dl className="grid grid-cols-1 gap-x-4 gap-y-8 sm:grid-cols-2">
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">File Name</dt>
                <dd className="mt-1 text-sm text-gray-900">{document.filename}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">File Type</dt>
                <dd className="mt-1 text-sm text-gray-900">{document.file_type}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">File Size</dt>
                <dd className="mt-1 text-sm text-gray-900">{document.file_size}</dd>
              </div>
              <div className="sm:col-span-1">
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                    {document.status || 'Processed'}
                  </span>
                </dd>
              </div>
              {document.metadata && (
                <div className="sm:col-span-2">
                  <dt className="text-sm font-medium text-gray-500">Metadata</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    <pre className="bg-gray-50 p-4 rounded overflow-auto max-h-40">
                      {JSON.stringify(document.metadata, null, 2)}
                    </pre>
                  </dd>
                </div>
              )}
            </dl>
          )}

          {activeTab === 'content' && (
            <div className="prose max-w-none">
              <div className="bg-gray-50 p-4 rounded overflow-auto max-h-96">
                {document.content ? (
                  <p className="whitespace-pre-line">{document.content}</p>
                ) : (
                  <p className="text-gray-500 italic">Content preview not available</p>
                )}
              </div>
            </div>
          )}

          {activeTab === 'themes' && (
            <div>
              {document.themes && document.themes.length > 0 ? (
                <ul className="divide-y divide-gray-200">
                  {document.themes.map((theme) => (
                    <li key={theme.id} className="py-4">
                      <Link to={`/themes/${theme.id}`} className="block hover:bg-gray-50">
                        <div className="px-4 py-4 sm:px-6">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-primary-600 truncate">{theme.name}</p>
                            <div className="ml-2 flex-shrink-0 flex">
                              <p className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                {theme.confidence_score ? `${Math.round(theme.confidence_score * 100)}% confidence` : 'Related'}
                              </p>
                            </div>
                          </div>
                          <div className="mt-2 sm:flex sm:justify-between">
                            <div className="sm:flex">
                              <p className="flex items-center text-sm text-gray-500">
                                {theme.description}
                              </p>
                            </div>
                          </div>
                        </div>
                      </Link>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500 italic">No themes associated with this document</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}