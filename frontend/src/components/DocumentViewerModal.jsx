import React, { useState, useEffect } from 'react';
import { X, FileText, ExternalLink, Search, Copy, Check } from 'lucide-react';
import { fetchKBDoc } from '../api/client';

export default function DocumentViewerModal({ docRef, onClose }) {
  const [docContent, setDocContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copied, setCopied] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Extract file name and section anchor if present (e.g. "10_ROLE_TOOLS_ACCESS_MATRIX.md#Day 1 Provisioning Baseline")
  const parts = (docRef || '').split('#');
  let fileName = parts[0];
  const sectionTitle = parts[1] || '';

  // Clean path if it contains prefixes like backend/data/learning_plans/
  if (fileName.includes('/')) {
    fileName = fileName.split('/').pop();
  }

  useEffect(() => {
    async function load() {
      if (!fileName) return;
      try {
        setLoading(true);
        const data = await fetchKBDoc(fileName);
        setDocContent(data);
      } catch (err) {
        console.error(err);
        setError('Could not load source document: ' + fileName);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [fileName]);

  const handleCopy = () => {
    if (docContent?.content) {
      navigator.clipboard.writeText(docContent.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (!docRef) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white w-full max-w-4xl max-h-[88vh] rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden">
        
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-brand-100 text-brand-700 rounded-lg">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-base text-slate-900">{fileName}</h3>
                {sectionTitle && (
                  <span className="text-xs px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 border border-brand-200 font-medium">
                    #{sectionTitle}
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-500">Knowledge Base Source Document</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
              {copied ? 'Copied' : 'Copy'}
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Search within document bar */}
        <div className="px-6 py-2.5 bg-white border-b border-slate-100 flex items-center gap-2">
          <Search className="w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Search within this document..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full text-xs text-slate-800 focus:outline-none placeholder-slate-400"
          />
          {searchTerm && (
            <button onClick={() => setSearchTerm('')} className="text-xs text-slate-400 hover:text-slate-600">
              Clear
            </button>
          )}
        </div>

        {/* Modal Body */}
        <div className="flex-1 p-6 overflow-y-auto bg-slate-50/50 font-mono text-xs leading-relaxed text-slate-800">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-20 text-slate-400">
              <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mb-3"></div>
              <p className="font-sans text-sm">Loading document...</p>
            </div>
          ) : error ? (
            <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 font-sans">
              <p className="font-semibold">Error Loading Document</p>
              <p className="text-xs mt-1">{error}</p>
            </div>
          ) : (
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm whitespace-pre-wrap font-sans text-sm text-slate-700">
              {docContent?.content.split('\n').map((line, idx) => {
                const isSectionMatch = sectionTitle && line.toLowerCase().includes(sectionTitle.toLowerCase());
                const isSearchMatch = searchTerm && line.toLowerCase().includes(searchTerm.toLowerCase());
                
                let highlightClass = '';
                if (isSectionMatch) highlightClass = 'bg-emerald-100 text-emerald-950 font-semibold px-1 rounded';
                else if (isSearchMatch) highlightClass = 'bg-amber-100 text-amber-950 font-medium px-1 rounded';

                return (
                  <div key={idx} className={`py-0.5 ${highlightClass}`}>
                    {line}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="px-6 py-3 border-t border-slate-200 bg-white flex items-center justify-between text-xs text-slate-500">
          <span>Total Lines: {docContent?.line_count || 0}</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 text-white font-medium hover:bg-slate-900 transition-colors"
          >
            Close Reader
          </button>
        </div>

      </div>
    </div>
  );
}
