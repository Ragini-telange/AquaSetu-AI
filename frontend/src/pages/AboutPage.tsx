import React from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  Globe2
} from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="border-b border-[#E3EBE5] pb-5">
        <div className="flex items-center gap-2 text-[#073B32] font-semibold text-xs tracking-wider uppercase">
          <span className="w-2 h-2 rounded-full bg-[#119B72]" />
          <span>System Architecture &bull; Technical Specifications</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-[#182C25] mt-1">
          About AquaSetu AI Environmental Platform
        </h1>
        <p className="text-[#718078] text-xs sm:text-sm mt-1">
          Integrated Environmental Decision Support Platform combining machine learning groundwater depth prediction, water potability screening, spatial GIS discovery, and directed road network pathfinding.
        </p>
      </div>

      {/* Platform Mission Card */}
      <div className="bg-[#073B32] text-white p-7 rounded-2xl border border-[#0B4F43] shadow-xs space-y-3">
        <div className="flex items-center gap-2 text-xs font-bold text-[#D9F2E6] uppercase tracking-wider">
          <Globe2 className="w-4 h-4 text-[#119B72]" />
          <span>Mission &amp; Scientific Scope</span>
        </div>
        <h2 className="text-xl sm:text-2xl font-black">
          Empirical Water Resource Intelligence for Maharashtra State
        </h2>
        <p className="text-xs sm:text-sm text-[#D9F2E6]/85 leading-relaxed max-w-3xl">
          AquaSetu AI was developed to replace fragmented water spreadsheets and opaque forecasts with a reproducible, empirical environmental intelligence engine. By anchoring models strictly to verified Central Ground Water Board (CGWB) monitoring stations and statutory Bureau of Indian Standards (BIS IS 10500:2012) regulations, the platform delivers trustworthy decisions without data fabrication.
        </p>
      </div>

      {/* 4 Certified Architectural Modules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Module 1 */}
        <div className="bg-white rounded-2xl border border-[#E3EBE5] p-6 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded bg-[#EDF8F1] text-[#073B32] border border-[#D9F2E6]">
              Module 1: Groundwater Regression
            </span>
            <span className="text-xs font-bold text-[#119B72]">R² = 0.7766</span>
          </div>
          <h3 className="text-base font-bold text-[#182C25]">Groundwater Depth Regression</h3>
          <p className="text-xs text-[#718078] leading-relaxed">
            Employs an Experiment B distance-weighted K-Nearest Neighbors (KNN, k=7) regressor trained on 16 features (sequential depth lags, antecedent rainfall accumulators for 30d, 60d, 90d, 180d, and seasonal cycles).
          </p>
          <ul className="text-xs text-[#718078] space-y-1.5 pt-2 border-t border-[#E3EBE5]">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#119B72]" />
              <span>Deterministic point estimates in metres below ground level (m bgl)</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#119B72]" />
              <span>3,737 unique monitoring well locations indexed</span>
            </li>
          </ul>
        </div>

        {/* Module 2 */}
        <div className="bg-white rounded-2xl border border-[#E3EBE5] p-6 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded bg-[#EDF8F1] text-[#073B32] border border-[#D9F2E6]">
              Module 2: Water Potability Classification
            </span>
            <span className="text-xs font-bold text-[#119B72]">98.8% CV Accuracy</span>
          </div>
          <h3 className="text-base font-bold text-[#182C25]">Water Potability Classification</h3>
          <p className="text-xs text-[#718078] leading-relaxed">
            Evaluates 11 physicochemical drinking water parameters using an XGBoost classification pipeline with Median Imputation and StandardScaler, paired with an itemized Bureau of Indian Standards (BIS IS 10500:2012) compliance rule engine.
          </p>
          <ul className="text-xs text-[#718078] space-y-1.5 pt-2 border-t border-[#E3EBE5]">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#119B72]" />
              <span>Hydrological ratio fallback for missing TDS (TDS = 0.64 &times; EC)</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#119B72]" />
              <span>Explicit statutory disclaimer separating ML probability from laboratory certification</span>
            </li>
          </ul>
        </div>

        {/* Module 3 */}
        <div className="bg-white rounded-2xl border border-[#E3EBE5] p-6 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded bg-[#EDF8F1] text-[#073B32] border border-[#D9F2E6]">
              Module 3: Spatial Nearest-Well Search
            </span>
            <span className="text-xs font-bold text-[#119B72]">&lt; 1 ms Latency</span>
          </div>
          <h3 className="text-base font-bold text-[#182C25]">Statewide Spatial Nearest-Well Search</h3>
          <p className="text-xs text-[#718078] leading-relaxed">
            Provides sub-millisecond 2D KDTree spatial search across 4,381 monitoring locations covering all 33 Maharashtra districts using true great-circle Haversine trigonometry.
          </p>
          <ul className="text-xs text-[#718078] space-y-1.5 pt-2 border-t border-[#E3EBE5]">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#119B72]" />
              <span>District-bounded candidate filtering</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#119B72]" />
              <span>Pre-computed road node snaps for emergency dispatch routing</span>
            </li>
          </ul>
        </div>

        {/* Module 4 */}
        <div className="bg-white rounded-2xl border border-[#E3EBE5] p-6 shadow-xs space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded bg-[#EDF8F1] text-[#073B32] border border-[#D9F2E6]">
              Module 4: Pune Road Network Pathfinding
            </span>
            <span className="text-xs font-bold text-[#119B72]">170,253 Nodes</span>
          </div>
          <h3 className="text-base font-bold text-[#182C25]">Pune Road Network Pathfinding</h3>
          <p className="text-xs text-[#718078] leading-relaxed">
            Performs high-performance graph searches across 170,253 road nodes and 409,399 directed OpenStreetMap road edges strictly within Pune District, supporting A*, Bidirectional, BFS, Greedy Best-First, IDDFS, and DFS.
          </p>
          <ul className="text-xs text-[#718078] space-y-1.5 pt-2 border-t border-[#E3EBE5]">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#119B72]" />
              <span>Pre-parsed 10.17 MB binary joblib cache loaded at startup</span>
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-[#119B72]" />
              <span>Returns exact route polylines, edge counts, and distance in meters/km</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Data Governance & Provenance Statement */}
      <div className="bg-white rounded-2xl border border-[#E3EBE5] p-6 shadow-xs space-y-3">
        <h3 className="text-sm font-bold text-[#182C25] uppercase tracking-wider flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-[#119B72]" />
          <span>Statutory Compliance &amp; Data Integrity Commitment</span>
        </h3>
        <p className="text-xs text-[#718078] leading-relaxed">
          In strict compliance with software engineering and scientific standards, AquaSetu AI forbids synthetic coordinate generation, dummy prediction numbers, and stock photographic imagery. All monitoring stations, depths, road segments, and chemical parameters reflect verified repositories audited in the AquaSetu AI codebase.
        </p>
      </div>
    </div>
  );
};
