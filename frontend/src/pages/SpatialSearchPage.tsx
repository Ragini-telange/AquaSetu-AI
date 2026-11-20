import React, { useState, useEffect, useRef } from 'react';
import { Search, AlertCircle, Compass, Layers } from 'lucide-react';
import L from 'leaflet';
import { findNearestWells } from '../services/api';
import type { NearestWellRequest, NearestWellResponse } from '../services/api';
import { createCustomPin } from '../components/MapHelper';

export const SpatialSearchPage: React.FC = () => {
  const [latitude, setLatitude] = useState<number>(18.5204);
  const [longitude, setLongitude] = useState<number>(73.8567);
  const [maxResults, setMaxResults] = useState<number>(5);
  const [districtFilter, setDistrictFilter] = useState<string>('');

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<NearestWellResponse | null>(null);

  // Leaflet map reference
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);

  // Preset quick coordinates across Maharashtra
  const presets = [
    { label: 'Pune City', lat: 18.5204, lon: 73.8567, district: 'Pune' },
    { label: 'Baramati (Pune)', lat: 18.1520, lon: 74.5770, district: 'Pune' },
    { label: 'Wardha', lat: 20.9611, lon: 78.5625, district: 'Wardha' },
    { label: 'Solapur', lat: 17.6599, lon: 75.9064, district: 'Solapur' },
    { label: 'Nagpur', lat: 21.1458, lon: 79.0882, district: 'Nagpur' },
  ];

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current).setView([18.5204, 73.8567], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 18,
    }).addTo(map);

    const markers = L.layerGroup().addTo(map);
    markersLayerRef.current = markers;
    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update map markers when response changes
  useEffect(() => {
    if (!mapInstanceRef.current || !markersLayerRef.current) return;

    const markers = markersLayerRef.current;
    markers.clearLayers();

    // Query Pin (Blue)
    const queryPin = createCustomPin('blue');
    const queryMarker = L.marker([latitude, longitude], { icon: queryPin })
      .bindPopup(`<strong>Search Coordinate</strong><br/>Lat: ${latitude.toFixed(4)}, Lon: ${longitude.toFixed(4)}`);
    markers.addLayer(queryMarker);

    if (response && response.nearest_wells.length > 0) {
      const bounds = L.latLngBounds([L.latLng(latitude, longitude)]);

      response.nearest_wells.forEach((well, idx) => {
        const wellPin = createCustomPin('teal');
        bounds.extend([well.latitude, well.longitude]);

        const popupContent = `
          <div style="font-family: sans-serif; font-size: 12px; line-height: 1.4;">
            <div style="font-weight: bold; color: #0f172a; font-size: 13px;">#${idx + 1} ${well.village} (${well.district})</div>
            <div style="color: #0d9488; font-weight: 600; margin-top: 2px;">Distance: ${well.distance_km} km</div>
            <div style="color: #64748b; font-size: 11px; margin-top: 4px;">Block: ${well.block}</div>
            <div style="color: #64748b; font-size: 11px;">Wells at Location: ${well.num_wells} (${well.well_ids.slice(0, 2).join(', ')})</div>
            ${well.pune_road_node_id ? `<div style="color: #4f46e5; font-size: 10px; margin-top: 4px;">Pune Node ID: ${well.pune_road_node_id} (Snap: ${well.snap_distance_m}m)</div>` : ''}
          </div>
        `;

        const wellMarker = L.marker([well.latitude, well.longitude], { icon: wellPin })
          .bindPopup(popupContent);
        markers.addLayer(wellMarker);
      });

      mapInstanceRef.current.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
    } else {
      mapInstanceRef.current.setView([latitude, longitude], 11);
    }
  }, [response, latitude, longitude]);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload: NearestWellRequest = {
        latitude: parseFloat(String(latitude)),
        longitude: parseFloat(String(longitude)),
        max_results: maxResults,
        filter_district: districtFilter.trim() || undefined,
      };

      const res = await findNearestWells(payload);
      setResponse(res);
    } catch (err: any) {
      setError(err.message || 'Failed to search nearest wells.');
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2 text-indigo-600 font-semibold text-xs tracking-wider uppercase">
            <Compass className="w-4 h-4" />
            <span>Vedangi &bull; Spatial Nearest-Well Search</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-1">
            Statewide Nearest-Well Discovery
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            2D spatial indexing across all 4,381 well locations in all 33 Maharashtra districts via KDTree & Haversine.
          </p>
        </div>

        {/* Quick Location Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-400">Presets:</span>
          {presets.map((p) => (
            <button
              key={p.label}
              onClick={() => {
                setLatitude(p.lat);
                setLongitude(p.lon);
                setDistrictFilter(p.district);
              }}
              className="px-2.5 py-1 text-xs font-medium rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100 transition-colors"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Controls Column */}
        <div className="lg:col-span-4 space-y-5">
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-4">
              Coordinate Query Parameters
            </h3>

            <form onSubmit={handleSearch} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Query Latitude</label>
                <input
                  type="number"
                  step="0.0001"
                  value={latitude}
                  onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                  required
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Query Longitude</label>
                <input
                  type="number"
                  step="0.0001"
                  value={longitude}
                  onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                  required
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Max Results</label>
                  <select
                    value={maxResults}
                    onChange={(e) => setMaxResults(parseInt(e.target.value, 10))}
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                  >
                    <option value={3}>3 wells</option>
                    <option value={5}>5 wells</option>
                    <option value={10}>10 wells</option>
                    <option value={15}>15 wells</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">District Filter</label>
                  <input
                    type="text"
                    value={districtFilter}
                    onChange={(e) => setDistrictFilter(e.target.value)}
                    placeholder="Optional (e.g. Pune)"
                    className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-2.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition-all shadow-md shadow-indigo-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Searching KDTree...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    <span>Find Nearest Wells</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Module Architecture Scope Callout */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600 space-y-1.5">
            <p className="font-bold text-slate-800 flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-indigo-600" />
              <span>Statewide Spatial Discovery</span>
            </p>
            <p>
              Unlike road network routing which is restricted strictly to Pune, nearest-well search covers
              <strong> all 33 districts</strong> in Maharashtra using high-speed 2D spatial indexing.
            </p>
            <p className="text-[11px] text-slate-400">
              Latency: &lt; 1.0 ms across 4,381 monitored locations.
            </p>
          </div>
        </div>

        {/* Interactive Map & Table Column */}
        <div className="lg:col-span-8 space-y-5">
          {error && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-rose-500 mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-bold">Search Error</p>
                <p className="text-xs mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {/* Leaflet Map Card */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-3 text-xs">
              <div className="flex items-center gap-4">
                <span className="font-bold text-slate-700">OpenStreetMap Interactive View</span>
                <span className="flex items-center gap-1.5 text-slate-500">
                  <span className="w-2.5 h-2.5 rounded-full bg-cyan-600" /> Query Center
                </span>
                <span className="flex items-center gap-1.5 text-slate-500">
                  <span className="w-2.5 h-2.5 rounded-full bg-teal-600" /> Nearest Wells
                </span>
              </div>
              <span className="text-slate-400 text-[11px]">Click markers for details</span>
            </div>

            <div 
              ref={mapContainerRef} 
              className="h-[380px] w-full rounded-lg border border-slate-200"
            />
          </div>

          {/* Results Table */}
          {response && response.nearest_wells.length > 0 && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
              <div className="p-4 border-b border-slate-100 flex items-center justify-between">
                <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                  Discovered Wells ({response.total_found} Locations)
                </h4>
                <span className="text-xs text-slate-400">Sorted by Haversine Distance</span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 text-slate-500 uppercase text-[10px] border-b border-slate-200">
                    <tr>
                      <th className="py-2.5 px-3">#</th>
                      <th className="py-2.5 px-3">Village / Block</th>
                      <th className="py-2.5 px-3">District</th>
                      <th className="py-2.5 px-3">Distance</th>
                      <th className="py-2.5 px-3">Well IDs</th>
                      <th className="py-2.5 px-3">Pune Snap</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {response.nearest_wells.map((well, idx) => (
                      <tr key={well.location_id} className="hover:bg-slate-50/70">
                        <td className="py-2.5 px-3 font-bold text-slate-700">{idx + 1}</td>
                        <td className="py-2.5 px-3">
                          <p className="font-semibold text-slate-900">{well.village}</p>
                          <p className="text-[10px] text-slate-400">{well.block}</p>
                        </td>
                        <td className="py-2.5 px-3 font-medium text-slate-700">{well.district}</td>
                        <td className="py-2.5 px-3">
                          <span className="font-bold text-teal-700 bg-teal-50 px-2 py-0.5 rounded">
                            {well.distance_km.toFixed(2)} km
                          </span>
                        </td>
                        <td className="py-2.5 px-3 font-mono text-[11px] text-slate-600 truncate max-w-[140px]">
                          {well.well_ids.join(', ')}
                        </td>
                        <td className="py-2.5 px-3 text-[11px]">
                          {well.pune_road_node_id ? (
                            <span className="text-indigo-600 font-mono font-medium">
                              #{well.pune_road_node_id} ({well.snap_distance_m}m)
                            </span>
                          ) : (
                            <span className="text-slate-300">N/A</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
