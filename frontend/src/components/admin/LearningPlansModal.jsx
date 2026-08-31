import React, { useState, useEffect } from 'react';
import { 
  X, 
  BookOpen, 
  FileText, 
  Edit3, 
  Save, 
  Check, 
  Plus, 
  Sparkles,
  ExternalLink 
} from 'lucide-react';
import { fetchLearningPlans, fetchLearningPlan, updateLearningPlan } from '../../api/client';

export default function LearningPlansModal({ onClose }) {
  const [plans, setPlans] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [markdownContent, setMarkdownContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      setLoading(true);
      const data = await fetchLearningPlans();
      setPlans(data);
      if (data.length > 0 && !selectedPlan) {
        handleSelectPlan(data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPlan = async (plan) => {
    setSelectedPlan(plan);
    setIsEditing(false);
    try {
      const data = await fetchLearningPlan(plan.role_slug);
      setMarkdownContent(data.markdown_content);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSave = async () => {
    if (!selectedPlan) return;
    try {
      setSaving(true);
      await updateLearningPlan(selectedPlan.role_slug, markdownContent);
      setSavedSuccess(true);
      setIsEditing(false);
      setTimeout(() => setSavedSuccess(false), 2500);
      await loadPlans();
    } catch (e) {
      console.error(e);
      alert('Error saving plan: ' + e.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white w-full max-w-5xl h-[88vh] rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-brand-500 rounded-lg text-white">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-base">Learning Expert Agent - Role Learning Plans (.md)</h3>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-900/60 text-emerald-300 border border-emerald-700">
                  Reusable File Storage
                </span>
              </div>
              <p className="text-xs text-slate-300">
                Maintains and reuses role-specific markdown curriculum files stored in <code className="text-emerald-300">backend/data/learning_plans/</code>
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Layout */}
        <div className="flex-1 flex overflow-hidden">
          
          {/* Left Sidebar: Plan Files List */}
          <div className="w-80 border-r border-slate-200 bg-slate-50 flex flex-col">
            <div className="p-4 border-b border-slate-200 flex items-center justify-between">
              <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                Saved Learning Plans ({plans.length})
              </span>
            </div>

            <div className="flex-1 overflow-y-auto p-2 space-y-1">
              {plans.map((p) => {
                const isSelected = selectedPlan?.role_slug === p.role_slug;
                return (
                  <button
                    key={p.role_slug}
                    onClick={() => handleSelectPlan(p)}
                    className={`w-full text-left p-3 rounded-xl text-xs transition-all flex items-start gap-2.5 ${
                      isSelected
                        ? 'bg-white text-brand-800 shadow-sm border border-brand-200 font-semibold'
                        : 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900'
                    }`}
                  >
                    <FileText className={`w-4 h-4 flex-shrink-0 mt-0.5 ${isSelected ? 'text-brand-600' : 'text-slate-400'}`} />
                    <div className="truncate">
                      <div className="truncate font-medium">{p.role_title}</div>
                      <div className="text-[10px] text-slate-400 font-mono mt-0.5">{p.file_name}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Editor / Viewer Area */}
          <div className="flex-1 flex flex-col bg-white overflow-hidden">
            
            {/* Action Bar */}
            <div className="px-6 py-3 border-b border-slate-200 flex items-center justify-between bg-slate-50/50">
              <div className="flex items-center gap-2">
                <span className="font-bold text-xs text-slate-900">{selectedPlan?.file_name}</span>
                {savedSuccess && (
                  <span className="flex items-center gap-1 text-[11px] text-emerald-600 font-bold bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                    <Check className="w-3 h-3" /> Saved to Disk
                  </span>
                )}
              </div>

              <div className="flex items-center gap-2">
                {isEditing ? (
                  <>
                    <button
                      onClick={() => setIsEditing(false)}
                      className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-100 rounded-lg"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={saving}
                      className="flex items-center gap-1 px-4 py-1.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold rounded-lg shadow-sm"
                    >
                      <Save className="w-3.5 h-3.5" />
                      {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="flex items-center gap-1 px-3.5 py-1.5 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-lg shadow-2xs"
                  >
                    <Edit3 className="w-3.5 h-3.5 text-slate-500" />
                    Edit Markdown
                  </button>
                )}
              </div>
            </div>

            {/* Markdown Content Area */}
            <div className="flex-1 p-6 overflow-y-auto">
              {isEditing ? (
                <textarea
                  value={markdownContent}
                  onChange={(e) => setMarkdownContent(e.target.value)}
                  className="w-full h-full p-4 font-mono text-xs text-slate-800 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:bg-white resize-none"
                />
              ) : (
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-2xs font-sans text-xs leading-relaxed text-slate-700 whitespace-pre-wrap">
                  {markdownContent}
                </div>
              )}
            </div>

          </div>

        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-white border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
          <span>Plans are cached per role and automatically injected into new employee roadmaps.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 text-white font-medium hover:bg-slate-900 transition-colors"
          >
            Close Repository
          </button>
        </div>

      </div>
    </div>
  );
}
