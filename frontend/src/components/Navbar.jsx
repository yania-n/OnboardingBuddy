import React from 'react';
import { 
  Users, 
  ShieldCheck, 
  UserCheck, 
  Sparkles, 
  BookOpen, 
  HelpCircle, 
  Network,
  CheckCircle2,
  ChevronDown
} from 'lucide-react';

export default function Navbar({
  currentView,
  setCurrentView,
  joiners,
  selectedJoiner,
  setSelectedJoiner,
  onOpenJoinerForm,
  onOpenOrgScanner,
  onOpenLearningPlans,
  onOpenFeedback,
  missingCount
}) {
  return (
    <header className="sticky top-0 z-40 bg-white/95 backdrop-blur border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-emerald-400 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-lg text-slate-900 tracking-tight">OnboardingBuddy</span>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                  AI Multi-Agent
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">CleanTech & Energy Ecosystem</p>
            </div>
          </div>

          {/* Center Navigation Tabs (Manager vs Joiner) */}
          <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200">
            <button
              onClick={() => setCurrentView('manager')}
              className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                currentView === 'manager'
                  ? 'bg-white text-brand-700 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <ShieldCheck className="w-4 h-4" />
              Manager Portal
            </button>
            <button
              onClick={() => setCurrentView('joiner')}
              className={`flex items-center gap-2 px-4 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                currentView === 'joiner'
                  ? 'bg-white text-brand-700 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <UserCheck className="w-4 h-4" />
              New Joiner Portal
            </button>
          </div>

          {/* Right Actions & Persona Switcher */}
          <div className="flex items-center gap-2">
            
            {/* Quick Admin Action Icons */}
            <button
              onClick={onOpenOrgScanner}
              title="Org Expert Knowledge & Live Scan"
              className="p-2 text-slate-600 hover:text-brand-600 hover:bg-slate-50 rounded-lg border border-slate-200 transition-colors"
            >
              <Network className="w-4 h-4" />
            </button>

            <button
              onClick={onOpenLearningPlans}
              title="Role Learning Plans Repository (.md)"
              className="p-2 text-slate-600 hover:text-brand-600 hover:bg-slate-50 rounded-lg border border-slate-200 transition-colors"
            >
              <BookOpen className="w-4 h-4" />
            </button>

            <button
              onClick={onOpenFeedback}
              title="Missing Information Feedback Log"
              className="relative p-2 text-slate-600 hover:text-amber-600 hover:bg-slate-50 rounded-lg border border-slate-200 transition-colors"
            >
              <HelpCircle className="w-4 h-4" />
              {missingCount > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 bg-amber-500 text-white rounded-full text-[10px] font-bold flex items-center justify-center animate-pulse">
                  {missingCount}
                </span>
              )}
            </button>

            {/* Persona Switcher Dropdown */}
            <div className="relative flex items-center pl-2 border-l border-slate-200">
              <label className="text-xs font-medium text-slate-500 mr-2 hidden sm:inline">Active Joiner:</label>
              <select
                value={selectedJoiner?.id || ''}
                onChange={(e) => {
                  const j = joiners.find((item) => item.id === e.target.value);
                  if (j) setSelectedJoiner(j);
                }}
                className="text-xs font-semibold text-slate-800 bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 pr-7 cursor-pointer"
              >
                {joiners.map((j) => (
                  <option key={j.id} value={j.id}>
                    {j.name} ({j.role} - {j.progress_percentage || 0}%)
                  </option>
                ))}
              </select>
            </div>

          </div>

        </div>
      </div>
    </header>
  );
}
