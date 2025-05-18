import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function CitationDisplay({ citations }) {
  const [expandedCitation, setExpandedCitation] = useState(null);

  if (!citations || citations.length === 0) {
    return null;
  }

  const toggleCitation = (index) => {
    if (expandedCitation === index) {
      setExpandedCitation(null);
    } else {
      setExpandedCitation(index);
    }
  };

  return (
    <div className="mt-2 text-sm">
      <ul className="space-y-2">
        {citations.map((citation, index) => (
          <li key={index} className="border border-gray-200 rounded-md overflow-hidden">
            <div
              className="flex justify-between items-center p-2 bg-gray-50 cursor-pointer"
              onClick={() => toggleCitation(index)}
            >
              <div className="flex items-center">
                <span className="font-medium text-xs">
                  {citation.document_title || citation.document_id}
                </span>
                <span className="ml-2 text-xs text-gray-500">
                  {citation.relevance_score ? `Relevance: ${Math.round(citation.relevance_score * 100)}%` : ''}
                </span>
              </div>
              <svg
                className={`h-4 w-4 text-gray-500 transition-transform ${expandedCitation === index ? 'transform rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
            {expandedCitation === index && (
              <div className="p-2 bg-white">
                <p className="text-xs text-gray-700 whitespace-pre-line">{citation.text}</p>
                <div className="mt-2 flex justify-end">
                  <Link
                    to={`/documents/${citation.document_id}`}
                    className="text-xs text-primary-600 hover:text-primary-800"
                  >
                    View Document
                  </Link>
                </div>
              </div>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}