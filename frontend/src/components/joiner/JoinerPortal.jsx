import React, { useState, useEffect } from 'react';
import { 
  User, 
  Calendar, 
  Building2, 
  Sparkles, 
  MessageSquare, 
  CheckCircle2, 
  Clock, 
  Award,
  ChevronRight,
  TrendingUp,
  FileCheck
} from 'lucide-react';
import { fetchUserPlan } from '../../api/client';
import PhasedChecklist from './PhasedChecklist';

export default function JoinerPortal({
  selectedJoiner,
  onOpenDoc,
  onOpenChatbot,
  isChatbotOpen
}) {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all');

  useEffect(() => {
    loadPlan();
  }, [selectedJoiner?.id]);

  const loadPlan = async () => {
    if (!selectedJoiner?.id) return;
    try {
      setLoading(true);
      const data = await fetchUserPlan(selectedJoiner.id);
      setPlan(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleTaskToggled = (taskId, isCompleted, planStats) => {
    if (!plan) return;
    const updatedTasks = plan.tasks.map((t) =>
      t.id === taskId ? { ...t, is_completed: isCompleted } : t
    );
    setPlan({
      ...plan,
      tasks: updatedTasks,
      stats: planStats || plan.stats
    });
  };

  const totalTasks = plan?.stats?.total_tasks || plan?.tasks?.length || 0;
  const completedTasks = plan?.stats?.completed_tasks || plan?.tasks?.filter((t) => t.is_completed).length || 0;
  const pct = plan?.stats?.progress_percentage ?? (totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0);

  return (
    <div className="space-y-8 animate-fade-in pb-20">
      
      {/* Joiner Profile & Progress Hero Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white rounded-3xl p-6 sm:p-8 shadow-xl border border-slate-800 relative overflow-hidden">
        
        {/* Subtle decorative background glow */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl -mr-20 -mt-20 pointer-events-none"></div>

        <div className="relative z-10 flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          
          {/* Left: Joiner Identity */}
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-500/20 text-brand-300 border border-brand-500/30 text-xs font-bold">
              <Sparkles className="w-3.5 h-3.5 text-brand-400" />
              Personalized 6-Phase AI Onboarding Roadmap
            </div>

            <div>
              <h1 className="text-2xl sm:text-3xl font-black tracking-tight text-white">
                Welcome, {selectedJoiner?.name}! 🎉
              </h1>
              <p className="text-sm text-slate-300 font-medium mt-1">
                {selectedJoiner?.seniority} <span className="text-brand-400 font-bold">{selectedJoiner?.role}</span>
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-y-2 gap-x-4 text-xs text-slate-300 pt-1">
              <span className="flex items-center gap-1.5 bg-slate-800/80 px-3 py-1 rounded-lg border border-slate-700">
                <Building2 className="w-3.5 h-3.5 text-brand-400" />
                {selectedJoiner?.department}
              </span>
              <span className="flex items-center gap-1.5 bg-slate-800/80 px-3 py-1 rounded-lg border border-slate-700">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                {selectedJoiner?.business_unit}
              </span>
              <span className="flex items-center gap-1.5 bg-slate-800/80 px-3 py-1 rounded-lg border border-slate-700">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                Started: {selectedJoiner?.start_date}
              </span>
            </div>
          </div>

          {/* Right: Progress Tracker Card */}
          <div className="bg-slate-800/90 backdrop-blur p-5 rounded-2xl border border-slate-700/80 min-w-[280px] flex items-center gap-5 shadow-inner">
            
            {/* Circular Progress Ring */}
            <div className="relative w-20 h-20 flex-shrink-0 flex items-center justify-center">
              <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
                <path
                  className="text-slate-700"
                  strokeWidth="3.5"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className="text-brand-500 transition-all duration-700 ease-out"
                  strokeDasharray={`${pct}, 100`}
                  strokeWidth="3.5"
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="none"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="absolute flex flex-col items-center justify-center">
                <span className="text-base font-black text-white">{pct}%</span>
                <span className="text-[8px] uppercase tracking-wider text-slate-400 font-bold">Done</span>
              </div>
            </div>

            {/* Stats Breakdown */}
            <div className="space-y-1">
              <div className="text-xs font-bold text-slate-300">Tasks Completed</div>
              <div className="text-xl font-extrabold text-white">
                {completedTasks} <span className="text-xs font-normal text-slate-400">/ {totalTasks} tasks</span>
              </div>
              <p className="text-[11px] text-brand-400 font-medium">
                {totalTasks - completedTasks === 0 ? 'All tasks completed! 🌟' : `${totalTasks - completedTasks} remaining`}
              </p>
            </div>

          </div>

        </div>

      </div>

      {/* Team & Organisation Brief */}
      {plan?.overview && (
        <div className="bg-white rounded-3xl p-6 sm:p-8 shadow-sm border border-slate-200 space-y-4">
          <div className="flex items-center gap-2.5 text-slate-900">
            <div className="p-2 bg-brand-50 text-brand-700 rounded-xl">
              <Building2 className="w-5 h-5 text-brand-600" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Your Team & Organisation Brief</h3>
              <p className="text-xs text-slate-500">A tailored introduction to your team, role alignment, key contacts, and culture.</p>
            </div>
          </div>
          <div className="text-xs text-slate-700 border-t border-slate-100 pt-4 leading-relaxed font-sans whitespace-pre-wrap">
            {plan.overview}
          </div>
        </div>
      )}

      {/* Main Checklist Section */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900">Your Phased Onboarding Checklist</h3>
            <p className="text-xs text-slate-500">
              Click checkboxes to update progress. Click <strong className="text-slate-700">"View Source Doc"</strong> on any task to view authoritative knowledge base references.
            </p>
          </div>

          <button
            onClick={onOpenChatbot}
            className="flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold rounded-xl shadow-md shadow-brand-500/20 transition-all"
          >
            <MessageSquare className="w-4 h-4" />
            {isChatbotOpen ? 'Assistant Open' : 'Ask AI Assistant'}
          </button>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400">
            <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin mb-3"></div>
            <p className="text-xs font-medium">Loading your personalized roadmap...</p>
          </div>
        ) : (
          <PhasedChecklist
            plan={plan}
            onTaskToggled={handleTaskToggled}
            onOpenDoc={onOpenDoc}
            activeFilter={activeFilter}
            setActiveFilter={setActiveFilter}
          />
        )}
      </div>

    </div>
  );
}
