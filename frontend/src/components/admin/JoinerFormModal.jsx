import React, { useState } from 'react';
import { X, Sparkles, UserPlus, Eye, Check } from 'lucide-react';
import { previewPlan, createJoiner } from '../../api/client';

const ROLES_SUGGESTIONS = [
  "Account Executive",
  "Marketing Analyst",
  "Product Owner",
  "Tech Recruiter",
  "Project Manager – Solar Energy Systems",
  "Graduate Trainee",
  "Senior Embedded Firmware Engineer",
  "Principal MLOps Engineer",
  "Solutions Engineer",
  "Customer Success Manager",
  "Battery Storage Architect"
];

const BU_OPTIONS = [
  "Electric Mobility",
  "Solar Energy Systems",
  "Energy Storage Systems",
  "Central Platforms & Corporate Operations",
  "Central Commercial / Cross-BU"
];

const DEPARTMENTS = [
  "Powertrain & Hardware Engineering",
  "Vehicle Embedded Software",
  "Vehicle Quality & Safety",
  "Solar Project Management & Delivery",
  "Photovoltaic Engineering",
  "Field Operations & Commissioning",
  "BESS Architecture & Battery Engineering",
  "Grid Integration & Telemetry",
  "Battery Analytics & MLOps",
  "Global Commercial Operations",
  "Global Talent Acquisition & HR",
  "Global Early Careers Program"
];

export default function JoinerFormModal({ onClose, onJoinerCreated, onOpenPlanEditor }) {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'Account Executive',
    team: 'Commercial Expansion',
    department: 'Global Commercial Operations',
    business_unit: 'Central Commercial / Cross-BU',
    seniority: 'Mid-Level',
    start_date: new Date().toISOString().split('T')[0]
  });

  const [loading, setLoading] = useState(false);
  const [previewLoading, setPreviewLoading] = useState(false);

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handlePreview = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.role) return;

    try {
      setPreviewLoading(true);
      const previewData = await previewPlan(formData);
      onOpenPlanEditor(formData, previewData);
    } catch (err) {
      console.error(err);
      alert('Error generating preview: ' + err.message);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name || !formData.email || !formData.role) return;

    try {
      setLoading(true);
      const newJoiner = await createJoiner(formData);
      onJoinerCreated(newJoiner);
      onClose();
    } catch (err) {
      console.error(err);
      alert('Error creating joiner: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white w-full max-w-2xl rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col">
        
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-brand-500 rounded-lg text-white">
              <UserPlus className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-base">Provision New Joiner Onboarding</h3>
              <p className="text-xs text-slate-300">Generate personalized phased roadmap with multi-agent AI</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 max-h-[75vh] overflow-y-auto">
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Full Name *
              </label>
              <input
                type="text"
                required
                placeholder="e.g. Jordan Hayes"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:bg-white text-slate-800"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Corporate Email *
              </label>
              <input
                type="email"
                required
                placeholder="jordan.hayes@enterprise.com"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:bg-white text-slate-800"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Role / Title *
              </label>
              <input
                type="text"
                list="roles-list"
                required
                value={formData.role}
                onChange={(e) => handleChange('role', e.target.value)}
                className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:bg-white text-slate-800 font-medium"
              />
              <datalist id="roles-list">
                {ROLES_SUGGESTIONS.map((r, i) => (
                  <option key={i} value={r} />
                ))}
              </datalist>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Seniority Level
              </label>
              <select
                value={formData.seniority}
                onChange={(e) => handleChange('seniority', e.target.value)}
                className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:bg-white text-slate-800"
              >
                <option value="Entry-Level / Trainee">Entry-Level / Trainee</option>
                <option value="Associate">Associate</option>
                <option value="Mid-Level">Mid-Level</option>
                <option value="Senior">Senior</option>
                <option value="Staff / Lead">Staff / Lead</option>
                <option value="Principal / Director">Principal / Director</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Business Unit (BU) *
              </label>
              <select
                value={formData.business_unit}
                onChange={(e) => handleChange('business_unit', e.target.value)}
                className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:bg-white text-slate-800"
              >
                {BU_OPTIONS.map((bu, i) => (
                  <option key={i} value={bu}>{bu}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Department *
              </label>
              <input
                type="text"
                list="departments-list"
                required
                value={formData.department}
                onChange={(e) => handleChange('department', e.target.value)}
                className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:bg-white text-slate-800"
              />
              <datalist id="departments-list">
                {DEPARTMENTS.map((d, i) => (
                  <option key={i} value={d} />
                ))}
              </datalist>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Team Name
              </label>
              <input
                type="text"
                placeholder="e.g. Inverter Firmware Core"
                value={formData.team}
                onChange={(e) => handleChange('team', e.target.value)}
                className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:bg-white text-slate-800"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
                Start Date
              </label>
              <input
                type="date"
                value={formData.start_date}
                onChange={(e) => handleChange('start_date', e.target.value)}
                className="w-full text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-brand-500 focus:bg-white text-slate-800"
              />
            </div>
          </div>

          <div className="p-3.5 bg-brand-50/70 border border-brand-200 rounded-xl text-xs text-brand-900 flex items-start gap-2.5">
            <Sparkles className="w-4 h-4 text-brand-600 flex-shrink-0 mt-0.5" />
            <div>
              <span className="font-bold">Multi-Agent Workflow:</span> Our Org Expert Agent retrieves reporting lines & RACI, the Learning Expert creates/reuses the role `.md` plan, and the Plan Generator assembles a standardized 6-phase roadmap with required tool SLAs.
            </div>
          </div>

          {/* Footer Actions */}
          <div className="pt-3 border-t border-slate-200 flex items-center justify-end gap-2.5">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 rounded-xl hover:bg-slate-100 transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handlePreview}
              disabled={previewLoading || !formData.name || !formData.email}
              className="flex items-center gap-1.5 px-4 py-2 text-xs font-semibold bg-white border border-brand-500 text-brand-700 hover:bg-brand-50 rounded-xl shadow-2xs transition-all disabled:opacity-40"
            >
              {previewLoading ? (
                <div className="w-3.5 h-3.5 border-2 border-brand-600 border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Eye className="w-3.5 h-3.5" />
              )}
              Preview & Edit AI Plan
            </button>
            <button
              type="submit"
              disabled={loading || !formData.name || !formData.email}
              className="flex items-center gap-1.5 px-5 py-2 text-xs font-semibold bg-brand-600 hover:bg-brand-700 text-white rounded-xl shadow-sm transition-all disabled:opacity-40"
            >
              {loading ? (
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Check className="w-3.5 h-3.5" />
              )}
              Create & Publish Plan
            </button>
          </div>

        </form>

      </div>
    </div>
  );
}
