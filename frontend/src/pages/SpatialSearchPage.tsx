import React, { useState, useEffect, useRef } from 'react';
import { Search, AlertCircle, Compass, Layers, Info } from 'lucide-react';
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

    const map = L.map(mapContainerRef.current, { zoomControl: false }).setView([18.5204, 73.8567], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors | AquaGuard AI',
      maxZoom: 18,
    }).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    const markers = L.layerGroup().addTo(map);
    markersLayerRef.current = markers;
    mapInstanceRef.current = map;

    // Click map to select coordinates
    map.on('click', (e: L.LeafletMouseEvent) => {
      const { lat, lng } = e.latlng;
      setLatitude(Number(lat.toFixed(4)));
      setLongitude(Number(lng.toFixed(4)));
    });

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

    // Query Pin (Forest Green)
    const queryPin = createCustomPin('forest');
    const queryMarker = L.marker([latitude, longitude], { icon: queryPin })
      .bindPopup(`<strong style="color:#073B32;">Target Query Coordinates</strong><br/>Lat: ${latitude.toFixed(4)}, Lon: ${longitude.toFixed(4)}`);
    markers.addLayer(queryMarker);

    if (response && response.nearest_wells.length > 0) {
      const bounds = L.latLngBounds([L.latLng(latitude, longitude)]);

      response.nearest_wells.forEach((well, idx) => {
        const wellPin = createCustomPin('emerald');
        bounds.extend([well.latitude, well.longitude]);

        // Connection line
        const line = L.polyline(
          [[latitude, longitude], [well.latitude, well.longitude]],
          { color: '#119B72', weight: 1.5, dashArray: '4, 4', opacity: 0.7 }
        );
        markers.addLayer(line);

        const popupContent = `
          <div style="font-family: sans-serif; font-size: 12px; line-height: 1.4; color: #182C25;">
            <div style="font-weight: bold; color: #073B32; font-size: 13px;">#${idx + 1} ${well.village} (${well.district})</div>
            <div style="color: #119B72; font-weight: 700; margin-top: 2px;">Distance: ${well.distance_km} km</div>
            <div style="color: #718078; font-size: 11px; margin-top: 4px;">Block: ${well.block}</div>
            <div style="color: #718078; font-size: 11px;">Wells at Location: ${well.num_wells} (${well.well_ids.slice(0, 2).join(', ')})</div>
            ${well.pune_road_node_id ? `<div style="color: #0B4F43; font-size: 10px; font-weight: 600; margin-top: 4px;">Pune Node ID: #${well.pune_road_node_id} (Snap: ${well.snap_distance_m}m)</div>` : ''}
          </div>
        `;

        const wellMarker = L.marker([well.latitude, well.longitude], { icon: wellPin })
          .bindPopup(popupContent);
        markers.addLayer(wellMarker);
      });

      mapInstanceRef.current.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 });
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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-[#E3EBE5] pb-5">
        <div>
          <div className="flex items-center gap-2 text-[#073B32] font-semibold text-xs tracking-wider uppercase">
            <span className="w-2 h-2 rounded-full bg-[#119B72]" />
            <span>Spatial Discovery &bull; Nearest-Well Search Engine</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#182C25] mt-1">
            Statewide Nearest-Well Discovery Engine
          </h1>
          <p className="text-[#718078] text-xs sm:text-sm mt-1">
            Spatial indexing across all 4,381 well locations in all 33 Maharashtra districts via optimized 2D KDTree &amp; Haversine.
          </p>
        </div>

        {/* Quick Location Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-[#718078]">Presets:</span>
          {presets.map((p) => (
            <button
              key={p.label}
              onClick={() => {
                setLatitude(p.lat);
                setLongitude(p.lon);
                setDistrictFilter(p.district);
              }}
              className="px-3 py-1.5 text-xs font-semibold rounded-xl bg-white text-[#182C25] border border-[#E3EBE5] hover:border-[#119B72] hover:bg-[#EDF8F1] transition-colors"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Controls Column (4 Cols) */}
        <div className="lg:col-span-4 space-y-5">
          <div className="bg-white rounded-2xl border border-[#E3EBE5] p-5 shadow-xs">
            <h3 className="text-xs font-bold text-[#182C25] uppercase tracking-wider mb-4 flex items-center gap-2">
              <Compass className="w-4 h-4 text-[#119B72]" />
              <span>Coordinate Query Parameters</span>
            </h3>

            <form onSubmit={handleSearch} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#182C25] mb-1">Query Latitude</label>
                <input
                  type="number"
                  step="0.0001"
                  value={latitude}
                  onChange={(e) => setLatitude(parseFloat(e.target.value) || 0)}
                  required
                  className="w-full px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-mono text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#182C25] mb-1">Query Longitude</label>
                <input
                  type="number"
                  step="0.0001"
                  value={longitude}
                  onChange={(e) => setLongitude(parseFloat(e.target.value) || 0)}
                  required
                  className="w-full px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-mono text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-[#182C25] mb-1">Max Results</label>
                  <select
                    value={maxResults}
                    onChange={(e) => setMaxResults(parseInt(e.target.value, 10))}
                    className="w-full px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                  >
                    <option value={3}>3 wells</option>
                    <option value={5}>5 wells</option>
                    <option value={10}>10 wells</option>
                    <option value={15}>15 wells</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-[#182C25] mb-1">District Filter</label>
                  <input
                    type="text"
                    value={districtFilter}
                    onChange={(e) => setDistrictFilter(e.target.value)}
                    placeholder="Optional (e.g. Pune)"
                    className="w-full px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-3 px-4 rounded-xl bg-[#119B72] hover:bg-[#0E8360] text-white font-bold text-xs sm:text-sm transition-all shadow-md shadow-[#119B72]/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Querying KDTree Index...</span>
                  </>
                ) : (
                  <>
                    <Search className="w-4 h-4" />
                    <span>Discover Nearest Wells</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Module Scope Notice */}
          <div className="p-4 rounded-2xl bg-[#EDF8F1] border border-[#D9F2E6] text-xs text-[#073B32] space-y-1.5">
            <p className="font-bold flex items-center gap-1.5 text-[#073B32]">
              <Layers className="w-4 h-4 text-[#119B72]" />
              <span>Statewide Spatial Coverage</span>
            </p>
            <p className="leading-relaxed text-[#073B32]/85">
              Spatial nearest-well search indexes <strong>4,381 monitoring locations across all 33 Maharashtra districts</strong> with sub-millisecond latency. Click anywhere on the map to set target coordinates.
            </p>
          </div>
        </div>

        {/* Interactive Map & Table Column (8 Cols) */}
        <div className="lg:col-span-8 space-y-5">
          {error && (
            <div className="p-4 rounded-2xl bg-[#FDF2F2] border border-[#FAD2D2] text-[#E45B55] flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-[#E45B55] mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-bold">Spatial Search Error</p>
                <p className="text-xs mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {/* Map View */}
          <div className="bg-white rounded-2xl border border-[#E3EBE5] p-4 shadow-xs">
            <div className="h-[380px] rounded-xl overflow-hidden border border-[#E3EBE5]">
              <div ref={mapContainerRef} className="w-full h-full" />
            </div>
            <p className="text-[11px] text-[#718078] mt-2 flex items-center gap-1.5">
              <Info className="w-3.5 h-3.5 text-[#119B72]" />
              <span>Click anywhere on the map to instantly update search latitude and longitude.</span>
            </p>
          </div>

          {/* Discovered Nearest Wells Results */}
          {response && (
            <div className="bg-white rounded-2xl border border-[#E3EBE5] p-5 shadow-xs space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#E3EBE5]">
                <div>
                  <h3 className="text-sm font-bold text-[#182C25]">
                    Discovered Nearest Monitoring Locations ({response.total_found})
                  </h3>
                  <p className="text-[11px] text-[#718078]">
                    Sorted by true spherical Haversine distance from ({response.query_coords.latitude.toFixed(4)}, {response.query_coords.longitude.toFixed(4)})
                  </p>
                </div>
                <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-[#EDF8F1] text-[#119B72] border border-[#D9F2E6]">
                  {response.total_found} Wells Found
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {response.nearest_wells.map((well, idx) => (
                  <div
                    key={well.location_id}
                    className="p-3.5 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] hover:bg-white hover:border-[#119B72]/40 transition-all space-y-2"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-xs font-bold text-[#182C25]">
                          #{idx + 1} {well.village}
                        </span>
                        <p className="text-[11px] text-[#718078]">{well.block}, {well.district}</p>
                      </div>
                      <span className="text-xs font-extrabold text-[#119B72] bg-[#EDF8F1] px-2.5 py-0.5 rounded-full border border-[#D9F2E6]">
                        {well.distance_km} km
                      </span>
                    </div>

                    <div className="text-[11px] text-[#718078] space-y-0.5 pt-1 border-t border-[#E3EBE5]">
                      <p>Station Node: <strong>#{well.location_id}</strong> &bull; Wells: {well.num_wells}</p>
                      <p className="font-mono text-[10px]">
                        Coords: {well.latitude.toFixed(4)}, {well.longitude.toFixed(4)}
                      </p>
                      {well.pune_road_node_id && (
                        <p className="text-[10px] text-[#073B32] font-semibold">
                          Pune Road Graph Node: #{well.pune_road_node_id} (snap: {well.snap_distance_m}m)
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
