import React, { useState } from 'react';
import { 
  X, 
  Sparkles, 
  Plus, 
  Trash2, 
  Save, 
  Check, 
  Clock, 
  ShieldCheck, 
  FileText, 
  Layers, 
  BookOpen 
} from 'lucide-react';
import { createJoiner, updatePlan } from '../../api/client';

const PHASES = [
  "Phase 1: Welcome (Days 1–2)",
  "Phase 2: Bearings (Days 3–5)",
  "Phase 3: Learning (Days 6–29)",
  "Phase 4: Hands Dirty (Days 30–50)",
  "Phase 5: Ready to Own (Days 61–89)",
  "Phase 6: Finish Line (Day 90)"
];

const CATEGORIES = [
  { value: 'access_setup', label: 'IT & Tool Access' },
  { value: 'training', label: 'Training & LMS' },
  { value: 'meeting', label: '1-on-1 & Team Sync' },
  { value: 'reading', label: 'Documentation & Reading' },
  { value: 'deliverable', label: 'Milestone Deliverable' }
];

export default function PlanEditorModal({ joinerData, previewPlanData, onClose, onPlanPublished }) {
  const [overview, setOverview] = useState(previewPlanData?.overview || '');
  const [tasks, setTasks] = useState(previewPlanData?.tasks || []);
  const [selectedPhase, setSelectedPhase] = useState(PHASES[0]);
  const [saving, setSaving] = useState(false);

  const handleTaskChange = (index, field, value) => {
    const updated = [...tasks];
    updated[index][field] = value;
    setTasks(updated);
  };

  const handleAddTask = () => {
    const newTask = {
      phase: selectedPhase,
      title: 'New Custom Onboarding Task',
      description: 'Describe the requirements and expected outcomes for this task.',
      category: 'training',
      tool_name: '',
      provisioning_channel: '',
      required_approvals: '',
      sla: '',
      kb_doc_reference: '07_GLOBAL_ONBOARDING_FRAMEWORK.md',
      is_completed: false,
      order_index: tasks.length + 1
    };
    setTasks([...tasks, newTask]);
  };

  const handleDeleteTask = (index) => {
    const updated = tasks.filter((_, i) => i !== index);
    setTasks(updated);
  };

  const handleSaveAndPublish = async () => {
    try {
      setSaving(true);
      // 1. Create the joiner
      const joiner = await createJoiner(joinerData);
      
      // 2. Fetch the plan created for this joiner to get planId
      const planRes = await fetch(`/api/plans/user/${joiner.id}`);
      const plan = await planRes.json();

      // 3. Update the plan with the manager's customized overview and task list
      await updatePlan(plan.id, {
        overview,
        tasks
      });

      onPlanPublished(joiner);
      onClose();
    } catch (err) {
      console.error(err);
      alert('Error publishing plan: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const filteredTasks = tasks.filter((t) => !selectedPhase || t.phase === selectedPhase);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white w-full max-w-5xl h-[90vh] rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-brand-500 rounded-lg text-white">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-base">Review & Customize AI Onboarding Roadmap</h3>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-900/60 text-emerald-300 border border-emerald-700">
                  {joinerData.role}
                </span>
              </div>
              <p className="text-xs text-slate-300">
                New Joiner: <span className="font-semibold text-white">{joinerData.name}</span> ({joinerData.department} - {joinerData.business_unit})
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Phase Selector Tabs */}
        <div className="px-6 py-2.5 bg-slate-100 border-b border-slate-200 flex items-center justify-between overflow-x-auto gap-2">
          <div className="flex items-center gap-1">
            {PHASES.map((p, idx) => (
              <button
                key={idx}
                onClick={() => setSelectedPhase(p)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all ${
                  selectedPhase === p
                    ? 'bg-white text-brand-700 shadow-xs border border-slate-200'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
                }`}
              >
                {p}
              </button>
            ))}
          </div>

          <button
            onClick={handleAddTask}
            className="flex items-center gap-1 px-3 py-1.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold rounded-lg shadow-2xs transition-colors flex-shrink-0"
          >
            <Plus className="w-3.5 h-3.5" />
            Add Task to Phase
          </button>
        </div>

        {/* Plan Body */}
        <div className="flex-1 p-6 overflow-y-auto bg-slate-50 space-y-4">
          
          {/* Plan Overview Editor */}
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs">
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1">
              Onboarding Objectives Overview
            </label>
            <textarea
              rows={2}
              value={overview}
              onChange={(e) => setOverview(e.target.value)}
              className="w-full text-xs p-2.5 bg-slate-50 border border-slate-200 rounded-lg focus:ring-2 focus:ring-brand-500 focus:bg-white text-slate-800"
            />
          </div>

          {/* Tasks in Selected Phase */}
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
              <span>Tasks in {selectedPhase} ({filteredTasks.length})</span>
              <span>Total Tasks in Roadmap: {tasks.length}</span>
            </div>

            {filteredTasks.length === 0 ? (
              <div className="p-8 text-center bg-white rounded-xl border border-dashed border-slate-300 text-slate-400">
                <p className="text-xs">No tasks in this phase yet.</p>
                <button
                  onClick={handleAddTask}
                  className="mt-2 text-xs font-semibold text-brand-600 hover:underline"
                >
                  + Add First Task
                </button>
              </div>
            ) : (
              filteredTasks.map((task, idx) => {
                const globalIndex = tasks.findIndex((t) => t === task);
                return (
                  <div
                    key={globalIndex}
                    className="bg-white p-4 rounded-xl border border-slate-200 shadow-2xs hover:border-slate-300 transition-all space-y-3"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2">
                          <span className="w-5 h-5 rounded-full bg-slate-100 text-slate-600 text-[10px] font-bold flex items-center justify-center flex-shrink-0">
                            {globalIndex + 1}
                          </span>
                          <input
                            type="text"
                            value={task.title}
                            onChange={(e) => handleTaskChange(globalIndex, 'title', e.target.value)}
                            className="flex-1 text-xs font-bold text-slate-900 bg-slate-50 px-2.5 py-1 rounded border border-slate-200 focus:bg-white focus:ring-1 focus:ring-brand-500"
                          />
                        </div>

                        <textarea
                          rows={2}
                          value={task.description}
                          onChange={(e) => handleTaskChange(globalIndex, 'description', e.target.value)}
                          className="w-full text-xs text-slate-600 bg-slate-50/50 p-2 rounded border border-slate-200 focus:bg-white focus:ring-1 focus:ring-brand-500"
                        />
                      </div>

                      <button
                        onClick={() => handleDeleteTask(globalIndex)}
                        className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        title="Delete task"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    {/* Metadata tags line */}
                    <div className="grid grid-cols-1 sm:grid-cols-4 gap-2 pt-2 border-t border-slate-100 text-[11px]">
                      <div>
                        <label className="text-[10px] text-slate-400 font-semibold block">Category</label>
                        <select
                          value={task.category}
                          onChange={(e) => handleTaskChange(globalIndex, 'category', e.target.value)}
                          className="w-full bg-slate-50 border border-slate-200 rounded px-1.5 py-0.5 text-slate-700"
                        >
                          {CATEGORIES.map((c) => (
                            <option key={c.value} value={c.value}>{c.label}</option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <label className="text-[10px] text-slate-400 font-semibold block">Tool / System</label>
                        <input
                          type="text"
                          placeholder="e.g. Jira / ServiceNow"
                          value={task.tool_name || ''}
                          onChange={(e) => handleTaskChange(globalIndex, 'tool_name', e.target.value)}
                          className="w-full bg-slate-50 border border-slate-200 rounded px-1.5 py-0.5 text-slate-700"
                        />
                      </div>

                      <div>
                        <label className="text-[10px] text-slate-400 font-semibold block">Approver & SLA</label>
                        <input
                          type="text"
                          placeholder="e.g. Direct Manager (24h)"
                          value={task.sla || task.required_approvals ? `${task.required_approvals || ''} (${task.sla || ''})` : ''}
                          onChange={(e) => {
                            handleTaskChange(globalIndex, 'sla', e.target.value);
                          }}
                          className="w-full bg-slate-50 border border-slate-200 rounded px-1.5 py-0.5 text-slate-700"
                        />
                      </div>

                      <div>
                        <label className="text-[10px] text-slate-400 font-semibold block">KB Reference</label>
                        <input
                          type="text"
                          placeholder="e.g. 10_ROLE_TOOLS_ACCESS_MATRIX.md"
                          value={task.kb_doc_reference || ''}
                          onChange={(e) => handleTaskChange(globalIndex, 'kb_doc_reference', e.target.value)}
                          className="w-full bg-slate-50 border border-slate-200 rounded px-1.5 py-0.5 text-slate-700"
                        />
                      </div>
                    </div>

                  </div>
                );
              })
            )}
          </div>

        </div>

        {/* Footer */}
        <div className="px-6 py-4 bg-white border-t border-slate-200 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Clicking <span className="font-semibold text-slate-800">Approve & Publish</span> will activate the employee profile and roadmap.
          </span>

          <div className="flex items-center gap-2.5">
            <button
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-slate-600 hover:text-slate-900 rounded-xl hover:bg-slate-100 transition-colors"
            >
              Back to Form
            </button>
            <button
              onClick={handleSaveAndPublish}
              disabled={saving || tasks.length === 0}
              className="flex items-center gap-1.5 px-5 py-2 text-xs font-semibold bg-brand-600 hover:bg-brand-700 text-white rounded-xl shadow-sm transition-all disabled:opacity-40"
            >
              {saving ? (
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Check className="w-3.5 h-3.5" />
              )}
              Approve & Publish Plan
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
