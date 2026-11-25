import React, { useState } from 'react';
import {
  Droplets,
  Calendar,
  Gauge,
  AlertCircle,
  CheckCircle2,
  Sliders,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { predictWaterLevel } from '../services/api';
import type { WaterLevelPredictionResponse, WaterLevelPredictionRequest } from '../services/api';

// Helper: Depth range classification & color mapping
const getDepthClassification = (depth: number) => {
  if (depth < 5) {
    return {
      label: 'Shallow Zone (0–5 m)',
      category: 'Shallow',
      color: '#119B72',
      badgeClass: 'bg-[#EDF8F1] text-[#073B32] border-[#D9F2E6]',
    };
  } else if (depth < 10) {
    return {
      label: 'Moderate Zone (5–10 m)',
      category: 'Moderate',
      color: '#0B4F43',
      badgeClass: 'bg-[#0B4F43]/15 text-[#073B32] border-[#0B4F43]/30',
    };
  } else if (depth < 15) {
    return {
      label: 'Deep Zone (10–15 m)',
      category: 'Deep',
      color: '#E9A23B',
      badgeClass: 'bg-[#FFF8ED] text-[#975A16] border-[#FEEBC8]',
    };
  } else {
    return {
      label: 'Very Deep Zone (Above 15 m)',
      category: 'Very Deep',
      color: '#E45B55',
      badgeClass: 'bg-[#FDF2F2] text-[#E45B55] border-[#FAD2D2]',
    };
  }
};

// Helper: Calculate scale marker position percentage across the 4 continuous ranges
const getMarkerPositionPercent = (depth: number): number => {
  if (depth <= 0) return 2;
  if (depth <= 5) {
    // 0 - 5 m maps to 0% - 25% (Green)
    return Math.max(2, (depth / 5) * 25);
  } else if (depth <= 10) {
    // 5 - 10 m maps to 25% - 50% (Dark Green)
    return 25 + ((depth - 5) / 5) * 25;
  } else if (depth <= 15) {
    // 10 - 15 m maps to 50% - 75% (Yellow)
    return 50 + ((depth - 10) / 5) * 25;
  } else {
    // Above 15 m maps to 75% - 100% (Red)
    // Scale calibrated with 15 - 25 m span, clamped to 98%
    const excess = Math.min(depth - 15, 10);
    return Math.min(98, 75 + (excess / 10) * 25);
  }
};

export const RegressionPage: React.FC = () => {
  const [mode, setMode] = useState<'historical_lookup' | 'custom_scenario'>('historical_lookup');

  // Mode A state (Verified Well Presets)
  const [wellId, setWellId] = useState<string>('W153803073591301');
  const [predictionDate, setPredictionDate] = useState<string>('2024-05-29');

  // Mode B state
  const [district, setDistrict] = useState<string>('Pune');
  const [season, setSeason] = useState<string>('Post-Monsoon');
  const [wellDepth, setWellDepth] = useState<number>(15.0);
  const [lag1, setLag1] = useState<number>(3.5);
  const [lag2, setLag2] = useState<number>(4.2);
  const [lag4, setLag4] = useState<number>(3.8);
  const [rain30d, setRain30d] = useState<number>(150.0);
  const [rain60d, setRain60d] = useState<number>(320.0);
  const [rain90d, setRain90d] = useState<number>(450.0);
  const [rain180d, setRain180d] = useState<number>(500.0);

  // Status & Output
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<WaterLevelPredictionResponse | null>(null);
  const [showFeatures, setShowFeatures] = useState<boolean>(false);

  // Sample well presets verified in Experiment B repository
  const sampleWells = [
    { id: 'W153803073591301', name: 'Matne (Sindhudurg)', date: '2024-05-29', district: 'Sindhudurg' },
    { id: 'W182646073521001', name: 'Katraj, Pune (Haveli)', date: '2024-05-28', district: 'Pune' },
    { id: 'W204427078364501', name: 'Wardha Sub-district', date: '2024-06-01', district: 'Wardha' },
    { id: 'W174810075540001', name: 'Mardi, Solapur (Dug Well)', date: '2024-06-06', district: 'Solapur' }
  ];

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      let payload: WaterLevelPredictionRequest;
      if (mode === 'historical_lookup') {
        payload = {
          mode: 'historical_lookup',
          well_id: wellId.trim(),
          prediction_date: predictionDate.trim() || undefined,
        };
      } else {
        payload = {
          mode: 'custom_scenario',
          district_name: district,
          season: season,
          well_depth_m: wellDepth,
          lag_1: lag1,
          lag_2: lag2,
          lag_4: lag4,
          rain_prior_30d: rain30d,
          rain_prior_60d: rain60d,
          rain_prior_90d: rain90d,
          rain_prior_180d: rain180d,
        };
      }

      const res = await predictWaterLevel(payload);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to predict groundwater level.');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Page Scientific Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#E3EBE5] pb-5">
        <div>
          <div className="flex items-center gap-2 text-[#073B32] font-semibold text-xs tracking-wider uppercase">
            <span className="w-2 h-2 rounded-full bg-[#119B72]" />
            <span>Predictive Analytics &bull; Scientific Groundwater Regression</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#182C25] mt-1">
            Groundwater Depth Prediction Analytics
          </h1>
          <p className="text-[#718078] text-xs sm:text-sm mt-1">
            Predicts future phreatic water table depth in metres below ground level (m bgl) via verified distance-weighted KNN Regressor (k=7).
          </p>
        </div>

        {/* Mode Selector Tabs */}
        <div className="flex bg-[#EDF8F1] p-1 rounded-xl self-start sm:self-auto border border-[#D9F2E6]">
          <button
            onClick={() => setMode('historical_lookup')}
            className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all ${mode === 'historical_lookup'
              ? 'bg-white text-[#073B32] shadow-xs'
              : 'text-[#718078] hover:text-[#182C25]'
              }`}
          >
            Historical Well Lookup
          </button>
          <button
            onClick={() => setMode('custom_scenario')}
            className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all ${mode === 'custom_scenario'
              ? 'bg-white text-[#073B32] shadow-xs'
              : 'text-[#718078] hover:text-[#182C25]'
              }`}
          >
            Custom Hydrological Scenario
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Form Controls Column */}
        <div className="lg:col-span-5 space-y-5">
          <div className="bg-white rounded-2xl border border-[#E3EBE5] p-5 shadow-xs">
            <form onSubmit={handlePredict} className="space-y-4">
              {mode === 'historical_lookup' ? (
                <>
                  <div>
                    <label className="block text-xs font-bold text-[#182C25] mb-1">
                      CGWB Monitoring Well Identifier
                    </label>
                    <input
                      type="text"
                      value={wellId}
                      onChange={(e) => setWellId(e.target.value)}
                      placeholder="e.g. W153803073591301"
                      required
                      className="w-full px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-mono text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none transition-colors"
                    />
                    <p className="text-[11px] text-[#718078] mt-1">
                      Lookup across 3,737 precomputed CGWB monitoring stations in Maharashtra.
                    </p>
                  </div>

                  {/* Sample Presets */}
                  <div>
                    <p className="text-xs font-semibold text-[#718078] mb-1.5">Verified Sample Stations:</p>
                    <div className="grid grid-cols-2 gap-2">
                      {sampleWells.map((s) => (
                        <button
                          key={s.id}
                          type="button"
                          onClick={() => {
                            setWellId(s.id);
                            setPredictionDate(s.date);
                          }}
                          className={`text-left p-2.5 rounded-xl border transition-all text-xs ${wellId === s.id
                            ? 'bg-[#EDF8F1] border-[#119B72] text-[#073B32] font-semibold'
                            : 'bg-white border-[#E3EBE5] text-[#182C25] hover:border-[#CDDAD1]'
                            }`}
                        >
                          <p className="font-semibold truncate">{s.name}</p>
                          <p className="text-[10px] font-mono text-[#718078] truncate">{s.id}</p>
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#182C25] mb-1">
                      Target Monitoring Date (YYYY-MM-DD)
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        value={predictionDate}
                        onChange={(e) => setPredictionDate(e.target.value)}
                        placeholder="e.g. 2024-05-29 (or leave empty for latest)"
                        className="w-full pl-9 pr-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none transition-colors"
                      />
                      <Calendar className="w-4 h-4 text-[#718078] absolute left-3 top-2.5 pointer-events-none" />
                    </div>
                    <p className="text-[11px] text-[#718078] mt-1">
                      Repository observations span 2021-02-15 through 2025-06-18.
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-[#182C25] mb-1">District Name</label>
                      <select
                        value={district}
                        onChange={(e) => setDistrict(e.target.value)}
                        className="w-full px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                      >
                        {['Pune', 'Wardha', 'Nagpur', 'Solapur', 'Nashik', 'Amravati', 'Aurangabad', 'Kolhapur', 'Thane'].map((d) => (
                          <option key={d} value={d}>{d}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-[#182C25] mb-1">Season</label>
                      <select
                        value={season}
                        onChange={(e) => setSeason(e.target.value)}
                        className="w-full px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                      >
                        {['Pre-Monsoon', 'Monsoon', 'Post-Monsoon', 'Winter'].map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-[#182C25] mb-1">Well Borehole Depth (m)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={wellDepth}
                      onChange={(e) => setWellDepth(parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs text-[#182C25]"
                    />
                  </div>

                  <div className="pt-2 border-t border-[#E3EBE5]">
                    <p className="text-xs font-bold text-[#182C25] mb-2">Historical Water Level Lags (m bgl)</p>
                    <div className="grid grid-cols-3 gap-2">
                      <div>
                        <label className="text-[10px] text-[#718078]">Lag 1 (Prev)</label>
                        <input
                          type="number"
                          step="0.1"
                          value={lag1}
                          onChange={(e) => setLag1(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1.5 text-xs border border-[#E3EBE5] bg-[#F8FAF7] rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-[#718078]">Lag 2</label>
                        <input
                          type="number"
                          step="0.1"
                          value={lag2}
                          onChange={(e) => setLag2(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1.5 text-xs border border-[#E3EBE5] bg-[#F8FAF7] rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-[#718078]">Lag 4 (~1 yr)</label>
                        <input
                          type="number"
                          step="0.1"
                          value={lag4}
                          onChange={(e) => setLag4(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1.5 text-xs border border-[#E3EBE5] bg-[#F8FAF7] rounded-lg"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-[#E3EBE5]">
                    <p className="text-xs font-bold text-[#182C25] mb-2">Antecedent Rainfall Accumulators (mm)</p>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="text-[10px] text-[#718078]">Prior 30d (mm)</label>
                        <input
                          type="number"
                          step="1"
                          value={rain30d}
                          onChange={(e) => setRain30d(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1.5 text-xs border border-[#E3EBE5] bg-[#F8FAF7] rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-[#718078]">Prior 60d (mm)</label>
                        <input
                          type="number"
                          step="1"
                          value={rain60d}
                          onChange={(e) => setRain60d(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1.5 text-xs border border-[#E3EBE5] bg-[#F8FAF7] rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-[#718078]">Prior 90d (mm)</label>
                        <input
                          type="number"
                          step="1"
                          value={rain90d}
                          onChange={(e) => setRain90d(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1.5 text-xs border border-[#E3EBE5] bg-[#F8FAF7] rounded-lg"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-[#718078]">Prior 180d (mm)</label>
                        <input
                          type="number"
                          step="1"
                          value={rain180d}
                          onChange={(e) => setRain180d(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1.5 text-xs border border-[#E3EBE5] bg-[#F8FAF7] rounded-lg"
                        />
                      </div>
                    </div>
                  </div>
                </>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-2.5 px-4 rounded-xl bg-[#119B72] hover:bg-[#0E8360] text-white font-semibold text-xs sm:text-sm transition-all shadow-md shadow-[#119B72]/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Executing KNN (k=7) Regressor...</span>
                  </>
                ) : (
                  <>
                    <Gauge className="w-4 h-4" />
                    <span>Run Groundwater Depth Prediction</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Model Specification Card */}
          <div className="bg-[#EDF8F1] rounded-2xl p-4 border border-[#D9F2E6] text-xs text-[#073B32] space-y-1.5">
            <p className="font-bold flex items-center gap-1.5 text-[#073B32]">
              <CheckCircle2 className="w-4 h-4 text-[#119B72]" />
              <span>Experiment B Model Verification</span>
            </p>
            <p><strong>Algorithm:</strong> KNN Regressor (k=7, distance-weighted metric)</p>
            <p><strong>Holdout Test Metrics:</strong> R² = 0.7766 | RMSE = 1.93 m | MAE = 1.32 m</p>
            <p><strong>TimeSeries CV (5-Fold):</strong> Mean RMSE = 1.9066 m (&plusmn; 0.8294)</p>
            <p className="text-[11px] text-[#718078] pt-1">
              * Note: KNN outputs empirical deterministic point estimates; artificial parametric intervals are omitted.
            </p>
          </div>
        </div>

        {/* Prediction Results Column */}
        <div className="lg:col-span-7 space-y-6">
          {error && (
            <div className="p-4 rounded-2xl bg-[#FDF2F2] border border-[#FAD2D2] text-[#E45B55] flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-[#E45B55] mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-bold">Prediction Error</p>
                <p className="text-xs mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {result ? (
            <div className="bg-white rounded-2xl border border-[#E3EBE5] shadow-xs overflow-hidden">
              {/* Header in Forest Green */}
              <div className="bg-[#073B32] p-6 text-white border-b border-[#0B4F43]">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-[#119B72]/30 text-[#D9F2E6] border border-[#119B72]/40">
                    {result.model_used}
                  </span>
                  {result.prediction_date && (
                    <span className="text-xs text-[#D9F2E6]/75">
                      Target Date: {result.prediction_date}
                    </span>
                  )}
                </div>

                <div className="mt-4 flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-4">
                  <div>
                    <p className="text-xs text-[#D9F2E6]/70 uppercase tracking-wider font-medium">
                      Predicted Water Table Depth
                    </p>
                    <div className="flex items-baseline gap-2 mt-1">
                      <span className="text-4xl sm:text-5xl font-black text-white">
                        {result.predicted_water_level_m_bgl.toFixed(2)}
                      </span>
                      <span className="text-lg text-[#D9F2E6] font-medium">m bgl</span>
                    </div>
                    <p className="text-xs text-[#D9F2E6]/70 mt-1">
                      Metres below ground level to saturated zone
                    </p>
                  </div>

                  {result.effective_water_column_m !== null && result.effective_water_column_m !== undefined && (
                    <div className="bg-[#0B4F43] p-3 rounded-xl border border-[#119B72]/30 text-right sm:self-end">
                      <p className="text-[10px] text-[#D9F2E6]/70 uppercase tracking-wider">
                        Available Water Column
                      </p>
                      <p className="text-xl font-bold text-[#119B72]">
                        {result.effective_water_column_m.toFixed(2)} m
                      </p>
                      <p className="text-[10px] text-[#D9F2E6]/70">
                        Total Borehole: {result.well_depth_m} m
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Station Context & Model Evaluation Metrics */}
              <div className="p-6 space-y-6">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  <div className="p-3 rounded-xl bg-[#F8FAF7] border border-[#E3EBE5]">
                    <span className="text-[10px] uppercase font-bold text-[#718078]">Operational Mode</span>
                    <p className="text-sm font-bold text-[#182C25] mt-0.5 capitalize">
                      {result.mode.replace('_', ' ')}
                    </p>
                    <p className="text-[11px] text-[#718078] font-mono">{result.well_id || district}</p>
                  </div>

                  <div className="p-3 rounded-xl bg-[#F8FAF7] border border-[#E3EBE5]">
                    <span className="text-[10px] uppercase font-bold text-[#718078]">Holdout Test R²</span>
                    <p className="text-sm font-bold text-[#119B72] mt-0.5">
                      {result.evaluation_context.test_r2}
                    </p>
                    <p className="text-[11px] text-[#718078]">KNN Distance Weight</p>
                  </div>

                  <div className="p-3 rounded-xl bg-[#F8FAF7] border border-[#E3EBE5]">
                    <span className="text-[10px] uppercase font-bold text-[#718078]">Holdout RMSE</span>
                    <p className="text-sm font-bold text-[#182C25] mt-0.5">
                      {result.evaluation_context.test_rmse_m} m
                    </p>
                    <p className="text-[11px] text-[#718078]">Root Mean Sq Error</p>
                  </div>

                  <div className="p-3 rounded-xl bg-[#F8FAF7] border border-[#E3EBE5]">
                    <span className="text-[10px] uppercase font-bold text-[#718078]">Holdout MAE</span>
                    <p className="text-sm font-bold text-[#182C25] mt-0.5">
                      {result.evaluation_context.test_mae_m} m
                    </p>
                    <p className="text-[11px] text-[#718078]">Mean Absolute Error</p>
                  </div>
                </div>

                {/* Ground Truth Validation Box */}
                {result.historical_actual_m_bgl !== null && result.historical_actual_m_bgl !== undefined && (
                  <div className="p-4 rounded-xl bg-[#EDF8F1] border border-[#D9F2E6] flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <p className="text-xs font-bold text-[#073B32]">
                        Observed Ground Truth Benchmark Available
                      </p>
                      <p className="text-[11px] text-[#718078] mt-0.5">
                        Actual monitored depth recorded on this date: <strong>{result.historical_actual_m_bgl.toFixed(2)} m bgl</strong>
                      </p>
                    </div>

                    <div className="flex items-center gap-3 self-end sm:self-auto">
                      <div className="text-right">
                        <span className="text-[10px] text-[#718078] uppercase">Absolute Error</span>
                        <p className="text-sm font-bold text-[#073B32]">
                          {result.absolute_error_m !== null && result.absolute_error_m !== undefined
                            ? `${result.absolute_error_m.toFixed(2)} m`
                            : 'N/A'}
                        </p>
                      </div>
                      <span className="px-2.5 py-1 rounded-full bg-[#119B72] text-white text-xs font-bold">
                        Verified
                      </span>
                    </div>
                  </div>
                )}

                {/* Groundwater Depth Category & Gauge Indicator */}
                <div className="p-4 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-[#182C25] uppercase tracking-wider flex items-center gap-1.5">
                      <Droplets className="w-4 h-4 text-[#119B72]" />
                      <span>Predicted Groundwater Table Classification</span>
                    </h3>
                    <span className={`text-xs font-bold px-2.5 py-0.5 rounded-full border transition-colors ${getDepthClassification(result.predicted_water_level_m_bgl).badgeClass}`}>
                      {getDepthClassification(result.predicted_water_level_m_bgl).label}
                    </span>
                  </div>

                  {/* Visual Saturated Depth Scale with Dynamic Indicator */}
                  <div className="pt-7 pb-1">
                    <div className="relative">
                      {/* Floating Marker Tooltip with Pin */}
                      <div
                        className="absolute -top-7 -translate-x-1/2 flex flex-col items-center transition-all duration-500 ease-out z-20 pointer-events-none"
                        style={{ left: `${getMarkerPositionPercent(result.predicted_water_level_m_bgl)}%` }}
                      >
                        <div
                          className="px-2 py-0.5 rounded-md text-[10px] font-bold font-mono shadow-md text-white whitespace-nowrap flex items-center gap-1"
                          style={{ backgroundColor: getDepthClassification(result.predicted_water_level_m_bgl).color }}
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                          <span>{result.predicted_water_level_m_bgl.toFixed(2)} m bgl</span>
                        </div>
                        <div
                          className="w-0 h-0 border-x-4 border-x-transparent border-t-[5px]"
                          style={{ borderTopColor: getDepthClassification(result.predicted_water_level_m_bgl).color }}
                        />
                      </div>

                      {/* Continuous 4-Segment Scale Bar */}
                      <div className="relative w-full h-3.5 rounded-full bg-[#E3EBE5] overflow-hidden flex shadow-inner">
                        <div className="bg-[#119B72] h-full" style={{ width: '25%' }} title="0–5 m: Green (Shallow)" />
                        <div className="bg-[#0B4F43] h-full" style={{ width: '25%' }} title="5–10 m: Dark Green (Moderate)" />
                        <div className="bg-[#E9A23B] h-full" style={{ width: '25%' }} title="10–15 m: Yellow (Deep)" />
                        <div className="bg-[#E45B55] h-full" style={{ width: '25%' }} title="Above 15 m: Red (Very Deep)" />
                      </div>

                      {/* Visual Marker Needle on the Bar */}
                      <div
                        className="absolute -top-[2px] h-[18px] w-1 bg-white border border-[#182C25] rounded-full -translate-x-1/2 transition-all duration-500 ease-out z-10 pointer-events-none shadow"
                        style={{ left: `${getMarkerPositionPercent(result.predicted_water_level_m_bgl)}%` }}
                      />
                    </div>

                    {/* Scale Boundaries and Range Ticks */}
                    <div className="flex justify-between text-[10px] text-[#718078] font-mono px-0.5 pt-2">
                      <span>0 m (Surface)</span>
                      <span>5 m</span>
                      <span>10 m</span>
                      <span>15 m</span>
                      <span>25+ m (Deep)</span>
                    </div>

                    {/* Depth Range & Color Legend Indicators */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2.5 border-t border-[#E3EBE5] mt-2.5">
                      <div className={`flex items-center gap-1.5 px-2 py-1 rounded-lg text-[11px] transition-colors ${
                        result.predicted_water_level_m_bgl < 5 ? 'bg-[#EDF8F1] font-bold text-[#073B32]' : 'text-[#718078]'
                      }`}>
                        <span className="w-2.5 h-2.5 rounded-full bg-[#119B72] shrink-0" />
                        <span>0–5 m: Green</span>
                      </div>
                      <div className={`flex items-center gap-1.5 px-2 py-1 rounded-lg text-[11px] transition-colors ${
                        result.predicted_water_level_m_bgl >= 5 && result.predicted_water_level_m_bgl < 10 ? 'bg-[#EDF8F1] font-bold text-[#073B32]' : 'text-[#718078]'
                      }`}>
                        <span className="w-2.5 h-2.5 rounded-full bg-[#0B4F43] shrink-0" />
                        <span>5–10 m: Dark Green</span>
                      </div>
                      <div className={`flex items-center gap-1.5 px-2 py-1 rounded-lg text-[11px] transition-colors ${
                        result.predicted_water_level_m_bgl >= 10 && result.predicted_water_level_m_bgl < 15 ? 'bg-[#FFF8ED] font-bold text-[#975A16]' : 'text-[#718078]'
                      }`}>
                        <span className="w-2.5 h-2.5 rounded-full bg-[#E9A23B] shrink-0" />
                        <span>10–15 m: Yellow</span>
                      </div>
                      <div className={`flex items-center gap-1.5 px-2 py-1 rounded-lg text-[11px] transition-colors ${
                        result.predicted_water_level_m_bgl >= 15 ? 'bg-[#FDF2F2] font-bold text-[#E45B55]' : 'text-[#718078]'
                      }`}>
                        <span className="w-2.5 h-2.5 rounded-full bg-[#E45B55] shrink-0" />
                        <span>Above 15 m: Red</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Collapsible Feature Inputs Inspector */}
                <div className="border border-[#E3EBE5] rounded-xl overflow-hidden">
                  <button
                    onClick={() => setShowFeatures(!showFeatures)}
                    className="w-full px-4 py-3 bg-[#F8FAF7] hover:bg-[#EDF8F1] flex items-center justify-between text-xs font-bold text-[#182C25] transition-colors"
                  >
                    <span className="flex items-center gap-2">
                      <Sliders className="w-4 h-4 text-[#119B72]" />
                      <span>Full 16-Dimensional Model Input Features Vector</span>
                    </span>
                    {showFeatures ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </button>

                  {showFeatures && (
                    <div className="p-4 bg-white grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                      {Object.entries(result.features_used).map(([k, v]) => (
                        <div key={k} className="p-2 rounded-lg bg-[#F8FAF7] border border-[#E3EBE5]">
                          <span className="text-[10px] text-[#718078] block truncate">{k}</span>
                          <span className="font-bold text-[#182C25] font-mono mt-0.5 block">
                            {typeof v === 'number' ? v.toFixed(2) : String(v)}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-2xl border border-[#E3EBE5] p-12 text-center text-[#718078] space-y-3">
              <Droplets className="w-12 h-12 text-[#CDDAD1] mx-auto" />
              <h3 className="text-base font-bold text-[#182C25]">Awaiting Prediction Request</h3>
              <p className="text-xs text-[#718078] max-w-md mx-auto leading-relaxed">
                Select a verified well identifier preset or enter custom hydrological conditions on the left to trigger the distance-weighted KNN (k=7) prediction pipeline.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
