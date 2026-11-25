import React, { useState, useEffect, useRef } from 'react';
import { Navigation, AlertCircle, Zap, ShieldAlert, Clock } from 'lucide-react';
import L from 'leaflet';
import { findPuneRoute } from '../services/api';
import type { PuneRoutingRequest, PuneRoutingResponse } from '../services/api';
import { createCustomPin } from '../components/MapHelper';

export const RoutingPage: React.FC = () => {
  const [startNode, setStartNode] = useState<number>(12788595845);
  const [targetNode, setTargetNode] = useState<number>(12788595830);
  const [algorithm, setAlgorithm] = useState<'A*' | 'Bidirectional' | 'BFS' | 'Greedy_Best_First' | 'IDDFS' | 'DFS'>('A*');
  const [maxDepth, setMaxDepth] = useState<number>(25);

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<PuneRoutingResponse | null>(null);

  // Map references
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const routeLayerRef = useRef<L.LayerGroup | null>(null);

  // Validated test pairs from the audit
  const testPairs = [
    { label: 'Sarati Village Hop', src: 12788595845, dst: 12788595830, desc: 'Local alley shortcut hop (A*)' },
    { label: 'Bhor Town Route', src: 1849234040, dst: 2542090919, desc: 'Town-level arterial route' },
    { label: 'Sakurde to Belsar', src: 5983616771, dst: 5378450158, desc: 'Inter-village path in Purandhar' },
  ];

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    // Center on Pune District
    const map = L.map(mapContainerRef.current, { zoomControl: false }).setView([18.5204, 73.8567], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors | AquaSetu AI',
      maxZoom: 18,
    }).addTo(map);

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    const routeLayer = L.layerGroup().addTo(map);
    routeLayerRef.current = routeLayer;
    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update route geometry on map when response updates
  useEffect(() => {
    if (!mapInstanceRef.current || !routeLayerRef.current) return;

    const layer = routeLayerRef.current;
    layer.clearLayers();

    if (response && response.success && response.route_geometry && response.route_geometry.length > 0) {
      const geom = response.route_geometry; // [lat, lon] tuples
      const latLngs = geom.map(([lat, lon]) => L.latLng(lat, lon));

      // Draw Green Route Polyline
      const polyline = L.polyline(latLngs, {
        color: '#119B72',
        weight: 5,
        opacity: 0.9,
        lineCap: 'round',
        lineJoin: 'round',
      });
      layer.addLayer(polyline);

      // Start Pin (Forest Green)
      const startCoord = latLngs[0];
      const startMarker = L.marker(startCoord, { icon: createCustomPin('forest') })
        .bindPopup(`<strong style="color:#073B32;">Start Node:</strong> #${response.start_node_id}`);
      layer.addLayer(startMarker);

      // End Pin (Critical Red)
      const endCoord = latLngs[latLngs.length - 1];
      const endMarker = L.marker(endCoord, { icon: createCustomPin('red') })
        .bindPopup(`<strong style="color:#E45B55;">Target Node:</strong> #${response.target_node_id}`);
      layer.addLayer(endMarker);

      // Fit map to route bounds
      mapInstanceRef.current.fitBounds(polyline.getBounds(), { padding: [50, 50], maxZoom: 16 });
    }
  }, [response]);

  const handleRoute = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload: PuneRoutingRequest = {
        start_node_id: parseInt(String(startNode), 10),
        target_node_id: parseInt(String(targetNode), 10),
        algorithm: algorithm,
        max_depth: algorithm === 'IDDFS' ? maxDepth : undefined,
      };

      const res = await findPuneRoute(payload);
      setResponse(res);
    } catch (err: any) {
      setError(err.message || 'Failed to compute route.');
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
            <span>Route Intelligence &bull; Pune Road Network Routing</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-[#182C25] mt-1">
            Pune Road Graph Route Intelligence
          </h1>
          <p className="text-[#718078] text-xs sm:text-sm mt-1">
            Pathfinding algorithms executed on 170,253 nodes &amp; 409,399 directed OpenStreetMap road segments across Pune District.
          </p>
        </div>

        {/* Test Pairs Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-[#718078]">Audit Presets:</span>
          {testPairs.map((tp) => (
            <button
              key={tp.label}
              onClick={() => {
                setStartNode(tp.src);
                setTargetNode(tp.dst);
              }}
              className="px-3 py-1.5 text-xs font-semibold rounded-xl bg-white text-[#182C25] border border-[#E3EBE5] hover:border-[#119B72] hover:bg-[#EDF8F1] transition-colors"
            >
              {tp.label}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Controls Column (4 Cols) */}
        <div className="lg:col-span-4 space-y-5">
          <div className="bg-white rounded-2xl border border-[#E3EBE5] p-5 shadow-xs">
            <h3 className="text-xs font-bold text-[#182C25] uppercase tracking-wider mb-4 flex items-center gap-2">
              <Navigation className="w-4 h-4 text-[#119B72]" />
              <span>Routing Search Parameters</span>
            </h3>

            <form onSubmit={handleRoute} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-[#182C25] mb-1">Start Node ID (Pune)</label>
                <input
                  type="number"
                  value={startNode}
                  onChange={(e) => setStartNode(parseInt(e.target.value, 10) || 0)}
                  required
                  className="w-full px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-mono text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#182C25] mb-1">Target Node ID (Pune)</label>
                <input
                  type="number"
                  value={targetNode}
                  onChange={(e) => setTargetNode(parseInt(e.target.value, 10) || 0)}
                  required
                  className="w-full px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-mono text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-[#182C25] mb-1">Search Algorithm</label>
                <select
                  value={algorithm}
                  onChange={(e) => setAlgorithm(e.target.value as any)}
                  className="w-full px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs font-semibold text-[#182C25] focus:bg-white focus:border-[#119B72] outline-none"
                >
                  <option value="A*">A* (Distance-Optimal Heuristic)</option>
                  <option value="Bidirectional">Bidirectional BFS (Hop-Optimal, Fast)</option>
                  <option value="BFS">Breadth-First Search (Hop Benchmark)</option>
                  <option value="Greedy_Best_First">Greedy Best-First (Heuristic)</option>
                  <option value="IDDFS">IDDFS (Iterative Deepening)</option>
                  <option value="DFS">Depth-First Search</option>
                </select>
              </div>

              {algorithm === 'IDDFS' && (
                <div>
                  <label className="block text-xs font-bold text-[#182C25] mb-1">Max Depth Bound</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={maxDepth}
                    onChange={(e) => setMaxDepth(parseInt(e.target.value, 10) || 25)}
                    className="w-full px-3 py-2 rounded-xl border border-[#E3EBE5] bg-[#F8FAF7] text-xs"
                  />
                  <p className="text-[10px] text-[#718078] mt-0.5">Exploration terminates if destination exceeds depth bound.</p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-3 px-4 rounded-xl bg-[#119B72] hover:bg-[#0E8360] text-white font-bold text-xs sm:text-sm transition-all shadow-md shadow-[#119B72]/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Searching Pune Road Graph...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4" />
                    <span>Calculate Road Route</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* District Scope Reminder */}
          <div className="p-4 rounded-2xl bg-[#EDF8F1] border border-[#D9F2E6] text-xs text-[#073B32] space-y-1">
            <p className="font-bold flex items-center gap-1.5 text-[#073B32]">
              <ShieldAlert className="w-4 h-4 text-[#119B72]" />
              <span>Pune District Scope Restriction</span>
            </p>
            <p className="leading-relaxed text-[#073B32]/85">
              The road network graph strictly covers Pune District (170,253 nodes). Graph calculations outside Pune district boundaries are rejected by the coordinate boundary guard.
            </p>
          </div>
        </div>

        {/* Map & Route Stats Column (8 Cols) */}
        <div className="lg:col-span-8 space-y-5">
          {error && (
            <div className="p-4 rounded-2xl bg-[#FDF2F2] border border-[#FAD2D2] text-[#E45B55] flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-[#E45B55] mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-bold">Routing Error</p>
                <p className="text-xs mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {/* Map Preview */}
          <div className="bg-white rounded-2xl border border-[#E3EBE5] p-4 shadow-xs">
            <div className="h-[400px] rounded-xl overflow-hidden border border-[#E3EBE5]">
              <div ref={mapContainerRef} className="w-full h-full" />
            </div>
          </div>

          {/* Route Result Statistics Card */}
          {response && response.success && (
            <div className="bg-[#073B32] text-white p-6 rounded-2xl border border-[#0B4F43] shadow-xs space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-[#0B4F43]">
                <div>
                  <span className="text-xs font-bold text-[#D9F2E6] uppercase tracking-wider">
                    {response.algorithm} Path Result Verified
                  </span>
                  <p className="text-xs text-[#D9F2E6]/70 mt-0.5">
                    Start #{response.start_node_id} &rarr; Target #{response.target_node_id}
                  </p>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-[#D9F2E6] bg-[#0B4F43] px-3 py-1.5 rounded-xl border border-[#119B72]/30">
                  <Clock className="w-3.5 h-3.5 text-[#119B72]" />
                  <span>{response.execution_time_ms} ms</span>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                <div className="p-3 rounded-xl bg-[#0B4F43]/80 border border-[#119B72]/20">
                  <span className="text-[10px] text-[#D9F2E6]/70 uppercase">Total Road Distance</span>
                  <p className="text-xl font-extrabold text-white mt-0.5">
                    {response.total_distance_m} m
                  </p>
                  <p className="text-[11px] text-[#D9F2E6]/75">({response.total_distance_km} km)</p>
                </div>

                <div className="p-3 rounded-xl bg-[#0B4F43]/80 border border-[#119B72]/20">
                  <span className="text-[10px] text-[#D9F2E6]/70 uppercase">Edge Hops</span>
                  <p className="text-xl font-extrabold text-[#119B72] mt-0.5">
                    {response.edge_count}
                  </p>
                  <p className="text-[11px] text-[#D9F2E6]/75">Road segments traversed</p>
                </div>

                <div className="p-3 rounded-xl bg-[#0B4F43]/80 border border-[#119B72]/20 col-span-2 sm:col-span-1">
                  <span className="text-[10px] text-[#D9F2E6]/70 uppercase">Expanded Graph Nodes</span>
                  <p className="text-xl font-extrabold text-[#D9F2E6] mt-0.5">
                    {response.expanded_nodes}
                  </p>
                  <p className="text-[11px] text-[#D9F2E6]/75">Search state space</p>
                </div>
              </div>

              {response.route_node_ids && response.route_node_ids.length > 0 && (
                <div className="p-3 rounded-xl bg-[#0B4F43] border border-[#119B72]/20 text-xs">
                  <span className="text-[10px] text-[#D9F2E6]/70 uppercase block mb-1">
                    Node Sequence ({response.route_node_ids.length} nodes)
                  </span>
                  <p className="font-mono text-[11px] text-[#D9F2E6] break-all leading-relaxed">
                    {response.route_node_ids.slice(0, 5).join(' → ')}
                    {response.route_node_ids.length > 7 ? ' → ... → ' : ' → '}
                    {response.route_node_ids.slice(-2).join(' → ')}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
