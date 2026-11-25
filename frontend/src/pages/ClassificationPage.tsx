import React, { useState } from 'react';
import {
  Activity,
  ShieldAlert,
  ShieldCheck,
  AlertCircle,
  Beaker,
  CheckCircle2,
  Scale,
  Info
} from 'lucide-react';
import { classifyWaterPotability } from '../services/api';
import type { WaterPotabilityRequest, WaterPotabilityResponse } from '../services/api';

export const ClassificationPage: React.FC = () => {
  // 11 Exact Physicochemical Parameters
  const [ph, setPh] = useState<number>(7.2);
  const [ec, setEc] = useState<number>(600.0);
  const [tds, setTds] = useState<string>('384.0');
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
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#E3EBE5] pb-5">
        <div>
          <div className="flex items-center gap-2 text-[#073B32] font-semibold text-xs tracking-wider uppercase">
            <span className="w-2 h-2 rounded-full bg-[#119B72]" />
            <span>Quality Assessment &bull; Digital Water Testing Laboratory</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#182C25] mt-1">
            Drinking Water Potability &amp; BIS Audit
          </h1>
          <p className="text-[#718078] text-xs sm:text-sm mt-1">
            Evaluates 11 laboratory physicochemical parameters against Bureau of Indian Standards (BIS IS 10500:2012) via XGBoost.
          </p>
        </div>

        {/* Preset Sample Buttons */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-[#718078]">Lab Presets:</span>
          <button
            type="button"
            onClick={() => applyPreset('potable')}
            className="px-3 py-1.5 text-xs font-semibold rounded-xl bg-[#EDF8F1] text-[#073B32] border border-[#D9F2E6] hover:bg-[#D9F2E6] transition-colors"
          >
            Safe Potable Sample
          </button>
          <button
            type="button"
            onClick={() => applyPreset('non_potable')}
            className="px-3 py-1.5 text-xs font-semibold rounded-xl bg-[#FDF2F2] text-[#E45B55] border border-[#FAD2D2] hover:bg-[#FAD2D2] transition-colors"
          >
            Contaminated Sample
          </button>
          <button
            type="button"
            onClick={() => applyPreset('missing_tds')}
            className="px-3 py-1.5 text-xs font-semibold rounded-xl bg-white text-[#182C25] border border-[#E3EBE5] hover:border-[#119B72] transition-colors"
          >
            Omit TDS (EC Ratio Fallback)
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Input Form Column (7 Cols) */}
        <div className="lg:col-span-7 space-y-5">
          <div className="bg-white rounded-2xl border border-[#E3EBE5] p-6 shadow-xs">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#E3EBE5]">
              <h2 className="text-xs font-bold text-[#182C25] uppercase tracking-wider flex items-center gap-2">
                <Beaker className="w-4 h-4 text-[#119B72]" />
                <span>Laboratory Physicochemical Inputs (11 Parameters)</span>
              </h2>
              <span className="text-[11px] font-semibold text-[#073B32] bg-[#EDF8F1] px-2 py-0.5 rounded border border-[#D9F2E6]">
                IS 10500 Compliant
              </span>
            </div>

            <form onSubmit={handleClassify} className="space-y-5">
              {/* Group 1: General & Salinity */}
              <div>
                <p className="text-[11px] font-bold uppercase tracking-wider text-[#718078] mb-2.5">
                  1. Acidity &amp; Salinity Indicators
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div>
                    <label className="text-[11px] font-bold text-[#182C25]">pH Level (0-14)</label>
                    <span className="text-[10px] text-[#718078] block">Limit: 6.5 &ndash; 8.5</span>
                    <input
                      type="number"
                      step="0.05"
                      min="0"
                      max="14"
                      value={ph}
                      onChange={(e) => setPh(parseFloat(e.target.value) || 0)}
                      required
                      className="w-full mt-1 px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-semibold text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-[#182C25]">Conductivity (EC)</label>
                    <span className="text-[10px] text-[#718078] block">&micro;S/cm at 25&deg;C</span>
                    <input
                      type="number"
                      step="1"
                      min="0"
                      value={ec}
                      onChange={(e) => setEc(parseFloat(e.target.value) || 0)}
                      required
                      className="w-full mt-1 px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-semibold text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-[#182C25]">TDS (mg/L)</label>
                    <span className="text-[10px] text-[#718078] block">Limit: &le; 500 mg/L</span>
                    <input
                      type="text"
                      value={tds}
                      onChange={(e) => setTds(e.target.value)}
                      placeholder="Blank for EC &times; 0.64"
                      className="w-full mt-1 px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-semibold text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none placeholder:text-[#718078]/60"
                    />
                  </div>
                </div>
              </div>

              {/* Group 2: Hardness & Cations */}
              <div className="pt-3 border-t border-[#E3EBE5]">
                <p className="text-[11px] font-bold uppercase tracking-wider text-[#718078] mb-2.5">
                  2. Hardness &amp; Major Cations (mg/L)
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div>
                    <label className="text-[11px] font-bold text-[#182C25]">Total Hardness</label>
                    <span className="text-[10px] text-[#718078] block">&le; 200 as CaCO3</span>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      value={th}
                      onChange={(e) => setTh(parseFloat(e.target.value) || 0)}
                      required
                      className="w-full mt-1 px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-semibold text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-[#182C25]">Calcium (Ca)</label>
                    <span className="text-[10px] text-[#718078] block">&le; 75 mg/L</span>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      value={ca}
                      onChange={(e) => setCa(parseFloat(e.target.value) || 0)}
                      required
                      className="w-full mt-1 px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-semibold text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-[#182C25]">Magnesium (Mg)</label>
                    <span className="text-[10px] text-[#718078] block">&le; 30 mg/L</span>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      value={mg}
                      onChange={(e) => setMg(parseFloat(e.target.value) || 0)}
                      required
                      className="w-full mt-1 px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-semibold text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-[#182C25]">Sodium (Na)</label>
                    <span className="text-[10px] text-[#718078] block">Alkali balance</span>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      value={na}
                      onChange={(e) => setNa(parseFloat(e.target.value) || 0)}
                      required
                      className="w-full mt-1 px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-semibold text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Group 3: Anions & Trace Metals */}
              <div className="pt-3 border-t border-[#E3EBE5]">
                <p className="text-[11px] font-bold uppercase tracking-wider text-[#718078] mb-2.5">
                  3. Anions &amp; Trace Dissolved Metals (mg/L)
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div>
                    <label className="text-[11px] font-bold text-[#182C25]">Chloride (Cl)</label>
                    <span className="text-[10px] text-[#718078] block">&le; 250 mg/L</span>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      value={cl}
                      onChange={(e) => setCl(parseFloat(e.target.value) || 0)}
                      required
                      className="w-full mt-1 px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-semibold text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-[#182C25]">Sulphate (SO4)</label>
                    <span className="text-[10px] text-[#718078] block">&le; 200 mg/L</span>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      value={so4}
                      onChange={(e) => setSo4(parseFloat(e.target.value) || 0)}
                      required
                      className="w-full mt-1 px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-semibold text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-[#182C25]">Dissolved Iron (Fe)</label>
                    <span className="text-[10px] text-[#718078] block">&le; 1.0 mg/L</span>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={fe}
                      onChange={(e) => setFe(parseFloat(e.target.value) || 0)}
                      required
                      className="w-full mt-1 px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-semibold text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] font-bold text-[#182C25]">Bicarbonate (HCO3)</label>
                    <span className="text-[10px] text-[#718078] block">Buffer alkalinity</span>
                    <input
                      type="number"
                      step="0.5"
                      min="0"
                      value={bicarb}
                      onChange={(e) => setBicarb(parseFloat(e.target.value) || 0)}
                      required
                      className="w-full mt-1 px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-semibold text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                    />
                  </div>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-3 px-4 rounded-xl bg-[#119B72] hover:bg-[#0E8360] text-white font-bold text-xs sm:text-sm transition-all shadow-md shadow-[#119B72]/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Evaluating Physicochemical Profile...</span>
                  </>
                ) : (
                  <>
                    <Activity className="w-4 h-4" />
                    <span>Classify Potability &amp; Check BIS Limits</span>
                  </>
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Output & Audit Result Column (5 Cols) */}
        <div className="lg:col-span-5 space-y-5">
          {error && (
            <div className="p-4 rounded-2xl bg-[#FDF2F2] border border-[#FAD2D2] text-[#E45B55] flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-[#E45B55] mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-bold">Evaluation Error</p>
                <p className="text-xs mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {result ? (
            <div className="bg-white rounded-2xl border border-[#E3EBE5] shadow-xs overflow-hidden space-y-5 p-6">
              {/* Primary Potability Outcome Banner */}
              <div
                className={`p-5 rounded-2xl border flex items-center justify-between ${result.potability_code === 1
                    ? 'bg-[#EDF8F1] border-[#D9F2E6] text-[#073B32]'
                    : 'bg-[#FDF2F2] border-[#FAD2D2] text-[#E45B55]'
                  }`}
              >
                <div>
                  <span className="text-[10px] uppercase font-bold tracking-wider">
                    Model Potability Classification
                  </span>
                  <h3 className="text-2xl font-extrabold mt-0.5">
                    {result.potability_label}
                  </h3>
                  <p className="text-xs mt-1">
                    Statistical confidence: {(result.confidence_score * 100).toFixed(1)}%
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-white shadow-xs">
                  {result.potability_code === 1 ? (
                    <ShieldCheck className="w-8 h-8 text-[#119B72]" />
                  ) : (
                    <ShieldAlert className="w-8 h-8 text-[#E45B55]" />
                  )}
                </div>
              </div>

              {/* Machine Learning Probability Breakdown */}
              <div className="space-y-2 bg-[#F8FAF7] p-4 rounded-xl border border-[#E3EBE5]">
                <p className="text-xs font-bold text-[#182C25] flex items-center justify-between">
                  <span>ML Class Probability Profile</span>
                  <span className="text-[10px] text-[#718078] font-normal">XGBoost (98.8% CV)</span>
                </p>

                <div className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-[#073B32]">Potable Probability</span>
                    <span className="font-bold text-[#182C25]">{(result.probability_potable * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-[#E3EBE5] overflow-hidden">
                    <div
                      className="h-full bg-[#119B72] rounded-full"
                      style={{ width: `${result.probability_potable * 100}%` }}
                    />
                  </div>
                </div>

                <div className="space-y-1 pt-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-[#E45B55]">Non-Potable Probability</span>
                    <span className="font-bold text-[#182C25]">{(result.probability_non_potable * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-[#E3EBE5] overflow-hidden">
                    <div
                      className="h-full bg-[#E45B55] rounded-full"
                      style={{ width: `${result.probability_non_potable * 100}%` }}
                    />
                  </div>
                </div>

                {result.input_tds_calculated && (
                  <p className="text-[10px] text-[#119B72] pt-2 border-t border-[#E3EBE5]">
                    &bull; Note: TDS was automatically derived from Electrical Conductivity via hydrological 0.64 factor.
                  </p>
                )}
              </div>

              {/* Separate BIS IS 10500:2012 Compliance Audit Section */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h4 className="text-xs font-bold text-[#182C25] uppercase tracking-wider flex items-center gap-1.5">
                    <Scale className="w-4 h-4 text-[#119B72]" />
                    <span>Statutory Standards Audit (BIS IS 10500)</span>
                  </h4>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${result.exceeded_parameters.length === 0
                        ? 'bg-[#EDF8F1] text-[#119B72] border border-[#D9F2E6]'
                        : 'bg-[#FDF2F2] text-[#E45B55] border border-[#FAD2D2]'
                      }`}
                  >
                    {result.exceeded_parameters.length === 0
                      ? 'Fully Compliant'
                      : `${result.exceeded_parameters.length} Violations`}
                  </span>
                </div>

                {result.exceeded_parameters.length === 0 ? (
                  <div className="p-3 rounded-xl bg-[#EDF8F1] border border-[#D9F2E6] text-xs text-[#073B32] flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-[#119B72] shrink-0" />
                    <span>All evaluated parameters reside within official BIS permissible drinking water limits.</span>
                  </div>
                ) : (
                  <div className="space-y-2">
                    {result.exceeded_parameters.map((e, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded-xl bg-[#FDF2F2] border border-[#FAD2D2] text-xs text-[#E45B55] space-y-1"
                      >
                        <div className="flex items-center justify-between font-bold">
                          <span>{e.parameter}</span>
                          <span>Observed: {e.observed_value} ({e.acceptable_limit})</span>
                        </div>
                        <p className="text-[11px] text-[#E45B55]/90">{e.description}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Explicit Mandatory Advisory Disclaimer */}
              <div className="p-3 rounded-xl bg-[#F8FAF7] border border-[#E3EBE5] text-[11px] text-[#718078] flex items-start gap-2 leading-relaxed">
                <Info className="w-4 h-4 text-[#718078] shrink-0 mt-0.5" />
                <p>
                  <strong className="text-[#182C25]">Regulatory Notice:</strong> Machine-learning potability estimates represent empirical statistical screening and do NOT certify drinking water safety. Formal potable release requires certified chemical, toxicological and microbiological laboratory assays.
                </p>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-2xl border border-[#E3EBE5] p-12 text-center text-[#718078] space-y-3">
              <Beaker className="w-12 h-12 text-[#CDDAD1] mx-auto" />
              <h3 className="text-base font-bold text-[#182C25]">Ready for Chemical Evaluation</h3>
              <p className="text-xs text-[#718078] max-w-sm mx-auto leading-relaxed">
                Enter your water sample parameters or choose a laboratory preset on the top right to assess potable suitability against Bureau of Indian Standards specifications.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
