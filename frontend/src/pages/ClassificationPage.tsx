import React, { useState } from 'react';
import { Activity, ShieldAlert, ShieldCheck, AlertCircle, Info, Sparkles } from 'lucide-react';
import { classifyWaterPotability } from '../services/api';
import type { WaterPotabilityRequest, WaterPotabilityResponse } from '../services/api';

export const ClassificationPage: React.FC = () => {
  // 11 Exact Physicochemical Parameters
  const [ph, setPh] = useState<number>(7.2);
  const [ec, setEc] = useState<number>(600.0);
  const [tds, setTds] = useState<string>('384.0'); // String to allow omitting
  const [th, setTh] = useState<number>(180.0);
  const [ca, setCa] = useState<number>(50.0);
  const [mg, setMg] = useState<number>(25.0);
  const [cl, setCl] = useState<number>(140.0);
  const [so4, setSo4] = useState<number>(90.0);
  const [fe, setFe] = useState<number>(0.1);
  const [bicarb, setBicarb] = useState<number>(200.0);
  const [na, setNa] = useState<number>(45.0);

  // Status & Output
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<WaterPotabilityResponse | null>(null);

  // Quick Preset Samples
  const applyPreset = (preset: 'potable' | 'non_potable' | 'missing_tds') => {
    setError(null);
    if (preset === 'potable') {
      setPh(7.2);
      setEc(600.0);
      setTds('384.0');
      setTh(180.0);
      setCa(50.0);
      setMg(25.0);
      setCl(140.0);
      setSo4(90.0);
      setFe(0.1);
      setBicarb(200.0);
      setNa(45.0);
    } else if (preset === 'non_potable') {
      setPh(9.1);
      setEc(2200.0);
      setTds('1408.0');
      setTh(350.0);
      setCa(90.0);
      setMg(45.0);
      setCl(320.0);
      setSo4(280.0);
      setFe(1.8);
      setBicarb(350.0);
      setNa(120.0);
    } else if (preset === 'missing_tds') {
      setPh(7.4);
      setEc(500.0);
      setTds(''); // Omitted TDS to exercise fallback TDS = 0.64 * EC
      setTh(150.0);
      setCa(40.0);
      setMg(20.0);
      setCl(100.0);
      setSo4(75.0);
      setFe(0.05);
      setBicarb(180.0);
      setNa(30.0);
    }
  };

  const handleClassify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const parsedTds = tds.trim() === '' ? null : parseFloat(tds);
      const payload: WaterPotabilityRequest = {
        pH: ph,
        Electrical_Conductivity: ec,
        TDS: parsedTds,
        Total_Hardness: th,
        Calcium: ca,
        Magnesium: mg,
        Chloride: cl,
        Sulphate: so4,
        Iron: fe,
        Bicarbonate: bicarb,
        Sodium: na,
      };

      const res = await classifyWaterPotability(payload);
      setResult(res);
    } catch (err: any) {
      setError(err.message || 'Failed to classify water quality.');
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
          <div className="flex items-center gap-2 text-teal-600 font-semibold text-xs tracking-wider uppercase">
            <Activity className="w-4 h-4" />
            <span>Sakshi &bull; Water Quality Classification</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-1">
            Drinking Water Potability Classification
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Evaluates physicochemical water safety against Bureau of Indian Standards (BIS IS 10500:2012).
          </p>
        </div>

        {/* Preset Sample Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-400">Presets:</span>
          <button
            type="button"
            onClick={() => applyPreset('potable')}
            className="px-2.5 py-1 text-xs font-medium rounded-lg bg-emerald-50 text-emerald-700 border border-emerald-200 hover:bg-emerald-100 transition-colors"
          >
            Safe Potable
          </button>
          <button
            type="button"
            onClick={() => applyPreset('non_potable')}
            className="px-2.5 py-1 text-xs font-medium rounded-lg bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 transition-colors"
          >
            Contaminated
          </button>
          <button
            type="button"
            onClick={() => applyPreset('missing_tds')}
            className="px-2.5 py-1 text-xs font-medium rounded-lg bg-cyan-50 text-cyan-700 border border-cyan-200 hover:bg-cyan-100 transition-colors"
          >
            Omit TDS (Fallback)
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Input Form Column */}
        <div className="lg:col-span-7">
          <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4 flex items-center justify-between">
              <span>Physicochemical Parameters (11 Inputs)</span>
              <span className="text-xs font-normal text-slate-400">BIS IS 10500:2012</span>
            </h2>

            <form onSubmit={handleClassify} className="space-y-4">
              {/* Row 1: pH and EC */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <div className="flex justify-between items-baseline mb-1">
                    <label className="text-xs font-bold text-slate-700">1. pH Level</label>
                    <span className="text-[11px] text-slate-400">Permissible: 6.5 – 8.5</span>
                  </div>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="14"
                    value={ph}
                    onChange={(e) => setPh(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>

                <div>
                  <div className="flex justify-between items-baseline mb-1">
                    <label className="text-xs font-bold text-slate-700">2. Electrical Conductivity</label>
                    <span className="text-[11px] text-slate-400">µS/cm at 25°C</span>
                  </div>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    value={ec}
                    onChange={(e) => setEc(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>
              </div>

              {/* Row 2: TDS and Hardness */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <div className="flex justify-between items-baseline mb-1">
                    <label className="text-xs font-bold text-slate-700">3. Total Dissolved Solids (TDS)</label>
                    <span className="text-[11px] text-slate-400">Limit: ≤ 500 mg/L</span>
                  </div>
                  <input
                    type="text"
                    value={tds}
                    onChange={(e) => setTds(e.target.value)}
                    placeholder="Leave blank for automatic 0.64 * EC fallback"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-teal-500 outline-none placeholder:text-slate-300"
                  />
                  <p className="text-[10px] text-teal-600 mt-1">
                    * If blank, backend applies hydrological ratio: TDS = 0.64 × EC
                  </p>
                </div>

                <div>
                  <div className="flex justify-between items-baseline mb-1">
                    <label className="text-xs font-bold text-slate-700">4. Total Hardness (as CaCO₃)</label>
                    <span className="text-[11px] text-slate-400">Limit: ≤ 200 mg/L</span>
                  </div>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={th}
                    onChange={(e) => setTh(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>
              </div>

              {/* Row 3: Calcium & Magnesium */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <div className="flex justify-between items-baseline mb-1">
                    <label className="text-xs font-bold text-slate-700">5. Calcium (Ca²⁺)</label>
                    <span className="text-[11px] text-slate-400">Limit: ≤ 75 mg/L</span>
                  </div>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={ca}
                    onChange={(e) => setCa(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>

                <div>
                  <div className="flex justify-between items-baseline mb-1">
                    <label className="text-xs font-bold text-slate-700">6. Magnesium (Mg²⁺)</label>
                    <span className="text-[11px] text-slate-400">Limit: ≤ 30 mg/L</span>
                  </div>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={mg}
                    onChange={(e) => setMg(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>
              </div>

              {/* Row 4: Chloride & Sulphate */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <div className="flex justify-between items-baseline mb-1">
                    <label className="text-xs font-bold text-slate-700">7. Chloride (Cl⁻)</label>
                    <span className="text-[11px] text-slate-400">Limit: ≤ 250 mg/L</span>
                  </div>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={cl}
                    onChange={(e) => setCl(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>

                <div>
                  <div className="flex justify-between items-baseline mb-1">
                    <label className="text-xs font-bold text-slate-700">8. Sulphate (SO₄²⁻)</label>
                    <span className="text-[11px] text-slate-400">Limit: ≤ 200 mg/L</span>
                  </div>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={so4}
                    onChange={(e) => setSo4(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>
              </div>

              {/* Row 5: Iron, Bicarbonate, Sodium */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <div className="flex justify-between items-baseline mb-1">
                    <label className="text-xs font-bold text-slate-700">9. Iron (Fe)</label>
                    <span className="text-[10px] text-slate-400">≤ 1.0 mg/L</span>
                  </div>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={fe}
                    onChange={(e) => setFe(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>

                <div>
                  <div className="flex justify-between items-baseline mb-1">
                    <label className="text-xs font-bold text-slate-700">10. Bicarbonate</label>
                    <span className="text-[10px] text-slate-400">mg/L</span>
                  </div>
                  <input
                    type="number"
                    step="1"
                    min="0"
                    value={bicarb}
                    onChange={(e) => setBicarb(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>

                <div>
                  <div className="flex justify-between items-baseline mb-1">
                    <label className="text-xs font-bold text-slate-700">11. Sodium (Na⁺)</label>
                    <span className="text-[10px] text-slate-400">mg/L</span>
                  </div>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    value={na}
                    onChange={(e) => setNa(parseFloat(e.target.value) || 0)}
                    required
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-teal-500 outline-none"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-4 py-2.5 px-4 rounded-lg bg-teal-600 hover:bg-teal-500 text-white font-semibold text-sm transition-all shadow-md shadow-teal-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Evaluating with XGBoost...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" />
                    <span>Classify Water Potability</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Results Column */}
        <div className="lg:col-span-5 space-y-6">
          {error && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-rose-500 mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-bold">Evaluation Error</p>
                <p className="text-xs mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {result ? (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden space-y-4">
              {/* Outcome Badge Card */}
              <div className={`p-6 text-white ${
                result.potability_code === 1
                  ? 'bg-gradient-to-r from-emerald-700 to-teal-800'
                  : 'bg-gradient-to-r from-rose-800 to-red-950'
              }`}>
                <div className="flex items-center gap-3">
                  {result.potability_code === 1 ? (
                    <ShieldCheck className="w-10 h-10 text-emerald-300" />
                  ) : (
                    <ShieldAlert className="w-10 h-10 text-rose-300" />
                  )}
                  <div>
                    <span className="text-xs font-semibold uppercase tracking-wider text-slate-200">
                      Classification Result
                    </span>
                    <h3 className="text-2xl font-black tracking-tight">
                      {result.potability_label === 'Potable' ? 'POTABLE WATER (SAFE)' : 'NON-POTABLE (UNSAFE)'}
                    </h3>
                  </div>
                </div>

                <div className="mt-5 grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-black/20 p-2.5 rounded-lg border border-white/10">
                    <p className="text-slate-300">Potable Probability</p>
                    <p className="text-lg font-bold text-emerald-300 mt-0.5">
                      {(result.probability_potable * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="bg-black/20 p-2.5 rounded-lg border border-white/10">
                    <p className="text-slate-300">Non-Potable Probability</p>
                    <p className="text-lg font-bold text-rose-300 mt-0.5">
                      {(result.probability_non_potable * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>

                {result.input_tds_calculated && (
                  <p className="mt-3 text-[11px] text-teal-200 bg-white/10 px-2.5 py-1 rounded">
                    &bull; Notice: TDS was omitted and automatically calculated via 0.64 × EC domain ratio.
                  </p>
                )}
              </div>

              {/* Exceeded Parameters Table */}
              <div className="p-5">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-2.5">
                  Physicochemical Limits Audit (BIS IS 10500:2012)
                </h4>

                {result.exceeded_parameters.length > 0 ? (
                  <div className="space-y-2">
                    {result.exceeded_parameters.map((ex, idx) => (
                      <div key={idx} className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs">
                        <div className="flex justify-between items-baseline font-bold text-rose-900">
                          <span>{ex.parameter} Exceedance</span>
                          <span className="text-rose-700">Observed: {ex.observed_value} ({ex.acceptable_limit})</span>
                        </div>
                        <p className="text-rose-800 text-[11px] mt-0.5">{ex.description}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-3.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
                    <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
                    <span>All tested physicochemical parameters conform strictly to BIS IS 10500:2012 acceptable limits.</span>
                  </div>
                )}
              </div>

              {/* Statutory Advisory */}
              <div className="p-4 bg-slate-50 border-t border-slate-200 text-slate-500 text-[11px] leading-relaxed flex items-start gap-2.5">
                <Info className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
                <p>{result.regulatory_advisory}</p>
              </div>
            </div>
          ) : (
            <div className="bg-slate-50 rounded-xl border border-dashed border-slate-300 p-12 text-center text-slate-400">
              <Activity className="w-12 h-12 mx-auto text-slate-300 mb-3" />
              <p className="text-sm font-semibold text-slate-600">No Classification Run</p>
              <p className="text-xs text-slate-400 mt-1">
                Enter physicochemical parameters or select a preset sample to classify potability against BIS standards.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
