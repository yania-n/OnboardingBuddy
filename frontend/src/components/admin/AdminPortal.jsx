import React, { useState, useEffect } from 'react';
import { 
  Users, 
  UserPlus, 
  CheckCircle2, 
  Clock, 
  TrendingUp, 
  Search, 
  ArrowUpRight, 
  Trash2, 
  Sparkles,
  Building2,
  Briefcase,
  ChevronRight,
  Filter
} from 'lucide-react';
import { fetchJoiners, fetchDashboardStats, deleteJoiner } from '../../api/client';

export default function AdminPortal({
  onOpenJoinerForm,
  onSelectJoinerForPlan,
  onSwitchToJoinerView
}) {
  const [joiners, setJoiners] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBU, setSelectedBU] = useState('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [joinerList, dashStats] = await Promise.all([
        fetchJoiners(),
        fetchDashboardStats()
      ]);
      setJoiners(joinerList);
      setStats(dashStats);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to remove ${name}'s onboarding profile?`)) return;
    try {
      await deleteJoiner(id);
      await loadData();
    } catch (e) {
      console.error(e);
      alert('Error deleting joiner: ' + e.message);
    }
  };

  const filteredJoiners = joiners.filter((j) => {
    const matchSearch = j.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        j.role.toLowerCase().includes(searchTerm.toLowerCase()) ||
                        j.department.toLowerCase().includes(searchTerm.toLowerCase());
    const matchBU = selectedBU === 'all' || j.business_unit === selectedBU;
    return matchSearch && matchBU;
  });

  return (
    <div className="space-y-8 animate-fade-in">
      
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-xl font-bold text-slate-900">Admin & Manager Onboarding Portal</h1>
            <span className="px-2.5 py-0.5 rounded-full bg-brand-50 text-brand-700 text-xs font-bold border border-brand-200">
              Enterprise Hub
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Provision personalized AI roadmaps, track team onboarding velocity, and manage organization knowledge.
          </p>
        </div>

        <button
          onClick={onOpenJoinerForm}
          className="flex items-center gap-2 px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold rounded-xl shadow-md shadow-brand-500/20 transition-all hover:scale-[1.02] active:scale-[0.98] self-start md:self-auto"
        >
          <UserPlus className="w-4 h-4" />
          Provision New Joiner
        </button>
      </div>

      {/* Analytics KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Total Joiners</span>
            <Users className="w-4 h-4 text-brand-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">{stats?.total_joiners || 0}</div>
          <p className="text-[11px] text-slate-400">Across all 4 Business Units</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Active Roadmaps</span>
            <Briefcase className="w-4 h-4 text-blue-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">{stats?.active_plans || 0}</div>
          <p className="text-[11px] text-slate-400">Currently in 90-day lifecycle</p>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Avg. Completion</span>
            <TrendingUp className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">{stats?.average_progress_pct || 0}%</div>
          <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2">
            <div
              className="bg-emerald-500 h-1.5 rounded-full transition-all duration-500"
              style={{ width: `${stats?.average_progress_pct || 0}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-1">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider">Completed Tasks</span>
            <CheckCircle2 className="w-4 h-4 text-purple-600" />
          </div>
          <div className="text-2xl font-black text-slate-900">
            {stats?.completed_tasks || 0} <span className="text-sm font-semibold text-slate-400">/ {stats?.total_tasks || 0}</span>
          </div>
          <p className="text-[11px] text-slate-400">Verified checklist items</p>
        </div>

      </div>

      {/* Joiners Table Section */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden space-y-4">
        
        {/* Table Header & Controls */}
        <div className="p-5 border-b border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4 bg-slate-50/50">
          <div>
            <h3 className="font-bold text-sm text-slate-900">Active Employee Onboarding Plans</h3>
            <p className="text-xs text-slate-500">Select a joiner to inspect roadmap, preview tasks, or monitor real-time completion</p>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            {/* Search */}
            <div className="relative flex-1 sm:w-64">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search by name, role, dept..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-9 pr-3 py-1.5 text-xs bg-white border border-slate-200 rounded-xl text-slate-800 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>

            {/* BU Filter */}
            <select
              value={selectedBU}
              onChange={(e) => setSelectedBU(e.target.value)}
              className="text-xs bg-white border border-slate-200 rounded-xl px-3 py-1.5 text-slate-700 focus:outline-none focus:ring-2 focus:ring-brand-500 font-medium"
            >
              <option value="all">All Business Units</option>
              <option value="Electric Mobility">Electric Mobility</option>
              <option value="Solar Energy Systems">Solar Energy Systems</option>
              <option value="Energy Storage Systems">Energy Storage Systems</option>
              <option value="Central Commercial / Cross-BU">Central Commercial</option>
              <option value="Central Platforms & Corporate Operations">Central Operations</option>
            </select>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-200 text-[10px]">
              <tr>
                <th className="px-6 py-3">Employee Name</th>
                <th className="px-6 py-3">Role & Seniority</th>
                <th className="px-6 py-3">Department & BU</th>
                <th className="px-6 py-3">Start Date</th>
                <th className="px-6 py-3">Progress</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-100 text-slate-800">
              {filteredJoiners.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                    No joiners found matching filter criteria.
                  </td>
                </tr>
              ) : (
                filteredJoiners.map((j) => (
                  <tr key={j.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-bold text-slate-900">{j.name}</div>
                      <div className="text-[11px] text-slate-400">{j.email}</div>
                    </td>

                    <td className="px-6 py-4">
                      <div className="font-semibold text-slate-800">{j.role}</div>
                      <span className="inline-block mt-0.5 px-2 py-0.2 rounded text-[10px] font-medium bg-slate-100 text-slate-600 border border-slate-200">
                        {j.seniority}
                      </span>
                    </td>

                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-700">{j.department}</div>
                      <div className="text-[11px] text-brand-700 font-semibold">{j.business_unit}</div>
                    </td>

                    <td className="px-6 py-4 font-mono text-slate-600">
                      {j.start_date}
                    </td>

                    <td className="px-6 py-4">
                      <div className="w-36 space-y-1">
                        <div className="flex justify-between text-[10px] font-bold text-slate-600">
                          <span>{j.completed_tasks} / {j.total_tasks} Tasks</span>
                          <span className="text-brand-700">{j.progress_percentage || 0}%</span>
                        </div>
                        <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-brand-500 h-1.5 rounded-full transition-all duration-300"
                            style={{ width: `${j.progress_percentage || 0}%` }}
                          ></div>
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => onSwitchToJoinerView(j)}
                          className="flex items-center gap-1 px-3 py-1.5 bg-brand-50 text-brand-700 hover:bg-brand-100 font-semibold rounded-lg border border-brand-200 transition-colors"
                          title="Open New Joiner Portal for this employee"
                        >
                          Joiner View
                          <ArrowUpRight className="w-3 h-3" />
                        </button>

                        <button
                          onClick={() => handleDelete(j.id, j.name)}
                          className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Delete profile"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

      </div>

    </div>
  );
}
