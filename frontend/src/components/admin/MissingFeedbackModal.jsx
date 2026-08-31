import React, { useState, useEffect } from 'react';
import { 
  X, 
  HelpCircle, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  FileEdit, 
  Check, 
  MessageSquare,
  Sparkles,
  Trash2
} from 'lucide-react';
import { fetchMissingFeedback, resolveFeedback, deleteFeedback } from '../../api/client';

/**
 * MissingFeedbackModal Component
 * Displays a list of queries submitted by employees that could not be answered by the KB,
 * and allows administrators/managers to resolve them by updating the KB, or delete them.
 */
export default function MissingFeedbackModal({ onClose, onFeedbackUpdated }) {
  const [feedbackList, setFeedbackList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [resolvingId, setResolvingId] = useState(null);
  const [notes, setNotes] = useState('');
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    loadFeedback();
  }, []);

  /**
   * Loads all missing feedback items from the backend and updates the local state.
   */
  const loadFeedback = async () => {
    try {
      setLoading(true);
      const data = await fetchMissingFeedback();
      setFeedbackList(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Submits a resolution for a missing feedback item, marking it as resolved.
   * @param {string} id - The ID of the feedback entry to resolve.
   */
  const handleResolve = async (id) => {
    try {
      await resolveFeedback(id, notes || 'Resolved and documented in KB');
      setResolvingId(null);
      setNotes('');
      await loadFeedback();
      if (onFeedbackUpdated) onFeedbackUpdated();
    } catch (e) {
      console.error(e);
      alert('Error resolving feedback: ' + e.message);
    }
  };

  /**
   * Prompts for confirmation and deletes a feedback query from backend.
   * @param {string} id - The ID of the feedback entry to delete.
   */
  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to permanently delete this unanswered query feedback?')) {
      return;
    }
    try {
      await deleteFeedback(id);
      await loadFeedback();
      if (onFeedbackUpdated) onFeedbackUpdated();
    } catch (e) {
      console.error(e);
      alert('Error deleting feedback: ' + e.message);
    }
  };

  const filtered = feedbackList.filter((f) => {
    if (filter === 'pending') return f.status === 'pending';
    if (filter === 'resolved') return f.status === 'resolved';
    return true;
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white w-full max-w-4xl h-[85vh] rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-amber-500 rounded-lg text-white">
              <HelpCircle className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-base">Missing Information Feedback Center</h3>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-amber-900/60 text-amber-300 border border-amber-700">
                  Unanswered Queries
                </span>
              </div>
              <p className="text-xs text-slate-300">
                Queries where the AI Chatbot found no grounded answer in KB and referred the employee to their manager
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Filter bar */}
        <div className="px-6 py-2.5 bg-slate-100 border-b border-slate-200 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1 rounded-md font-semibold ${
                filter === 'all' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              All Queries ({feedbackList.length})
            </button>
            <button
              onClick={() => setFilter('pending')}
              className={`px-3 py-1 rounded-md font-semibold ${
                filter === 'pending' ? 'bg-white text-amber-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Pending ({feedbackList.filter((f) => f.status === 'pending').length})
            </button>
            <button
              onClick={() => setFilter('resolved')}
              className={`px-3 py-1 rounded-md font-semibold ${
                filter === 'resolved' ? 'bg-white text-emerald-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Resolved ({feedbackList.filter((f) => f.status === 'resolved').length})
            </button>
          </div>

          <span className="text-slate-500 font-mono text-[11px]">
            File: backend/data/missing_kb_queries.json
          </span>
        </div>

        {/* Feedback List */}
        <div className="flex-1 p-6 overflow-y-auto bg-slate-50 space-y-3">
          {loading ? (
            <div className="flex items-center justify-center py-20 text-slate-400">
              <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : filtered.length === 0 ? (
            <div className="p-12 text-center bg-white rounded-2xl border border-dashed border-slate-300 text-slate-400 space-y-2">
              <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-500" />
              <p className="text-sm font-semibold text-slate-700">No missing queries recorded</p>
              <p className="text-xs">All employee questions have been answered with grounded knowledge base citations!</p>
            </div>
          ) : (
            filtered.map((item) => (
              <div
                key={item.id}
                className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs hover:border-slate-300 transition-all space-y-2.5"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-1 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-xs text-slate-900">
                        {item.user_name || 'Anonymous Employee'}
                      </span>
                      {item.user_role && (
                        <span className="px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[10px] font-semibold border border-slate-200">
                          {item.user_role}
                        </span>
                      )}
                      {item.context_bu && (
                        <span className="text-[10px] text-slate-400 font-medium">
                          • {item.context_bu}
                        </span>
                      )}
                      <span className="text-[10px] text-slate-400 ml-auto flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(item.timestamp).toLocaleString()}
                      </span>
                    </div>

                    <div className="text-xs font-semibold text-slate-800 bg-amber-50/70 p-2.5 rounded-lg border border-amber-200/60 flex items-start gap-2">
                      <MessageSquare className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
                      <span>"{item.query}"</span>
                    </div>
                  </div>

                  <div>
                    {item.status === 'resolved' ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-50 text-emerald-700 text-xs font-bold border border-emerald-200">
                        <Check className="w-3 h-3" /> Resolved
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 text-xs font-bold border border-amber-200">
                        <AlertTriangle className="w-3 h-3" /> Pending
                      </span>
                    )}
                  </div>
                </div>

                {item.status === 'resolved' && item.resolution_notes && (
                  <div className="text-[11px] text-slate-600 bg-slate-50 p-2 rounded-lg border border-slate-100">
                    <span className="font-bold text-slate-700">Resolution Notes:</span> {item.resolution_notes}
                  </div>
                )}

                {item.status === 'pending' && (
                  <div className="pt-2 border-t border-slate-100 flex items-center justify-end gap-2">
                    {resolvingId === item.id ? (
                      <div className="flex items-center gap-2 w-full">
                        <input
                          type="text"
                          placeholder="Resolution note (e.g. Added policy to 02_COMPANY_HANDBOOK.md)..."
                          value={notes}
                          onChange={(e) => setNotes(e.target.value)}
                          className="flex-1 text-xs px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-slate-800"
                        />
                        <button
                          onClick={() => handleResolve(item.id)}
                          className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow-2xs"
                        >
                          Confirm Resolve
                        </button>
                        <button
                          onClick={() => setResolvingId(null)}
                          className="px-2 py-1.5 text-xs text-slate-500 hover:text-slate-800"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => {
                            setResolvingId(item.id);
                            setNotes('');
                          }}
                          className="flex items-center gap-1 px-3 py-1 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg shadow-2xs"
                        >
                          <FileEdit className="w-3 h-3 text-slate-400" />
                          Resolve & Add to KB
                        </button>
                        <button
                          onClick={() => handleDelete(item.id)}
                          className="flex items-center gap-1 px-3 py-1 bg-white border border-rose-200 hover:bg-rose-50 text-rose-700 text-xs font-semibold rounded-lg shadow-2xs transition-colors"
                        >
                          <Trash2 className="w-3 h-3 text-rose-500" />
                          Delete Query
                        </button>
                      </div>
                    )}
                  </div>
                )}

              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-white border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
          <span>Feedback loop automatically improves knowledge base coverage and agent accuracy.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 text-white font-medium hover:bg-slate-900 transition-colors"
          >
            Close Center
          </button>
        </div>

      </div>
    </div>
  );
}
