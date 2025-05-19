import { useState } from 'react';
import CitationDisplay from './CitationDisplay';

export default function ChatMessage({ message }) {
  const [showCitations, setShowCitations] = useState(false);

  const hasCitations = message.citations && message.citations.length > 0;
  const hasThemes = message.themes && message.themes.length > 0;
  const isImageResponse = message.document_type === 'image';

  return (
    <div
      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
    >
      <div
        className={`max-w-3xl rounded-lg px-4 py-2 ${
          message.role === 'user'
            ? 'bg-primary-100 text-primary-900'
            : message.isError
            ? 'bg-red-100 text-red-900'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        <div className="prose">
          {isImageResponse ? (
            <div className="space-y-2">
              <div className="font-medium text-sm text-gray-600">
                Image Analysis:
              </div>
              <div className="whitespace-pre-line">{message.content}</div>
            </div>
          ) : (
            <div className="whitespace-pre-line">{message.content}</div>
          )}

          {hasCitations && (
            <div className="mt-2">
              <button
                onClick={() => setShowCitations(!showCitations)}
                className="text-xs text-primary-600 hover:text-primary-800 underline"
              >
                {showCitations ? 'Hide Citations' : `Show Citations (${message.citations.length})`}
              </button>
              {showCitations && <CitationDisplay citations={message.citations} />}
            </div>
          )}

          {hasThemes && (
            <div className="mt-2">
              <p className="text-xs font-medium text-gray-500">Identified Themes:</p>
              <div className="mt-1 flex flex-wrap gap-1">
                {message.themes.map((theme, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary-100 text-primary-800"
                  >
                    {theme.name}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}