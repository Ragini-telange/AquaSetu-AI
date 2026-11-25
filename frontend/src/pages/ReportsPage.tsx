import React from 'react';
import {
  Download,
  ShieldCheck,
  Database,
  BarChart2,
  Calendar
} from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const auditReports = [
    {
      title: 'Maharashtra Phreatic Groundwater Depth Audit 2024–2025',
      category: 'Hydrological Survey',
      date: 'May 2024',
      size: '2.4 MB',
      description: 'Comprehensive evaluation of 3,737 CGWB observation wells spanning 32 Maharashtra districts. Includes pre-monsoon depletion stress indicators.',
      coverage: '3,737 Stations',
      status: 'Validated'
    },
    {
      title: 'Statewide Drinking Water Potability Screening & BIS Compliance',
      category: 'Quality Assessment',
      date: 'April 2024',
      size: '1.8 MB',
      description: 'Physicochemical evaluation across 11 parameters benchmarked against Bureau of Indian Standards (BIS IS 10500:2012) using XGBoost classifier.',
      coverage: '11 BIS Parameters',
      status: 'Statutory Benchmark'
    },
    {
      title: 'Statewide Groundwater Monitoring Network Spatial Topology',
      category: 'GIS & Spatial',
      date: 'March 2024',
      size: '3.1 MB',
      description: '2D KDTree spherical spatial indexing and Haversine distance matrix for 4,381 groundwater locations across all 33 Maharashtra districts.',
      coverage: '4,381 Locations',
      status: 'Indexed'
    },
    {
      title: 'Pune District Emergency Road Routing Network Topology',
      category: 'Network Routing',
      date: 'March 2024',
      size: '10.2 MB',
      description: 'Directed OpenStreetMap road graph analysis across 170,253 nodes and 409,399 edges with A*, Bidirectional, and BFS path benchmarks.',
      coverage: '170,253 Nodes',
      status: 'OSM Cached'
    }
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#E3EBE5] pb-5">
        <div>
          <div className="flex items-center gap-2 text-[#073B32] font-semibold text-xs tracking-wider uppercase">
            <span className="w-2 h-2 rounded-full bg-[#119B72]" />
            <span>Environmental Intelligence Governance &bull; Reports &amp; Audits</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#182C25] mt-1">
            State Water Resource Audits &amp; Data Reports
          </h1>
          <p className="text-[#718078] text-xs sm:text-sm mt-1">
            Certified technical reports, model validation benchmarks, and statutory compliance documentation for Maharashtra.
          </p>
        </div>

        <button
          onClick={() => window.print()}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#073B32] hover:bg-[#0B4F43] text-white text-xs font-semibold self-start sm:self-auto transition-colors"
        >
          <Download className="w-3.5 h-3.5 text-[#119B72]" />
          <span>Export Summary View</span>
        </button>
      </div>

      {/* Highlights KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-[#E3EBE5] shadow-xs">
          <div className="flex items-center gap-2 text-xs font-bold text-[#718078] uppercase mb-1">
            <Database className="w-4 h-4 text-[#119B72]" />
            <span>Monitored Well Records</span>
          </div>
          <p className="text-3xl font-extrabold text-[#182C25]">65,738</p>
          <p className="text-xs text-[#718078] mt-1">Empirical observation records logged (2021&ndash;2025)</p>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-[#E3EBE5] shadow-xs">
          <div className="flex items-center gap-2 text-xs font-bold text-[#718078] uppercase mb-1">
            <ShieldCheck className="w-4 h-4 text-[#119B72]" />
            <span>Standard Compliance</span>
          </div>
          <p className="text-3xl font-extrabold text-[#182C25]">IS 10500</p>
          <p className="text-xs text-[#718078] mt-1">Bureau of Indian Standards potable guidelines</p>
        </div>

        <div className="bg-white rounded-2xl p-5 border border-[#E3EBE5] shadow-xs">
          <div className="flex items-center gap-2 text-xs font-bold text-[#718078] uppercase mb-1">
            <BarChart2 className="w-4 h-4 text-[#119B72]" />
            <span>Validated Model Test R²</span>
          </div>
          <p className="text-3xl font-extrabold text-[#182C25]">0.7766</p>
          <p className="text-xs text-[#718078] mt-1">KNN distance-weighted test set score</p>
        </div>
      </div>

      {/* Reports List */}
      <div className="bg-white rounded-2xl border border-[#E3EBE5] p-6 shadow-xs space-y-4">
        <h3 className="text-sm font-bold text-[#182C25] uppercase tracking-wider">
          Available Scientific &amp; Operational Reports
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {auditReports.map((report, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] hover:bg-white hover:border-[#119B72]/40 transition-all flex flex-col justify-between space-y-3"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-[#EDF8F1] text-[#073B32] border border-[#D9F2E6]">
                    {report.category}
                  </span>
                  <span className="text-[11px] text-[#718078] flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />
                    {report.date}
                  </span>
                </div>
                <h4 className="font-bold text-[#182C25] text-sm leading-tight">
                  {report.title}
                </h4>
                <p className="text-xs text-[#718078] mt-1.5 leading-relaxed">
                  {report.description}
                </p>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-[#E3EBE5] text-xs">
                <span className="font-semibold text-[#073B32]">{report.coverage}</span>
                <span className="px-2 py-0.5 rounded bg-white border border-[#E3EBE5] text-[10px] font-bold text-[#119B72]">
                  {report.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
