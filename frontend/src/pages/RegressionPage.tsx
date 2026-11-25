import React, { useState } from 'react';
import { Droplets, Calendar, Gauge, AlertCircle, CheckCircle2, Sliders, ChevronDown, ChevronUp } from 'lucide-react';
import { predictWaterLevel } from '../services/api';
import type { WaterLevelPredictionResponse, WaterLevelPredictionRequest } from '../services/api';

export const RegressionPage: React.FC = () => {
  const [mode, setMode] = useState<'historical_lookup' | 'custom_scenario'>('historical_lookup');
  
  // Mode A state
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

  // Sample well presets
  const sampleWells = [
    { id: 'W153803073591301', name: 'Matne (Sindhudurg)', date: '2024-05-29' },
    { id: 'W182646073521001', name: 'Katraj, Pune (Haveli)', date: '2024-05-28' },
    { id: 'W204427078364501', name: 'Wardha Sub-district', date: '2024-06-01' },
    { id: 'W174810075540001', name: 'Mardi, Solapur (Dug Well)', date: '2024-06-06' }
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
    <div className="space-y-6 max-w-6xl mx-auto pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2 text-cyan-600 font-semibold text-xs tracking-wider uppercase">
            <Droplets className="w-4 h-4" />
            <span>Ragini &bull; Regression Module</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-1">
            Groundwater Level Prediction
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Predict depth to water table in meters below ground level (m bgl) via verified KNN Regressor (k=7).
          </p>
        </div>

        {/* Mode Selector Tabs */}
        <div className="flex bg-slate-100 p-1 rounded-xl self-start sm:self-auto border border-slate-200">
          <button
            onClick={() => setMode('historical_lookup')}
            className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              mode === 'historical_lookup'
                ? 'bg-white text-cyan-700 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Historical Well Lookup
          </button>
          <button
            onClick={() => setMode('custom_scenario')}
            className={`px-3.5 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              mode === 'custom_scenario'
                ? 'bg-white text-cyan-700 shadow-sm'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            Custom Scenario
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Form Controls Column */}
        <div className="lg:col-span-5 space-y-5">
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <form onSubmit={handlePredict} className="space-y-4">
              {mode === 'historical_lookup' ? (
                <>
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      CGWB Well Identifier
                    </label>
                    <input
                      type="text"
                      value={wellId}
                      onChange={(e) => setWellId(e.target.value)}
                      placeholder="e.g. W153803073591301"
                      required
                      className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm font-mono focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 outline-none"
                    />
                    <p className="text-[11px] text-slate-400 mt-1">
                      Over 3,737 precomputed CGWB monitoring wells across Maharashtra.
                    </p>
                  </div>

                  {/* Sample Presets */}
                  <div>
                    <p className="text-xs font-semibold text-slate-500 mb-1.5">Preset Sample Wells:</p>
                    <div className="flex flex-wrap gap-1.5">
                      {sampleWells.map((s) => (
                        <button
                          key={s.id}
                          type="button"
                          onClick={() => {
                            setWellId(s.id);
                            setPredictionDate(s.date);
                          }}
                          className={`text-xs px-2.5 py-1 rounded-md border text-left transition-colors ${
                            wellId === s.id
                              ? 'bg-cyan-50 border-cyan-400 text-cyan-800 font-medium'
                              : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                          }`}
                        >
                          {s.name}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Target Monitoring Date (YYYY-MM-DD)
                    </label>
                    <div className="relative">
                      <input
                        type="text"
                        value={predictionDate}
                        onChange={(e) => setPredictionDate(e.target.value)}
                        placeholder="e.g. 2024-05-29 (or leave empty for latest)"
                        className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500 outline-none"
                      />
                      <Calendar className="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1">
                      Historical coverage spans 2021-02-15 to 2025-06-18.
                    </p>
                  </div>
                </>
              ) : (
                <>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">District Name</label>
                      <select
                        value={district}
                        onChange={(e) => setDistrict(e.target.value)}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-cyan-500 outline-none"
                      >
                        {['Pune', 'Wardha', 'Nagpur', 'Solapur', 'Nashik', 'Amravati', 'Aurangabad', 'Kolhapur', 'Thane'].map((d) => (
                          <option key={d} value={d}>{d}</option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">Season</label>
                      <select
                        value={season}
                        onChange={(e) => setSeason(e.target.value)}
                        className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-cyan-500 outline-none"
                      >
                        {['Pre-Monsoon', 'Monsoon', 'Post-Monsoon', 'Winter'].map((s) => (
                          <option key={s} value={s}>{s}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">Well Depth (m)</label>
                    <input
                      type="number"
                      step="0.1"
                      value={wellDepth}
                      onChange={(e) => setWellDepth(parseFloat(e.target.value) || 0)}
                      className="w-full px-3 py-1.5 rounded-lg border border-slate-300 text-sm"
                    />
                  </div>

                  <div className="pt-2 border-t border-slate-100">
                    <p className="text-xs font-bold text-slate-700 mb-2">Past Lags (Water Level m bgl)</p>
                    <div className="grid grid-cols-3 gap-2">
                      <div>
                        <label className="text-[10px] text-slate-500">Lag 1 (Prev)</label>
                        <input
                          type="number"
                          step="0.1"
                          value={lag1}
                          onChange={(e) => setLag1(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 text-xs border rounded"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-slate-500">Lag 2</label>
                        <input
                          type="number"
                          step="0.1"
                          value={lag2}
                          onChange={(e) => setLag2(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 text-xs border rounded"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-slate-500">Lag 4 (~1 yr)</label>
                        <input
                          type="number"
                          step="0.1"
                          value={lag4}
                          onChange={(e) => setLag4(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 text-xs border rounded"
                        />
                      </div>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-slate-100">
                    <p className="text-xs font-bold text-slate-700 mb-2">Antecedent Rainfall (mm)</p>
                    <div className="grid grid-cols-2 gap-2">
                      <div>
                        <label className="text-[10px] text-slate-500">Prior 30d (mm)</label>
                        <input
                          type="number"
                          step="1"
                          value={rain30d}
                          onChange={(e) => setRain30d(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 text-xs border rounded"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-slate-500">Prior 60d (mm)</label>
                        <input
                          type="number"
                          step="1"
                          value={rain60d}
                          onChange={(e) => setRain60d(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 text-xs border rounded"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-slate-500">Prior 90d (mm)</label>
                        <input
                          type="number"
                          step="1"
                          value={rain90d}
                          onChange={(e) => setRain90d(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 text-xs border rounded"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-slate-500">Prior 180d (mm)</label>
                        <input
                          type="number"
                          step="1"
                          value={rain180d}
                          onChange={(e) => setRain180d(parseFloat(e.target.value) || 0)}
                          className="w-full px-2 py-1 text-xs border rounded"
                        />
                      </div>
                    </div>
                  </div>
                </>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-2.5 px-4 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-sm transition-all shadow-md shadow-cyan-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Predicting with KNN (k=7)...</span>
                  </>
                ) : (
                  <>
                    <Gauge className="w-4 h-4" />
                    <span>Run Groundwater Prediction</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Model Specification Card */}
          <div className="bg-slate-50 rounded-xl p-4 border border-slate-200 text-xs text-slate-600 space-y-1.5">
            <p className="font-bold text-slate-800 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span>Experiment B Model Verified</span>
            </p>
            <p><strong>Algorithm:</strong> 7. KNN Regressor (k=7, distance-weighted)</p>
            <p><strong>Holdout Test Metrics:</strong> R² = 0.7766 | RMSE = 1.93 m | MAE = 1.32 m</p>
            <p><strong>TimeSeries CV (5-Fold):</strong> Mean RMSE = 1.9066 m (± 0.8294)</p>
            <p className="text-[11px] text-slate-400 pt-1">
              * Note: KNN outputs deterministic point estimates; arbitrary parametric confidence intervals are intentionally excluded.
            </p>
          </div>
        </div>

        {/* Prediction Results Column */}
        <div className="lg:col-span-7 space-y-6">
          {error && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-rose-500 mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-bold">Prediction Error</p>
                <p className="text-xs mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {result ? (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              {/* Header */}
              <div className="bg-gradient-to-r from-slate-900 to-cyan-950 p-6 text-white">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
                    {result.model_used}
                  </span>
                  {result.prediction_date && (
                    <span className="text-xs text-slate-300">
                      Target Date: {result.prediction_date}
                    </span>
                  )}
                </div>

                <div className="mt-4 flex flex-col sm:flex-row sm:items-baseline sm:justify-between gap-4">
                  <div>
                    <p className="text-xs text-slate-400 uppercase tracking-wider font-medium">
                      Predicted Water Table Depth
                    </p>
                    <div className="flex items-baseline gap-2 mt-1">
                      <span className="text-4xl font-black text-cyan-300">
                        {result.predicted_water_level_m_bgl.toFixed(2)}
                      </span>
                      <span className="text-lg text-slate-300 font-medium">m bgl</span>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">
                      meters below ground level
                    </p>
                  </div>

                  {result.effective_water_column_m !== null && result.effective_water_column_m !== undefined && (
                    <div className="bg-slate-800/80 px-4 py-3 rounded-lg border border-slate-700">
                      <p className="text-[11px] text-slate-400 uppercase font-medium">Effective Water Column</p>
                      <p className="text-xl font-bold text-emerald-400 mt-0.5">
                        {result.effective_water_column_m.toFixed(2)} m
                      </p>
                      <p className="text-[10px] text-slate-400">Total depth: {result.well_depth_m?.toFixed(1)} m</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Physical Well Water Column Visual Gauge */}
              <div className="p-6 border-b border-slate-100 bg-slate-50/50">
                <p className="text-xs font-bold text-slate-700 mb-3 flex items-center gap-1.5">
                  <Gauge className="w-4 h-4 text-cyan-600" />
                  <span>Physical Groundwater Cross-Section</span>
                </p>

                {result.well_depth_m ? (
                  <div className="space-y-2">
                    <div className="h-8 w-full bg-amber-100 rounded-lg overflow-hidden flex border border-amber-300 shadow-inner">
                      {/* Unsaturated Zone (Ground surface to water table) */}
                      <div 
                        style={{ width: `${Math.min(100, Math.max(5, (result.predicted_water_level_m_bgl / result.well_depth_m) * 100))}%` }}
                        className="bg-amber-700/30 flex items-center justify-center text-[11px] font-bold text-amber-900 border-r-2 border-dashed border-cyan-600"
                        title={`Unsaturated Zone: ${result.predicted_water_level_m_bgl.toFixed(2)} m`}
                      >
                        Unsaturated ({result.predicted_water_level_m_bgl.toFixed(1)}m)
                      </div>
                      {/* Saturated Aquifer Column */}
                      <div 
                        className="bg-gradient-to-r from-cyan-500 to-blue-600 flex-1 flex items-center justify-center text-[11px] font-bold text-white shadow-sm"
                        title={`Water Column: ${result.effective_water_column_m?.toFixed(2)} m`}
                      >
                        Water Column ({result.effective_water_column_m?.toFixed(1)}m)
                      </div>
                    </div>
                    <div className="flex justify-between text-[11px] text-slate-500 font-mono">
                      <span>0.0 m (Ground Surface)</span>
                      <span>Total Depth: {result.well_depth_m.toFixed(1)} m</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-slate-400">Well depth not recorded.</p>
                )}
              </div>

              {/* Validation & Ground Truth Comparison */}
              <div className="p-6 border-b border-slate-100">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-3">
                  Ground Truth Comparison & Verification
                </h4>

                {result.historical_actual_m_bgl !== null && result.historical_actual_m_bgl !== undefined ? (
                  <div className="grid grid-cols-3 gap-3 p-4 rounded-xl bg-emerald-50 border border-emerald-200">
                    <div>
                      <p className="text-xs text-emerald-800 font-medium">Actual Observation</p>
                      <p className="text-xl font-bold text-emerald-950 mt-0.5">
                        {result.historical_actual_m_bgl.toFixed(2)} m
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-emerald-800 font-medium">Predicted Level</p>
                      <p className="text-xl font-bold text-cyan-800 mt-0.5">
                        {result.predicted_water_level_m_bgl.toFixed(2)} m
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-emerald-800 font-medium">Absolute Error</p>
                      <p className="text-xl font-bold text-emerald-700 mt-0.5">
                        {result.absolute_error_m?.toFixed(2)} m
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600">
                    <p className="font-semibold text-slate-800">No Historical Observation Recorded for this exact date</p>
                    <p className="text-[11px] text-slate-500 mt-0.5">
                      Ground truth and error are not displayed because no actual physical reading exists for this date.
                    </p>
                  </div>
                )}
              </div>

              {/* Collapsible Features Used Accordion */}
              <div className="p-4 bg-slate-50">
                <button
                  onClick={() => setShowFeatures(!showFeatures)}
                  className="w-full flex items-center justify-between text-xs font-bold text-slate-700 hover:text-cyan-700"
                >
                  <span className="flex items-center gap-1.5">
                    <Sliders className="w-3.5 h-3.5" />
                    <span>View 16 Features Passed into Model Pipeline</span>
                  </span>
                  {showFeatures ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                </button>

                {showFeatures && (
                  <div className="mt-3 pt-3 border-t border-slate-200 grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                    {Object.entries(result.features_used).map(([k, v]) => (
                      <div key={k} className="p-2 bg-white rounded border border-slate-200">
                        <p className="text-[10px] text-slate-400 truncate">{k}</p>
                        <p className="font-mono font-medium text-slate-800 truncate">
                          {typeof v === 'number' ? v.toFixed(3) : String(v)}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-slate-50 rounded-xl border border-dashed border-slate-300 p-12 text-center text-slate-400">
              <Droplets className="w-12 h-12 mx-auto text-slate-300 mb-3" />
              <p className="text-sm font-semibold text-slate-600">No Prediction Yet</p>
              <p className="text-xs text-slate-400 mt-1">
                Select a well ID and monitoring date or configure a custom scenario to predict water table depth.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
