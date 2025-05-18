import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { TagIcon, DocumentTextIcon, ArrowLeftIcon } from '@heroicons/react/24/outline';
import themeService from '../api/themeService';
import documentService from '../api/documentService';

export default function ThemeDetail() {
  const { id } = useParams();
  const [theme, setTheme] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchThemeAndDocuments = async () => {
      try {
        setIsLoading(true);
        const themeData = await themeService.getThemeById(id);
        setTheme(themeData);

        if (themeData.document_ids && themeData.document_ids.length > 0) {
          const documentPromises = themeData.document_ids.map(docId => 
            documentService.getDocumentById(docId)
          );
          const documentsData = await Promise.all(documentPromises);
          setDocuments(documentsData);
        }
      } catch (err) {
        console.error('Error fetching theme details:', err);
        setError('Failed to load theme details. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    if (id) {
      fetchThemeAndDocuments();
    }
  }, [id]);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 p-4 rounded-md">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Error</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!theme) {
    return (
      <div className="text-center py-12">
        <TagIcon className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Theme not found</h3>
        <p className="mt-1 text-sm text-gray-500">The theme you're looking for doesn't exist or has been removed.</p>
        <div className="mt-6">
          <Link to="/themes" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            <ArrowLeftIcon className="-ml-1 mr-2 h-5 w-5" aria-hidden="true" />
            Back to Themes
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-lg">
      <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
        <div>
          <h3 className="text-lg leading-6 font-medium text-gray-900 flex items-center">
            <TagIcon className="h-5 w-5 text-primary-500 mr-2" />
            {theme.name}
          </h3>
          <p className="mt-1 max-w-2xl text-sm text-gray-500">{theme.description}</p>
        </div>
        <Link to="/themes" className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
          <ArrowLeftIcon className="-ml-1 mr-1 h-4 w-4" aria-hidden="true" />
          Back
        </Link>
      </div>
      <div className="border-t border-gray-200 px-4 py-5 sm:p-0">
        <dl className="sm:divide-y sm:divide-gray-200">
          <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Confidence Score</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              <div className="flex items-center">
                <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                  {Math.round(theme.confidence_score * 100)}%
                </span>
              </div>
            </dd>
          </div>
          <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Created At</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {new Date(theme.created_at).toLocaleString()}
            </dd>
          </div>
          <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Keywords</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              <div className="flex flex-wrap gap-2">
                {theme.keywords && theme.keywords.map((keyword, index) => (
                  <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                    {keyword}
                  </span>
                ))}
                {(!theme.keywords || theme.keywords.length === 0) && (
                  <span className="text-gray-500">No keywords available</span>
                )}
              </div>
            </dd>
          </div>
          <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
            <dt className="text-sm font-medium text-gray-500">Supporting Documents</dt>
            <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
              {documents.length > 0 ? (
                <ul className="border border-gray-200 rounded-md divide-y divide-gray-200">
                  {documents.map((doc) => (
                    <li key={doc.id} className="pl-3 pr-4 py-3 flex items-center justify-between text-sm">
                      <div className="w-0 flex-1 flex items-center">
                        <DocumentTextIcon className="flex-shrink-0 h-5 w-5 text-gray-400" aria-hidden="true" />
                        <span className="ml-2 flex-1 w-0 truncate">{doc.title || doc.filename}</span>
                      </div>
                      <div className="ml-4 flex-shrink-0">
                        <Link to={`/documents/${doc.id}`} className="font-medium text-primary-600 hover:text-primary-500">
                          View
                        </Link>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-500">No supporting documents available</p>
              )}
            </dd>
          </div>
        </dl>
      </div>
    </div>
  );
}