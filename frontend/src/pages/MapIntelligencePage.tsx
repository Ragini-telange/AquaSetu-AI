import React from 'react';
import { Map, Layers, ShieldCheck, Info } from 'lucide-react';
import { MaharashtraMap } from '../components/MaharashtraMap';

export const MapIntelligencePage: React.FC = () => {
  return (
    <div className="space-y-6 pb-12">
      {/* Header Banner */}
      <div className="bg-white rounded-2xl border border-[#E3EBE5] p-6 shadow-xs">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[#EDF8F1] text-[#073B32] border border-[#D9F2E6]">
                <Map className="w-3.5 h-3.5 text-[#119B72]" />
                Statewide Geographic Intelligence
              </span>
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-[#EDF8F1] text-[#073B32] border border-[#D9F2E6]">
                <ShieldCheck className="w-3 h-3 text-[#119B72]" />
                4 Synchronized Modules
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#182C25] tracking-tight">
              Maharashtra Geographic Intelligence Map
            </h1>
            <p className="text-sm text-[#718078] max-w-3xl mt-1 leading-relaxed">
              Unified multi-layer GIS visualization integrating 3,737 CGWB groundwater monitoring wells,
              on-demand KNN (k=7) depth predictions, BIS IS 10500:2012 water quality classification,
              statewide KDTree spatial well discovery, and Pune OpenStreetMap road routing.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 self-start md:self-auto text-xs text-[#718078] bg-[#F8FAF7] border border-[#E3EBE5] p-2.5 rounded-xl">
            <Layers className="w-4 h-4 text-[#119B72]" />
            <span className="font-semibold text-[#182C25]">Active Layers:</span>
            <span className="px-1.5 py-0.5 rounded bg-white border border-[#E3EBE5] text-[#182C25] font-medium">Regression</span>
            <span className="px-1.5 py-0.5 rounded bg-white border border-[#E3EBE5] text-[#182C25] font-medium">Classification</span>
            <span className="px-1.5 py-0.5 rounded bg-white border border-[#E3EBE5] text-[#182C25] font-medium">Spatial</span>
            <span className="px-1.5 py-0.5 rounded bg-white border border-[#E3EBE5] text-[#182C25] font-medium">Routing</span>
          </div>
        </div>

        {/* Informative Alert for Geolocation Integrity */}
        <div className="mt-4 pt-4 border-t border-[#E3EBE5] flex items-start gap-2.5 text-xs text-[#182C25] bg-[#EDF8F1]/60 -mx-6 -mb-6 p-4 rounded-b-2xl">
          <Info className="w-4 h-4 text-[#119B72] shrink-0 mt-0.5" />
          <div>
            <strong className="text-[#073B32] font-semibold">Strict Data Integrity Notice:</strong> Wells and stations are displayed exclusively at their verified Central Ground Water Board (CGWB) coordinates. Predictions are generated on-demand without fabricating unobserved records, and laboratory potability benchmarks strictly adhere to BIS IS 10500:2012 guidelines.
          </div>
        </div>
      </div>

      {/* Primary Interactive Multi-Layer Map */}
      <MaharashtraMap />

      {/* Layer Architecture & Documentation Guide */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl border border-[#E3EBE5] p-4 shadow-xs">
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#119B72]" />
            <h3 className="text-sm font-bold text-[#182C25]">1. Groundwater Depth</h3>
          </div>
          <p className="text-xs text-[#718078] leading-relaxed">
            Click any monitoring well to view historical depth trends and trigger instantaneous KNN (k=7) depth predictions with antecedent rainfall accumulators.
          </p>
        </div>

        <div className="bg-white rounded-xl border border-[#E3EBE5] p-4 shadow-xs">
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#0B4F43]" />
            <h3 className="text-sm font-bold text-[#182C25]">2. Water Quality</h3>
          </div>
          <p className="text-xs text-[#718078] leading-relaxed">
            Displays verified monitoring stations. Inspect laboratory physicochemical parameters evaluated via XGBoost (98.8% CV) and statutory BIS limits.
          </p>
        </div>

        <div className="bg-white rounded-xl border border-[#E3EBE5] p-4 shadow-xs">
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#073B32]" />
            <h3 className="text-sm font-bold text-[#182C25]">3. Spatial KDTree</h3>
          </div>
          <p className="text-xs text-[#718078] leading-relaxed">
            Click anywhere in Maharashtra to drop a target pin and query the nearest monitoring wells using optimized statewide Haversine search in &lt;1 ms.
          </p>
        </div>

        <div className="bg-white rounded-xl border border-[#E3EBE5] p-4 shadow-xs">
          <div className="flex items-center gap-2 mb-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#119B72]" />
            <h3 className="text-sm font-bold text-[#182C25]">4. Pune OSM Routing</h3>
          </div>
          <p className="text-xs text-[#718078] leading-relaxed">
            Switch to Pune district road network to run A*, Bidirectional, BFS, and Greedy graph searches over 170,253 nodes and 409,399 directed edges.
          </p>
        </div>
      </div>
    </div>
  );
};
