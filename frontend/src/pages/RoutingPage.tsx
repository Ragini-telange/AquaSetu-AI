import React, { useState, useEffect, useRef } from 'react';
import { Navigation, AlertCircle, Zap, CheckCircle2, ShieldAlert } from 'lucide-react';
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
    { label: 'Pair 1: Sarati Local Village Hop', src: 12788595845, dst: 12788595830, desc: 'Local hop demonstrating A* alley shortcut' },
    { label: 'Pair 2: Bhor Town Route', src: 1849234040, dst: 2542090919, desc: 'Town-level arterial route' },
    { label: 'Pair 3: Sakurde to Belsar', src: 5983616771, dst: 5378450158, desc: 'Inter-village route in Purandhar' },
  ];

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    // Center on Pune District
    const map = L.map(mapContainerRef.current).setView([18.5204, 73.8567], 10);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 18,
    }).addTo(map);

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

      // Draw Route Polyline
      const polyline = L.polyline(latLngs, {
        color: '#0284c7',
        weight: 5,
        opacity: 0.85,
        lineCap: 'round',
        lineJoin: 'round',
      });
      layer.addLayer(polyline);

      // Start Pin (Green)
      const startCoord = latLngs[0];
      const startMarker = L.marker(startCoord, { icon: createCustomPin('green') })
        .bindPopup(`<strong>Start Node:</strong> #${response.start_node_id}`);
      layer.addLayer(startMarker);

      // End Pin (Red)
      const endCoord = latLngs[latLngs.length - 1];
      const endMarker = L.marker(endCoord, { icon: createCustomPin('red') })
        .bindPopup(`<strong>Target Node:</strong> #${response.target_node_id}`);
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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-slate-200 pb-5">
        <div>
          <div className="flex items-center gap-2 text-indigo-600 font-semibold text-xs tracking-wider uppercase">
            <Navigation className="w-4 h-4" />
            <span>Vedangi &bull; Pune Road Network Routing</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 mt-1">
            Pune Road Graph Pathfinding
          </h1>
          <p className="text-slate-500 text-sm mt-1">
            Executes 6 graph search algorithms on the 170,253-node directed OSM road network of Pune District.
          </p>
        </div>

        {/* Test Pairs Presets */}
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-semibold text-slate-400">Audit Pairs:</span>
          {testPairs.map((tp) => (
            <button
              key={tp.label}
              onClick={() => {
                setStartNode(tp.src);
                setTargetNode(tp.dst);
              }}
              className="px-2.5 py-1 text-xs font-medium rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200 hover:bg-indigo-100 transition-colors"
            >
              {tp.label.split(':')[0]}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Controls Column */}
        <div className="lg:col-span-4 space-y-5">
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-4">
              Routing Parameters
            </h3>

            <form onSubmit={handleRoute} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Start Node ID (Pune)</label>
                <input
                  type="number"
                  value={startNode}
                  onChange={(e) => setStartNode(parseInt(e.target.value, 10) || 0)}
                  required
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm font-mono focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Target Node ID (Pune)</label>
                <input
                  type="number"
                  value={targetNode}
                  onChange={(e) => setTargetNode(parseInt(e.target.value, 10) || 0)}
                  required
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm font-mono focus:ring-2 focus:ring-indigo-500 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Search Algorithm</label>
                <select
                  value={algorithm}
                  onChange={(e) => setAlgorithm(e.target.value as any)}
                  className="w-full px-3 py-2 rounded-lg border border-slate-300 text-sm font-semibold focus:ring-2 focus:ring-indigo-500 outline-none"
                >
                  <option value="A*">A* (Shortest Road Distance - Optimal)</option>
                  <option value="Bidirectional">Bidirectional BFS (Hop-Optimal, Fast)</option>
                  <option value="BFS">BFS (Hop-Optimal Benchmark)</option>
                  <option value="Greedy_Best_First">Greedy Best-First (Heuristic)</option>
                  <option value="IDDFS">IDDFS (Iterative Deepening)</option>
                  <option value="DFS">DFS (Depth-First Search)</option>
                </select>
              </div>

              {algorithm === 'IDDFS' && (
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Max Depth Bound</label>
                  <input
                    type="number"
                    min="1"
                    max="100"
                    value={maxDepth}
                    onChange={(e) => setMaxDepth(parseInt(e.target.value, 10) || 25)}
                    className="w-full px-3 py-1.5 rounded-lg border border-slate-300 text-sm"
                  />
                  <p className="text-[10px] text-slate-400 mt-0.5">Fails if destination exceeds depth bound.</p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full mt-2 py-2.5 px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm transition-all shadow-md shadow-indigo-600/20 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Searching Pune Road Graph...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4" />
                    <span>Find Road Route</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* District Scope Reminder */}
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-800 space-y-1">
            <p className="font-bold flex items-center gap-1.5 text-amber-900">
              <ShieldAlert className="w-4 h-4 text-amber-700" />
              <span>Pune District Scope Restriction</span>
            </p>
            <p>
              The OpenStreetMap road graph covers only Pune District (170,253 nodes). Nodes or coordinates outside
              Pune are rejected by the boundary guard.
            </p>
          </div>
        </div>

        {/* Map & Route Stats Column */}
        <div className="lg:col-span-8 space-y-5">
          {error && (
            <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-rose-500 mt-0.5 shrink-0" />
              <div>
                <p className="text-sm font-bold">Routing Error</p>
                <p className="text-xs mt-0.5">{error}</p>
              </div>
            </div>
          )}

          {/* Leaflet Map Card */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
            <div className="flex items-center justify-between mb-3 text-xs">
              <div className="flex items-center gap-4">
                <span className="font-bold text-slate-700">Pune OSM Road Geometry</span>
                <span className="flex items-center gap-1.5 text-slate-500">
                  <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Start Node
                </span>
                <span className="flex items-center gap-1.5 text-slate-500">
                  <span className="w-2.5 h-2.5 rounded-full bg-rose-500" /> Destination
                </span>
              </div>
              {response?.success && (
                <span className="text-emerald-600 font-semibold text-[11px] flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Route Computed in {response.execution_time_ms} ms
                </span>
              )}
            </div>

            <div 
              ref={mapContainerRef} 
              className="h-[380px] w-full rounded-lg border border-slate-200"
            />
          </div>

          {/* Route Performance Card */}
          {response && response.success && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-[11px] text-slate-400 uppercase font-bold">Total Road Distance</p>
                  <p className="text-lg font-bold text-slate-900 mt-0.5">
                    {response.total_distance_m !== null && response.total_distance_m !== undefined ? `${response.total_distance_m.toFixed(2)} m` : 'N/A'}
                  </p>
                  <p className="text-[10px] text-slate-400">({response.total_distance_km} km)</p>
                </div>

                <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-[11px] text-slate-400 uppercase font-bold">Edge / Hop Count</p>
                  <p className="text-lg font-bold text-slate-900 mt-0.5">{response.edge_count} edges</p>
                  <p className="text-[10px] text-slate-400">Road segments traversed</p>
                </div>

                <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-[11px] text-slate-400 uppercase font-bold">Expanded Nodes</p>
                  <p className="text-lg font-bold text-slate-900 mt-0.5">{response.expanded_nodes}</p>
                  <p className="text-[10px] text-slate-400">Search frontier size</p>
                </div>

                <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                  <p className="text-[11px] text-slate-400 uppercase font-bold">Latency</p>
                  <p className="text-lg font-bold text-emerald-600 mt-0.5">{response.execution_time_ms} ms</p>
                  <p className="text-[10px] text-slate-400">Algorithm: {response.algorithm}</p>
                </div>
              </div>

              {/* Algorithmic Insight Callout */}
              <div className="p-3.5 bg-cyan-50 rounded-lg border border-cyan-200 text-xs text-cyan-900 leading-relaxed">
                <strong>Algorithmic Behavior Note:</strong>{' '}
                {response.algorithm === 'A*' && (
                  <span>
                    A* evaluates f(n) = g(n) + h(n) to minimize accumulated weighted road length. On Pair 1,
                    it bypasses a direct 127 m road segment to take a 3-segment alley saving 10.59 m (227.06 m vs. BFS 237.65 m).
                  </span>
                )}
                {response.algorithm === 'Bidirectional' && (
                  <span>
                    Bidirectional Search expands simultaneously from both start and target while respecting one-way edges.
                    It matches the minimal hop count of BFS while drastically reducing expanded nodes by ~77%.
                  </span>
                )}
                {response.algorithm === 'BFS' && (
                  <span>
                    BFS explores nodes layer by layer, guaranteeing the minimum number of road segments/hops,
                    regardless of individual segment lengths.
                  </span>
                )}
                {response.algorithm === 'Greedy_Best_First' && (
                  <span>
                    Greedy Best-First Search aggressively pursues the straight-line Euclidean distance heuristic h(n),
                    yielding rapid exploration with low expansion counts.
                  </span>
                )}
                {response.algorithm === 'IDDFS' && (
                  <span>
                    Iterative Deepening operates within the configured max depth bound ({maxDepth}), combining DFS's
                    space efficiency with iterative BFS completeness.
                  </span>
                )}
                {response.algorithm === 'DFS' && (
                  <span>
                    Unguided Depth-First Search traverses branches deeply without edge weighting, resulting in higher
                    distance variance on road topologies.
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
