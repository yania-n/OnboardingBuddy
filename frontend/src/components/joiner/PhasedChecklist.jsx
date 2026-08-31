import React, { useState } from 'react';
import { 
  CheckCircle2, 
  Circle, 
  Clock, 
  ShieldAlert, 
  FileText, 
  ExternalLink, 
  BookOpen, 
  Users, 
  Award, 
  ChevronDown, 
  ChevronUp, 
  Wrench,
  Sparkles,
  Info
} from 'lucide-react';
import { toggleTaskCompletion } from '../../api/client';

const CATEGORY_CONFIG = {
  access_setup: { label: 'Tool Access', icon: Wrench, color: 'bg-blue-50 text-blue-700 border-blue-200' },
  training: { label: 'Training', icon: BookOpen, color: 'bg-purple-50 text-purple-700 border-purple-200' },
  meeting: { label: '1-on-1 Sync', icon: Users, color: 'bg-amber-50 text-amber-700 border-amber-200' },
  reading: { label: 'Doc Reading', icon: FileText, color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
  deliverable: { label: 'Deliverable', icon: Award, color: 'bg-rose-50 text-rose-700 border-rose-200' }
};

export default function PhasedChecklist({
  plan,
  onTaskToggled,
  onOpenDoc,
  activeFilter,
  setActiveFilter
}) {
  const [expandedPhases, setExpandedPhases] = useState({
    "Phase 1: Welcome (Days 1–2)": true,
    "Phase 2: Bearings (Days 3–5)": true,
    "Phase 3: Learning (Days 6–29)": true,
    "Phase 4: Hands Dirty (Days 30–50)": true,
    "Phase 5: Ready to Own (Days 61–89)": true,
    "Phase 6: Finish Line (Day 90)": true,
  });

  const togglePhase = (phase) => {
    setExpandedPhases((prev) => ({ ...prev, [phase]: !prev[phase] }));
  };

  const handleCheck = async (taskId, currentCompleted) => {
    try {
      const res = await toggleTaskCompletion(taskId, !currentCompleted);
      onTaskToggled(taskId, res.is_completed, res.plan_stats);
    } catch (e) {
      console.error(e);
      alert('Error updating task: ' + e.message);
    }
  };

  // Group tasks by phase
  const phasesOrder = [
    "Phase 1: Welcome (Days 1–2)",
    "Phase 2: Bearings (Days 3–5)",
    "Phase 3: Learning (Days 6–29)",
    "Phase 4: Hands Dirty (Days 30–50)",
    "Phase 5: Ready to Own (Days 61–89)",
    "Phase 6: Finish Line (Day 90)"
  ];

  const grouped = {};
  phasesOrder.forEach((p) => { grouped[p] = []; });

  (plan?.tasks || []).forEach((t) => {
    if (!grouped[t.phase]) grouped[t.phase] = [];
    grouped[t.phase].push(t);
  });

  // Filter phases if activeFilter is set
  const displayedPhases = phasesOrder.filter((p) => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'day1') return p.includes('Phase 1');
    if (activeFilter === 'week1') return p.includes('Phase 2');
    if (activeFilter === 'month1') return p.includes('Phase 3');
    if (activeFilter === 'month3') return p.includes('Phase 4') || p.includes('Phase 5') || p.includes('Phase 6');
    return true;
  });

  return (
    <div className="space-y-6">
      
      {/* Quick Phase Filter Pills */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        <button
          onClick={() => setActiveFilter('all')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
            activeFilter === 'all'
              ? 'bg-slate-900 text-white shadow-sm'
              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          All 6 Phases
        </button>
        <button
          onClick={() => setActiveFilter('day1')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
            activeFilter === 'day1'
              ? 'bg-brand-600 text-white shadow-sm'
              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          Day 1 (Welcome)
        </button>
        <button
          onClick={() => setActiveFilter('week1')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
            activeFilter === 'week1'
              ? 'bg-brand-600 text-white shadow-sm'
              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          Week 1 (Bearings)
        </button>
        <button
          onClick={() => setActiveFilter('month1')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
            activeFilter === 'month1'
              ? 'bg-brand-600 text-white shadow-sm'
              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          Month 1 (Learning)
        </button>
        <button
          onClick={() => setActiveFilter('month3')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
            activeFilter === 'month3'
              ? 'bg-brand-600 text-white shadow-sm'
              : 'bg-white text-slate-600 hover:bg-slate-100 border border-slate-200'
          }`}
        >
          Days 30–90 (Ownership)
        </button>
      </div>

      {/* Phased Accordions */}
      <div className="space-y-4">
        {displayedPhases.map((phase) => {
          const tasksInPhase = grouped[phase] || [];
          if (tasksInPhase.length === 0) return null;

          const completedCount = tasksInPhase.filter((t) => t.is_completed).length;
          const isPhaseDone = completedCount === tasksInPhase.length && tasksInPhase.length > 0;
          const isExpanded = expandedPhases[phase] !== false;

          return (
            <div
              key={phase}
              className={`bg-white rounded-2xl border transition-all overflow-hidden ${
                isPhaseDone ? 'border-emerald-200 shadow-2xs' : 'border-slate-200 shadow-sm'
              }`}
            >
              
              {/* Phase Accordion Header */}
              <div
                onClick={() => togglePhase(phase)}
                className="px-6 py-4 flex items-center justify-between cursor-pointer hover:bg-slate-50/80 transition-colors select-none"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs ${
                    isPhaseDone
                      ? 'bg-emerald-500 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-700 border border-slate-200'
                  }`}>
                    {isPhaseDone ? <CheckCircle2 className="w-5 h-5" /> : tasksInPhase[0]?.phase.split(' ')[1] || '•'}
                  </div>

                  <div>
                    <h4 className="font-bold text-sm text-slate-900 flex items-center gap-2">
                      {phase}
                      {isPhaseDone && (
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 border border-emerald-200">
                          Phase Completed
                        </span>
                      )}
                    </h4>
                    <p className="text-xs text-slate-500">
                      {completedCount} of {tasksInPhase.length} tasks completed
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <div className="w-28 bg-slate-100 rounded-full h-2 overflow-hidden hidden sm:block">
                    <div
                      className="bg-brand-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${(completedCount / tasksInPhase.length) * 100}%` }}
                    ></div>
                  </div>
                  {isExpanded ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
                </div>
              </div>

              {/* Tasks List */}
              {isExpanded && (
                <div className="divide-y divide-slate-100 px-6 pb-3 pt-1">
                  {tasksInPhase.map((task) => {
                    const cfg = CATEGORY_CONFIG[task.category] || CATEGORY_CONFIG.training;
                    const IconComponent = cfg.icon;

                    return (
                      <div
                        key={task.id}
                        className={`py-4 flex items-start gap-4 transition-all ${
                          task.is_completed ? 'opacity-70' : 'opacity-100'
                        }`}
                      >
                        
                        {/* Checkbox */}
                        <button
                          onClick={() => handleCheck(task.id, task.is_completed)}
                          className="mt-0.5 flex-shrink-0 transition-transform active:scale-90"
                          title={task.is_completed ? "Mark pending" : "Mark completed"}
                        >
                          {task.is_completed ? (
                            <CheckCircle2 className="w-6 h-6 text-brand-600 fill-brand-50" />
                          ) : (
                            <Circle className="w-6 h-6 text-slate-300 hover:text-brand-500" />
                          )}
                        </button>

                        {/* Task Details */}
                        <div className="flex-1 space-y-1.5">
                          <div className="flex flex-wrap items-center gap-2">
                            <h5 className={`text-xs font-bold ${
                              task.is_completed ? 'line-through text-slate-500' : 'text-slate-900'
                            }`}>
                              {task.title}
                            </h5>

                            {/* Category Badge */}
                            <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-md border ${cfg.color}`}>
                              <IconComponent className="w-3 h-3" />
                              {cfg.label}
                            </span>

                            {/* SLA Badge */}
                            {task.sla && (
                              <span className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 border border-slate-200">
                                <Clock className="w-3 h-3 text-slate-400" />
                                SLA: {task.sla}
                              </span>
                            )}
                          </div>

                          <p className="text-xs text-slate-600 leading-relaxed font-sans">
                            {task.description}
                          </p>

                          {/* Tool details info bar */}
                          {task.provisioning_channel && (
                            <div className="p-2 bg-slate-50 border border-slate-200 rounded-lg text-[11px] text-slate-700 flex flex-wrap items-center gap-3">
                              <span>
                                <strong className="text-slate-900">Channel:</strong> {task.provisioning_channel}
                              </span>
                              {task.required_approvals && (
                                <span>
                                  <strong className="text-slate-900">Approvals:</strong> {task.required_approvals}
                                </span>
                              )}
                            </div>
                          )}

                          {/* KB Document Link */}
                          {task.kb_doc_reference && (
                            <div className="pt-1">
                              <button
                                onClick={() => onOpenDoc(task.kb_doc_reference)}
                                className="inline-flex items-center gap-1.5 text-[11px] font-semibold text-brand-700 hover:text-brand-800 bg-brand-50/70 hover:bg-brand-100/70 px-2.5 py-1 rounded-md border border-brand-200 transition-colors"
                              >
                                <FileText className="w-3 h-3" />
                                <span>View Source Doc: {task.kb_doc_reference.split('#')[0]}</span>
                                <ExternalLink className="w-2.5 h-2.5 opacity-60" />
                              </button>
                            </div>
                          )}

                        </div>

                      </div>
                    );
                  })}
                </div>
              )}

            </div>
          );
        })}
      </div>

    </div>
  );
}
