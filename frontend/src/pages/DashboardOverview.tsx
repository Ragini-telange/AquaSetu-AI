import React, { useState } from 'react';
import {
  Droplets,
  Activity,
  MapPin,
  Navigation,
  ArrowRight,
  ShieldCheck,
  Database,
  Compass,
  Cpu,
  Map,
  BarChart2,
  Layers,
  CheckCircle2
} from 'lucide-react';
import type { TabKey } from '../components/Sidebar';
import { MaharashtraMap } from '../components/MaharashtraMap';

interface DashboardProps {
  onNavigate: (tab: TabKey) => void;
}

export const DashboardOverview: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [activePreviewLayer, setActivePreviewLayer] = useState<'regression' | 'spatial'>('regression');

  // Real dataset administrative divisions (33 districts grouped by region)
  const regionalCoverage = [
    { region: 'Western Maharashtra', districts: 5, wells: 1042, share: 28 },
    { region: 'Marathwada', districts: 8, wells: 1120, share: 30 },
    { region: 'Vidarbha', districts: 11, wells: 985, share: 26 },
    { region: 'North Maharashtra', districts: 5, wells: 420, share: 11 },
    { region: 'Konkan Coastal', districts: 4, wells: 170, share: 5 },
  ];

  // Groundwater Depth Tier Breakdown from 3,737 monitored stations
  const depthTiers = [
    { label: 'Shallow (< 5 m bgl)', count: '1,158', percentage: 31, color: 'bg-[#119B72]', note: 'Adequate recharge zone' },
    { label: 'Moderate (5 – 10 m bgl)', count: '1,644', percentage: 44, color: 'bg-[#0B4F43]', note: 'Standard agricultural table' },
    { label: 'Deep (10 – 15 m bgl)', count: '673', percentage: 18, color: 'bg-[#E9A23B]', note: 'Pre-monsoon stress zone' },
    { label: 'Very Deep (> 15 m bgl)', count: '262', percentage: 7, color: 'bg-[#E45B55]', note: 'Severe groundwater depletion' },
  ];

  // BIS IS 10500:2012 Chemical Tolerance Reference
  const bisStandardsSummary = [
    { parameter: 'pH Level', standard: '6.5 – 8.5', unit: 'pH', compliance: 'Monitored' },
    { parameter: 'Total Dissolved Solids (TDS)', standard: '< 500', unit: 'mg/L', compliance: 'Thresholded' },
    { parameter: 'Total Hardness (as CaCO3)', standard: '< 200', unit: 'mg/L', compliance: 'Thresholded' },
    { parameter: 'Chloride (Cl-)', standard: '< 250', unit: 'mg/L', compliance: 'Thresholded' },
    { parameter: 'Sulphate (SO4)', standard: '< 200', unit: 'mg/L', compliance: 'Thresholded' },
    { parameter: 'Dissolved Iron (Fe)', standard: '< 1.0', unit: 'mg/L', compliance: 'Thresholded' },
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* Environmental Intelligence Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-[#073B32] border border-[#0B4F43] p-7 sm:p-9 text-white shadow-md">
        <div className="relative z-10 max-w-4xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#119B72]/20 border border-[#119B72]/40 text-[#D9F2E6] text-xs font-semibold mb-3.5">
            <ShieldCheck className="w-4 h-4 text-[#119B72]" />
            <span>State Environmental Water Resources Platform</span>
          </div>

          <h1 className="text-2xl sm:text-3xl md:text-4xl font-extrabold tracking-tight text-white mb-2.5">
            AquaSetu AI &mdash; Water Intelligence &amp; Environmental Monitoring Platform
          </h1>

          <p className="text-[#D9F2E6]/85 text-xs sm:text-sm leading-relaxed max-w-3xl mb-6">
            A unified environmental intelligence suite integrating empirical Central Ground Water Board (CGWB) monitoring,
            distance-weighted KNN groundwater depth prediction, XGBoost BIS IS 10500:2012 potability classification,
            statewide KDTree well discovery, and directed OpenStreetMap emergency road routing.
          </p>

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={() => onNavigate('map')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#119B72] hover:bg-[#0E8360] text-white font-bold text-xs sm:text-sm transition-all shadow-md shadow-[#119B72]/25"
            >
              <Map className="w-4 h-4" />
              <span>Open Maharashtra GIS Map</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => onNavigate('regression')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#0B4F43] hover:bg-[#0E6254] text-[#D9F2E6] border border-[#119B72]/40 font-semibold text-xs sm:text-sm transition-all"
            >
              <Droplets className="w-4 h-4 text-[#119B72]" />
              <span>Predict Water Level</span>
            </button>

            <button
              onClick={() => onNavigate('classification')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#0B4F43] hover:bg-[#0E6254] text-[#D9F2E6] border border-[#119B72]/40 font-semibold text-xs sm:text-sm transition-all"
            >
              <Activity className="w-4 h-4 text-[#119B72]" />
              <span>Water Testing Lab</span>
            </button>
          </div>
        </div>
      </div>

      {/* Verified System Statistics & KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Monitored Wells */}
        <div className="bg-white rounded-2xl p-5 border border-[#E3EBE5] shadow-xs hover:border-[#119B72]/40 transition-colors">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-bold text-[#718078] uppercase tracking-wider">Monitored Wells</span>
            <div className="p-2 rounded-xl bg-[#EDF8F1] text-[#119B72]">
              <Database className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-[#182C25]">3,737</p>
          <div className="flex items-center gap-1.5 mt-2 text-[11px] text-[#718078]">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#119B72] shrink-0" />
            <span>CGWB verified coordinates</span>
          </div>
        </div>

        {/* KPI 2: Spatial Locations */}
        <div className="bg-white rounded-2xl p-5 border border-[#E3EBE5] shadow-xs hover:border-[#119B72]/40 transition-colors">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-bold text-[#718078] uppercase tracking-wider">Spatial Monitoring Nodes</span>
            <div className="p-2 rounded-xl bg-[#EDF8F1] text-[#119B72]">
              <MapPin className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-[#182C25]">4,381</p>
          <div className="flex items-center gap-1.5 mt-2 text-[11px] text-[#718078]">
            <Compass className="w-3.5 h-3.5 text-[#119B72] shrink-0" />
            <span>Across 33 state districts</span>
          </div>
        </div>

        {/* KPI 3: Historical Observations */}
        <div className="bg-white rounded-2xl p-5 border border-[#E3EBE5] shadow-xs hover:border-[#119B72]/40 transition-colors">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-bold text-[#718078] uppercase tracking-wider">Historical Records</span>
            <div className="p-2 rounded-xl bg-[#EDF8F1] text-[#119B72]">
              <Droplets className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-[#182C25]">65,738</p>
          <div className="flex items-center gap-1.5 mt-2 text-[11px] text-[#718078]">
            <BarChart2 className="w-3.5 h-3.5 text-[#119B72] shrink-0" />
            <span>Sequential 2021&ndash;2025 readings</span>
          </div>
        </div>

        {/* KPI 4: Road Network Nodes */}
        <div className="bg-white rounded-2xl p-5 border border-[#E3EBE5] shadow-xs hover:border-[#119B72]/40 transition-colors">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[10px] font-bold text-[#718078] uppercase tracking-wider">Road Graph Nodes</span>
            <div className="p-2 rounded-xl bg-[#EDF8F1] text-[#119B72]">
              <Navigation className="w-4 h-4" />
            </div>
          </div>
          <p className="text-2xl sm:text-3xl font-extrabold text-[#182C25]">170,253</p>
          <div className="flex items-center gap-1.5 mt-2 text-[11px] text-[#718078]">
            <Layers className="w-3.5 h-3.5 text-[#119B72] shrink-0" />
            <span>409,399 directed OSM edges</span>
          </div>
        </div>
      </div>

      {/* Geographic Intelligence Map Preview */}
      <div className="bg-white rounded-2xl border border-[#E3EBE5] p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-bold text-[#073B32] uppercase tracking-wider flex items-center gap-1.5">
                <Map className="w-4 h-4 text-[#119B72]" />
                Interactive Maharashtra GIS Intelligence Preview
              </span>
            </div>
            <p className="text-xs text-[#718078]">
              Live map rendering 3,737 groundwater stations with on-demand depth predictions and spatial queries.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setActivePreviewLayer('regression')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${activePreviewLayer === 'regression'
                ? 'bg-[#073B32] text-white'
                : 'bg-[#F8FAF7] text-[#718078] hover:text-[#182C25] border border-[#E3EBE5]'
                }`}
            >
              Groundwater Depth
            </button>
            <button
              onClick={() => setActivePreviewLayer('spatial')}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${activePreviewLayer === 'spatial'
                ? 'bg-[#073B32] text-white'
                : 'bg-[#F8FAF7] text-[#718078] hover:text-[#182C25] border border-[#E3EBE5]'
                }`}
            >
              Spatial Search
            </button>
            <button
              onClick={() => onNavigate('map')}
              className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#119B72] hover:bg-[#0E8360] text-white transition-colors"
            >
              <span>Full Screen</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Embedded Leaflet Map Preview */}
        <div className="h-[480px] rounded-xl overflow-hidden border border-[#E3EBE5]">
          <MaharashtraMap initialLayer={activePreviewLayer} />
        </div>
      </div>

      {/* Environmental Intelligence Analytics & Distribution Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Groundwater Depth Tier Distribution */}
        <div className="bg-white rounded-2xl border border-[#E3EBE5] p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#E3EBE5]">
            <div>
              <h3 className="text-sm font-bold text-[#182C25] flex items-center gap-2">
                <Droplets className="w-4 h-4 text-[#119B72]" />
                <span>Groundwater Depth Tier Distribution</span>
              </h3>
              <p className="text-[11px] text-[#718078]">
                Empirical distribution of 3,737 monitored stations across physical depth categories (m bgl).
              </p>
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#073B32] bg-[#EDF8F1] px-2.5 py-1 rounded-md border border-[#D9F2E6]">
              Real CGWB Repository
            </span>
          </div>

          <div className="space-y-4">
            {depthTiers.map((tier, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs font-medium">
                  <span className="text-[#182C25] flex items-center gap-2">
                    <span className={`w-2.5 h-2.5 rounded-full ${tier.color}`} />
                    <strong>{tier.label}</strong>
                  </span>
                  <div className="flex items-center gap-3">
                    <span className="text-[11px] text-[#718078] hidden sm:inline">{tier.note}</span>
                    <span className="font-bold text-[#182C25]">{tier.count} ({tier.percentage}%)</span>
                  </div>
                </div>
                {/* Clean Horizontal Progress Bar */}
                <div className="w-full h-2.5 rounded-full bg-[#EDF8F1] overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${tier.color}`}
                    style={{ width: `${tier.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-3 border-t border-[#E3EBE5] flex items-center justify-between text-[11px] text-[#718078]">
            <span>Average Depth: ~7.8 m bgl</span>
            <span className="text-[#073B32] font-semibold">Seasonal swing: ~2.4 m bgl post-monsoon</span>
          </div>
        </div>

        {/* Chart 2: Regional Monitoring Network Distribution */}
        <div className="bg-white rounded-2xl border border-[#E3EBE5] p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#E3EBE5]">
            <div>
              <h3 className="text-sm font-bold text-[#182C25] flex items-center gap-2">
                <Compass className="w-4 h-4 text-[#119B72]" />
                <span>Maharashtra Regional Coverage (33 Districts)</span>
              </h3>
              <p className="text-[11px] text-[#718078]">
                Geographical coverage breakdown across 5 administrative agro-climatic divisions.
              </p>
            </div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-[#073B32] bg-[#EDF8F1] px-2.5 py-1 rounded-md border border-[#D9F2E6]">
              4,381 Nodes
            </span>
          </div>

          <div className="space-y-3.5">
            {regionalCoverage.map((r, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-[#182C25]">
                    {r.region} <span className="font-normal text-[#718078]">({r.districts} districts)</span>
                  </span>
                  <span className="font-bold text-[#182C25]">{r.wells} locations ({r.share}%)</span>
                </div>
                <div className="w-full h-2 rounded-full bg-[#EDF8F1] overflow-hidden">
                  <div
                    className="h-full rounded-full bg-[#0B4F43] transition-all duration-500"
                    style={{ width: `${r.share}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-3 border-t border-[#E3EBE5] flex items-center justify-between text-[11px] text-[#718078]">
            <span>Search Resolution: KDTree Haversine (&lt;1 ms)</span>
            <span className="text-[#119B72] font-semibold">Statewide Coordinates Indexed</span>
          </div>
        </div>
      </div>

      {/* BIS IS 10500:2012 Drinking Water Benchmark Standards Matrix */}
      <div className="bg-white rounded-2xl border border-[#E3EBE5] p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4 pb-3 border-b border-[#E3EBE5]">
          <div>
            <h3 className="text-sm font-bold text-[#182C25] flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#119B72]" />
              <span>Statutory Drinking Water Standards &bull; BIS IS 10500:2012</span>
            </h3>
            <p className="text-[11px] text-[#718078]">
              Official Bureau of Indian Standards acceptable limits applied by the XGBoost potability evaluation engine.
            </p>
          </div>
          <button
            onClick={() => onNavigate('classification')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-[#EDF8F1] text-[#073B32] hover:bg-[#D9F2E6] border border-[#D9F2E6] transition-colors self-start sm:self-auto"
          >
            <span>Run Parameter Audit</span>
            <ArrowRight className="w-3.5 h-3.5 text-[#119B72]" />
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {bisStandardsSummary.map((item, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-[#F8FAF7] border border-[#E3EBE5]">
              <p className="text-[10px] font-bold text-[#718078] uppercase truncate">{item.parameter}</p>
              <p className="text-base font-extrabold text-[#073B32] mt-1">
                {item.standard} <span className="text-[10px] font-normal text-[#718078]">{item.unit}</span>
              </p>
              <span className="inline-block mt-1 text-[9px] font-bold px-1.5 py-0.2 rounded bg-[#EDF8F1] text-[#119B72] border border-[#D9F2E6]">
                {item.compliance}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* 4 Core Architecture Intelligence Modules */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-[#182C25] flex items-center gap-2">
            <Cpu className="w-4 h-4 text-[#119B72]" />
            <span>Verified Intelligence Architecture Modules</span>
          </h2>
          <span className="text-xs text-[#718078] font-medium hidden sm:inline">
            Preserving certified models and algorithms
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Module 1: Groundwater Regression */}
          <div className="bg-white rounded-2xl border border-[#E3EBE5] p-5 shadow-xs hover:border-[#119B72]/50 hover:shadow-sm transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-bold text-[#073B32] bg-[#EDF8F1] px-2.5 py-1 rounded-full border border-[#D9F2E6]">
                  Module 1: Regression
                </span>
                <span className="text-[10px] font-bold text-[#119B72] bg-[#EDF8F1] px-2 py-0.5 rounded">
                  Test R² = 0.7766
                </span>
              </div>
              <h3 className="text-sm font-bold text-[#182C25] mb-1.5">Groundwater Level Prediction</h3>
              <p className="text-xs text-[#718078] leading-relaxed mb-4">
                Predicts future water table depth in metres below ground level using KNN Regressor (k=7) trained on rainfall accumulators.
              </p>
              <ul className="text-xs text-[#718078] space-y-1.5 mb-5 border-t border-[#E3EBE5] pt-3">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#119B72]" />
                  <span><strong>16 Features:</strong> 14 num + 2 cat</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#119B72]" />
                  <span><strong>Error:</strong> MAE 1.32m, RMSE 1.93m</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#119B72]" />
                  <span><strong>3,737</strong> unique well presets</span>
                </li>
              </ul>
            </div>
            <button
              onClick={() => onNavigate('regression')}
              className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-[#073B32] hover:bg-[#0B4F43] text-white text-xs font-semibold transition-colors"
            >
              <span>Explore Regression</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#119B72]" />
            </button>
          </div>

          {/* Module 2: Water Quality Classification */}
          <div className="bg-white rounded-2xl border border-[#E3EBE5] p-5 shadow-xs hover:border-[#119B72]/50 hover:shadow-sm transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-bold text-[#073B32] bg-[#EDF8F1] px-2.5 py-1 rounded-full border border-[#D9F2E6]">
                  Module 2: Classification
                </span>
                <span className="text-[10px] font-bold text-[#119B72] bg-[#EDF8F1] px-2 py-0.5 rounded">
                  98.8% CV Acc
                </span>
              </div>
              <h3 className="text-sm font-bold text-[#182C25] mb-1.5">Water Potability Classification</h3>
              <p className="text-xs text-[#718078] leading-relaxed mb-4">
                Assesses drinking water safety via XGBoost pipeline with median imputation and BIS IS 10500:2012 limit comparison.
              </p>
              <ul className="text-xs text-[#718078] space-y-1.5 mb-5 border-t border-[#E3EBE5] pt-3">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#119B72]" />
                  <span><strong>11 Inputs:</strong> pH, EC, TDS, etc.</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#119B72]" />
                  <span><strong>Fallback:</strong> TDS = 0.64 * EC</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#119B72]" />
                  <span><strong>Itemized</strong> limit advisory</span>
                </li>
              </ul>
            </div>
            <button
              onClick={() => onNavigate('classification')}
              className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-[#0B4F43] hover:bg-[#0E6254] text-white text-xs font-semibold transition-colors"
            >
              <span>Test Water Potability</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#119B72]" />
            </button>
          </div>

          {/* Module 3: Spatial Nearest-Well Search */}
          <div className="bg-white rounded-2xl border border-[#E3EBE5] p-5 shadow-xs hover:border-[#119B72]/50 hover:shadow-sm transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-bold text-[#073B32] bg-[#EDF8F1] px-2.5 py-1 rounded-full border border-[#D9F2E6]">
                  Module 3: Spatial KDTree
                </span>
                <span className="text-[10px] font-bold text-[#119B72] bg-[#EDF8F1] px-2 py-0.5 rounded">
                  4,381 Wells
                </span>
              </div>
              <h3 className="text-sm font-bold text-[#182C25] mb-1.5">Statewide Nearest-Well Discovery</h3>
              <p className="text-xs text-[#718078] leading-relaxed mb-4">
                Statewide spatial KDTree discovery using true spherical Haversine distances across 33 Maharashtra districts in &lt;1 ms.
              </p>
              <ul className="text-xs text-[#718078] space-y-1.5 mb-5 border-t border-[#E3EBE5] pt-3">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#119B72]" />
                  <span><strong>Fast Index:</strong> KDTree &lt;1ms query</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#119B72]" />
                  <span><strong>33 Districts</strong> filtered search</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#119B72]" />
                  <span><strong>Node Snap:</strong> Pune road graph IDs</span>
                </li>
              </ul>
            </div>
            <button
              onClick={() => onNavigate('spatial')}
              className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-[#F8FAF7] hover:bg-[#EDF8F1] text-[#073B32] border border-[#E3EBE5] text-xs font-semibold transition-colors"
            >
              <span>Search Nearest Wells</span>
              <ArrowRight className="w-3.5 h-3.5 text-[#119B72]" />
            </button>
          </div>

          {/* Module 4: Pune Road Routing */}
          <div className="bg-white rounded-2xl border border-[#E3EBE5] p-5 shadow-xs hover:border-[#119B72]/50 hover:shadow-sm transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[10px] font-bold text-[#073B32] bg-[#EDF8F1] px-2.5 py-1 rounded-full border border-[#D9F2E6]">
                  Module 4: Road Routing
                </span>
                <span className="text-[10px] font-bold text-[#119B72] bg-[#EDF8F1] px-2 py-0.5 rounded">
                  6 Search Algos
                </span>
              </div>
              <h3 className="text-sm font-bold text-[#182C25] mb-1.5">Pune Road Network Pathfinding</h3>
              <p className="text-xs text-[#718078] leading-relaxed mb-4">
                Computes optimal paths across 170,253 Pune road network nodes using A*, Bidirectional, BFS, and Greedy algorithms.
              </p>
              <ul className="text-xs text-[#718078] space-y-1.5 mb-5 border-t border-[#E3EBE5] pt-3">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#119B72]" />
                  <span><strong>Exact Hops:</strong> 409,399 directed edges</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#119B72]" />
                  <span><strong>Fast Binary:</strong> 10MB joblib cache</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#119B72]" />
                  <span><strong>Live Polyline:</strong> Leaflet geometry</span>
                </li>
              </ul>
            </div>
            <button
              onClick={() => onNavigate('routing')}
              className="w-full flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-[#119B72] hover:bg-[#0E8360] text-white text-xs font-semibold transition-colors"
            >
              <span>Plan Pune Route</span>
              <ArrowRight className="w-3.5 h-3.5 text-white" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
