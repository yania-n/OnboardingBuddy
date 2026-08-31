import React, { useState, useEffect } from 'react';
import { 
  X, 
  Network, 
  RefreshCw, 
  ShieldCheck, 
  Layers, 
  CheckCircle2, 
  AlertTriangle,
  ChevronRight,
  Sparkles,
  Building2
} from 'lucide-react';
import { fetchOrgSummary, triggerOrgScan } from '../../api/client';

export default function OrgScannerModal({ onClose }) {
  const [orgData, setOrgData] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('hierarchy');

  useEffect(() => {
    loadSummary();
  }, []);

  const loadSummary = async () => {
    try {
      setLoading(true);
      const data = await fetchOrgSummary();
      setOrgData(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerScan = async () => {
    try {
      setScanning(true);
      const res = await triggerOrgScan();
      setOrgData(res.org_graph || res);
      await loadSummary();
    } catch (e) {
      console.error(e);
      alert('Error triggering scan: ' + e.message);
    } finally {
      setScanning(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in">
      <div className="bg-white w-full max-w-5xl h-[88vh] rounded-2xl shadow-2xl border border-slate-200 flex flex-col overflow-hidden">
        
        {/* Header */}
        <div className="px-6 py-4 bg-slate-900 text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-emerald-500 rounded-lg text-white">
              <Network className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-base">Organization Expert Agent & Knowledge Graph</h3>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-900/60 text-emerald-300 border border-emerald-700">
                  Persistent Storage
                </span>
              </div>
              <p className="text-xs text-slate-300">
                Scans KB documents to track BU hierarchies, reporting structures, and RACI matrices without re-building per joiner
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleTriggerScan}
              disabled={scanning}
              className="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 text-white text-xs font-semibold rounded-lg shadow-sm transition-all"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${scanning ? 'animate-spin' : ''}`} />
              {scanning ? 'Scanning Knowledge Base...' : 'Scan KB for Org Changes'}
            </button>
            <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-white rounded-lg transition-colors">
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scan Status Banner */}
        <div className="px-6 py-2.5 bg-slate-100 border-b border-slate-200 flex flex-wrap items-center justify-between text-xs text-slate-600 gap-2">
          <div className="flex items-center gap-4">
            <span>
              <strong className="text-slate-900">Last Scanned:</strong>{' '}
              {orgData?.last_scanned_at ? new Date(orgData.last_scanned_at).toLocaleString() : 'Just now'}
            </span>
            <span>
              <strong className="text-slate-900">Storage File:</strong>{' '}
              <code className="bg-white px-1.5 py-0.5 rounded border border-slate-200 text-slate-800 text-[11px]">
                backend/data/org_knowledge.json
              </code>
            </span>
          </div>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setActiveTab('hierarchy')}
              className={`px-3 py-1 rounded-md text-xs font-semibold ${
                activeTab === 'hierarchy' ? 'bg-white text-brand-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              BU Hierarchy
            </button>
            <button
              onClick={() => setActiveTab('raci')}
              className={`px-3 py-1 rounded-md text-xs font-semibold ${
                activeTab === 'raci' ? 'bg-white text-brand-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Executive RACI
            </button>
            <button
              onClick={() => setActiveTab('changes')}
              className={`px-3 py-1 rounded-md text-xs font-semibold ${
                activeTab === 'changes' ? 'bg-white text-brand-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              Scan Logs & Changes
            </button>
          </div>
        </div>

        {/* Body Content */}
        <div className="flex-1 p-6 overflow-y-auto bg-slate-50 space-y-6">
          {loading ? (
            <div className="flex items-center justify-center py-20 text-slate-400">
              <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          ) : activeTab === 'hierarchy' ? (
            <>
              {/* C-Suite Cards */}
              <div>
                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
                  Executive Leadership (C-Suite)
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {orgData?.c_suite?.map((c, i) => (
                    <div key={i} className="bg-white p-3.5 rounded-xl border border-slate-200 shadow-2xs">
                      <div className="flex items-center gap-2 text-slate-900 font-bold text-xs">
                        <Building2 className="w-4 h-4 text-brand-600" />
                        {c.role}
                      </div>
                      <p className="text-[11px] text-slate-600 mt-1.5 leading-snug">{c.focus}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Business Units Grid */}
              <div>
                <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">
                  Business Units & Operational Departments
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {Object.entries(orgData?.business_units || {}).map(([buName, buInfo], idx) => (
                    <div key={idx} className="bg-white p-5 rounded-2xl border border-slate-200 shadow-2xs space-y-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <h5 className="font-bold text-sm text-slate-900">{buName}</h5>
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">
                              {buInfo.code}
                            </span>
                          </div>
                          <p className="text-xs font-semibold text-brand-700 mt-0.5">{buInfo.executive_lead}</p>
                        </div>
                      </div>

                      <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                        {buInfo.focus}
                      </p>

                      <div>
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1.5">
                          Departments & Core Teams:
                        </span>
                        <div className="space-y-1.5">
                          {Object.entries(buInfo.departments || {}).map(([dept, teams], dIdx) => (
                            <div key={dIdx} className="text-xs text-slate-700 bg-white border border-slate-100 p-2 rounded-lg">
                              <span className="font-bold text-slate-900">{dept}:</span>{' '}
                              <span className="text-slate-600">{Array.isArray(teams) ? teams.join(', ') : teams}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Cross-BU Synergies */}
              <div className="bg-gradient-to-r from-emerald-500/10 to-teal-500/10 p-5 rounded-2xl border border-emerald-200/60">
                <h4 className="text-xs font-bold text-emerald-950 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-emerald-600" />
                  Closed-Loop Clean Energy Synergies
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
                  {orgData?.cross_bu_synergies?.map((syn, sIdx) => (
                    <div key={sIdx} className="bg-white/90 backdrop-blur p-3.5 rounded-xl border border-emerald-200 shadow-2xs">
                      <h6 className="font-bold text-xs text-slate-900">{syn.title}</h6>
                      <p className="text-[11px] text-slate-600 mt-1 leading-relaxed">{syn.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : activeTab === 'raci' ? (
            <div className="bg-white rounded-2xl border border-slate-200 shadow-2xs overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-200">
                <h4 className="font-bold text-sm text-slate-900">Executive Decision RACI Matrix</h4>
                <p className="text-xs text-slate-500">
                  Accountability and consultation flow across corporate strategic initiatives
                </p>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 text-slate-500 font-bold border-b border-slate-200">
                    <tr>
                      <th className="px-6 py-3">Strategic Initiative</th>
                      <th className="px-6 py-3">Accountable (A)</th>
                      <th className="px-6 py-3">Responsible (R)</th>
                      <th className="px-6 py-3">Consulted (C)</th>
                      <th className="px-6 py-3">Informed (I)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-800">
                    {orgData?.executive_raci?.map((row, rIdx) => (
                      <tr key={rIdx} className="hover:bg-slate-50/60">
                        <td className="px-6 py-3.5 font-bold text-slate-900">{row.initiative}</td>
                        <td className="px-6 py-3.5">
                          <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-800 font-semibold">{row.accountable}</span>
                        </td>
                        <td className="px-6 py-3.5">
                          <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold">{row.responsible}</span>
                        </td>
                        <td className="px-6 py-3.5 text-slate-600">{row.consulted || '—'}</td>
                        <td className="px-6 py-3.5 text-slate-500">{row.informed || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-2xs space-y-4">
              <h4 className="font-bold text-sm text-slate-900">Knowledge Base Scan History & Change Logs</h4>
              <p className="text-xs text-slate-500">
                When documents in <code className="bg-slate-100 px-1 py-0.5 rounded text-slate-700">kb_docs/</code> are edited or added, the Org Expert Agent detects hash differences and updates the graph.
              </p>

              <div className="space-y-2">
                {orgData?.changes_detected?.map((log, lIdx) => (
                  <div key={lIdx} className="flex items-center gap-2.5 p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-800">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                    <span>{log}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 bg-white border-t border-slate-200 flex items-center justify-between text-xs text-slate-500">
          <span>Org Entities Tracked: {Object.keys(orgData?.business_units || {}).length} BUs, {orgData?.all_departments?.length || 0} Departments</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 text-white font-medium hover:bg-slate-900 transition-colors"
          >
            Close Inspector
          </button>
        </div>

      </div>
    </div>
  );
}
