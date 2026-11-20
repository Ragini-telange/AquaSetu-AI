import React from 'react';
import { Droplets, Activity, MapPin, Navigation, ArrowRight, ShieldCheck, Database, Compass, Cpu } from 'lucide-react';
import type { TabKey } from '../components/Navbar';

interface DashboardProps {
  onNavigate: (tab: TabKey) => void;
}

export const DashboardOverview: React.FC<DashboardProps> = ({ onNavigate }) => {
  return (
    <div className="space-y-8 pb-12">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-slate-900 via-cyan-950 to-slate-900 border border-cyan-800/40 p-8 sm:p-10 text-white shadow-xl">
        <div className="absolute -right-10 -bottom-10 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-semibold mb-4">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            AI-Driven Water Resource Management
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white mb-3">
            AquaGuard AI Decision Support Platform
          </h1>
          <p className="text-slate-300 text-sm sm:text-base leading-relaxed mb-6">
            An integrated intelligence system combining machine learning groundwater table depth prediction,
            physicochemical drinking water potability classification, statewide spatial well discovery,
            and directed road network emergency pathfinding.
          </p>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => onNavigate('regression')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-semibold text-sm transition-all shadow-md shadow-cyan-500/20"
            >
              <Droplets className="w-4 h-4" />
              <span>Predict Groundwater Level</span>
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={() => onNavigate('classification')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-200 border border-cyan-700/50 font-medium text-sm transition-all"
            >
              <Activity className="w-4 h-4" />
              <span>Evaluate Water Potability</span>
            </button>
          </div>
        </div>
      </div>

      {/* System Statistics Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 rounded-lg bg-cyan-50 text-cyan-600">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Monitored Wells</p>
            <p className="text-2xl font-bold text-slate-900">3,737</p>
            <p className="text-[11px] text-slate-400">CGWB Maharashtra network</p>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 rounded-lg bg-teal-50 text-teal-600">
            <Droplets className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Historical Records</p>
            <p className="text-2xl font-bold text-slate-900">65,738</p>
            <p className="text-[11px] text-slate-400">2021 – 2025 observations</p>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 rounded-lg bg-blue-50 text-blue-600">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Standards Basis</p>
            <p className="text-2xl font-bold text-slate-900">IS 10500</p>
            <p className="text-[11px] text-slate-400">11 BIS chemical parameters</p>
          </div>
        </div>

        <div className="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 rounded-lg bg-indigo-50 text-indigo-600">
            <Compass className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Road Graph Nodes</p>
            <p className="text-2xl font-bold text-slate-900">170,253</p>
            <p className="text-[11px] text-slate-400">409,399 directed OSM edges</p>
          </div>
        </div>
      </div>

      {/* 3 Core Architecture Modules */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 mb-4 flex items-center gap-2">
          <Cpu className="w-5 h-5 text-cyan-600" />
          <span>Verified Architecture Modules</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Module 1: Ragini Regression */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-cyan-700 bg-cyan-50 px-2.5 py-1 rounded-full border border-cyan-200">
                  Module 1: Ragini
                </span>
                <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">
                  Test R² = 0.7766
                </span>
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Groundwater Level Prediction</h3>
              <p className="text-sm text-slate-600 mb-4">
                Predicts future water table depth (meters below ground level) using Experiment B KNN Regressor (k=7)
                trained on sequential lags and antecedent rainfall accumulators.
              </p>
              <ul className="text-xs text-slate-500 space-y-1.5 mb-6">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-500" />
                  <strong>16 Features:</strong> 14 numerical + 2 categorical
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-500" />
                  <strong>Verified Error:</strong> Holdout MAE 1.32 m, RMSE 1.93 m
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-500" />
                  <strong>Modes:</strong> Historical lookup & custom scenario
                </li>
              </ul>
            </div>
            <button
              onClick={() => onNavigate('regression')}
              className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium transition-colors"
            >
              <span>Explore Regression Model</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Module 2: Sakshi Classification */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-teal-700 bg-teal-50 px-2.5 py-1 rounded-full border border-teal-200">
                  Module 2: Sakshi
                </span>
                <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded">
                  98.8% CV Acc
                </span>
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Water Quality Potability</h3>
              <p className="text-sm text-slate-600 mb-4">
                Evaluates drinking water safety against the official BIS IS 10500:2012 specification using an XGBoost
                pipeline with median imputation and standard scaling.
              </p>
              <ul className="text-xs text-slate-500 space-y-1.5 mb-6">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-teal-500" />
                  <strong>Exact 11 Inputs:</strong> pH, EC, TDS, Hardness, Ca, Mg, etc.
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-teal-500" />
                  <strong>Hydrological Fallback:</strong> Automatic TDS = 0.64 * EC
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-teal-500" />
                  <strong>Statutory Advisory:</strong> Itemized BIS limit exceedances
                </li>
              </ul>
            </div>
            <button
              onClick={() => onNavigate('classification')}
              className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg bg-teal-600 hover:bg-teal-500 text-white text-sm font-medium transition-colors"
            >
              <span>Test Water Potability</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Module 3: Vedangi Geographical & Routing */}
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs font-bold text-indigo-700 bg-indigo-50 px-2.5 py-1 rounded-full border border-indigo-200">
                  Module 3: Vedangi
                </span>
                <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2 py-0.5 rounded">
                  6 Algorithms
                </span>
              </div>
              <h3 className="text-lg font-bold text-slate-900 mb-2">Spatial Search & Pune Routing</h3>
              <p className="text-sm text-slate-600 mb-4">
                Provides two distinct geographical capabilities: 33-district statewide nearest-well KDTree discovery,
                and directed Pune OSM road network pathfinding.
              </p>
              <ul className="text-xs text-slate-500 space-y-1.5 mb-6">
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                  <strong>Statewide Search:</strong> 4,381 well locations in &lt;1 ms
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                  <strong>Pune Routing:</strong> A*, Bidirectional, BFS, GBFS, IDDFS, DFS
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
                  <strong>Fast Binary Cache:</strong> 10 MB joblib cache loaded in 7s
                </li>
              </ul>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <button
                onClick={() => onNavigate('spatial')}
                className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-medium transition-colors"
              >
                <MapPin className="w-3.5 h-3.5" />
                <span>Find Wells</span>
              </button>
              <button
                onClick={() => onNavigate('routing')}
                className="flex items-center justify-center gap-1.5 py-2 px-3 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium transition-colors"
              >
                <Navigation className="w-3.5 h-3.5" />
                <span>Pune Route</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
