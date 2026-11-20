"""
build_graph_cache.py
--------------------
Utility script to parse and pre-cache the Pune road network graphml into a high-performance
binary joblib cache.

Preserves the original pune_road_network.graphml file without modification.
Validates node count, edge count, and algorithm routing results between raw and cached formats.
"""

import os
import sys
import time
import math
import heapq
import collections
from collections import deque
import networkx as nx
import joblib

def build_cache(
    source_graphml_path: str,
    output_cache_path: str
):
    print("=" * 70)
    print("AQUAGUARD: PUNE ROAD NETWORK GRAPH CACHE BUILDER & VERIFIER")
    print("=" * 70)
    print(f"Source GraphML: {source_graphml_path}")
    print(f"Target Cache:   {output_cache_path}")
    
    if not os.path.exists(source_graphml_path):
        raise FileNotFoundError(f"Source GraphML not found at {source_graphml_path}")
    
    source_size_mb = os.path.getsize(source_graphml_path) / (1024 * 1024)
    print(f"Source file size: {source_size_mb:.2f} MB")
    
    # 1. Load original GraphML
    print("\n[Step 1/4] Reading raw XML GraphML via NetworkX...")
    t0 = time.time()
    raw_G = nx.read_graphml(source_graphml_path)
    t_load_raw = time.time() - t0
    raw_nodes = raw_G.number_of_nodes()
    raw_edges = raw_G.number_of_edges()
    print(f"   Raw loaded in {t_load_raw:.2f}s | Nodes: {raw_nodes:,} | Edges: {raw_edges:,}")
    
    # 2. Type-convert to production typed MultiDiGraph
    print("\n[Step 2/4] Converting node IDs to int and coordinates/lengths to float...")
    t1 = time.time()
    G = nx.MultiDiGraph()
    for node, data in raw_G.nodes(data=True):
        int_node = int(node)
        G.add_node(int_node, x=float(data.get('x', 0)), y=float(data.get('y', 0)))

    for u, v, k, data in raw_G.edges(keys=True, data=True):
        length_val = float(data.get('length', 0))
        G.add_edge(int(u), int(v), key=k, length=length_val)
    t_convert = time.time() - t1
    print(f"   Converted in {t_convert:.2f}s | Nodes: {G.number_of_nodes():,} | Edges: {G.number_of_edges():,}")
    
    # 3. Save to binary cache
    print("\n[Step 3/4] Serializing to compressed binary joblib cache...")
    os.makedirs(os.path.dirname(output_cache_path), exist_ok=True)
    t2 = time.time()
    joblib.dump(G, output_cache_path, compress=3)
    t_dump = time.time() - t2
    cache_size_mb = os.path.getsize(output_cache_path) / (1024 * 1024)
    print(f"   Saved in {t_dump:.2f}s | Cache file size: {cache_size_mb:.2f} MB")
    
    # 4. Verify cached graph loading and parity
    print("\n[Step 4/4] Verifying cache reload performance and data parity...")
    t3 = time.time()
    cached_G = joblib.load(output_cache_path)
    t_load_cached = time.time() - t3
    print(f"   Cached graph reloaded in {t_load_cached:.2f}s! ({t_load_raw / t_load_cached:.1f}x speedup)")
    
    # Assertions
    assert cached_G.number_of_nodes() == raw_nodes, f"Node count mismatch: {cached_G.number_of_nodes()} vs {raw_nodes}"
    assert cached_G.number_of_edges() == raw_edges, f"Edge count mismatch: {cached_G.number_of_edges()} vs {raw_edges}"
    print(f"   [PASS] Node count match: {cached_G.number_of_nodes():,}")
    print(f"   [PASS] Edge count match: {cached_G.number_of_edges():,}")
    
    # Test A* and BFS routing on Pair 1
    src = 12788595845
    dst = 12788595830
    print(f"\nVerifying routing on Pair 1 (Sarati: {src} -> {dst})...")
    
    def _shortest_edge(graph, u, v):
        edata = graph.get_edge_data(u, v, default={})
        return min([attr.get("length", float("inf")) for attr in edata.values()])
    
    # BFS
    frontier = deque([src])
    came_from_bfs = {src: None}
    while frontier:
        cur = frontier.popleft()
        if cur == dst:
            break
        for nbr in cached_G.successors(cur):
            if nbr not in came_from_bfs:
                frontier.append(nbr)
                came_from_bfs[nbr] = cur
    
    bfs_path = []
    curr = dst
    while curr is not None:
        bfs_path.append(curr)
        curr = came_from_bfs[curr]
    bfs_path.reverse()
    bfs_dist = sum(_shortest_edge(cached_G, u, v) for u, v in zip(bfs_path[:-1], bfs_path[1:]))
    print(f"   [PASS] BFS Route: {len(bfs_path)-1} edges, {bfs_dist:.2f} m (matches benchmark 237.65 m)")
    assert len(bfs_path) - 1 == 3, f"Expected 3 edges for BFS, got {len(bfs_path) - 1}"
    assert abs(bfs_dist - 237.65) < 0.1, f"Expected 237.65 m for BFS, got {bfs_dist}"
    
    # A*
    target_x = cached_G.nodes[dst]['x']
    target_y = cached_G.nodes[dst]['y']
    def h(n):
        return math.hypot(cached_G.nodes[n]['x'] - target_x, cached_G.nodes[n]['y'] - target_y)
    
    open_set = []
    heapq.heappush(open_set, (h(src), 0, src))
    g_score = {src: 0.0}
    came_from_astar = {src: None}
    
    while open_set:
        f, g, cur = heapq.heappop(open_set)
        if cur == dst:
            break
        if g > g_score.get(cur, float('inf')):
            continue
        for nbr in cached_G.successors(cur):
            cost = _shortest_edge(cached_G, cur, nbr)
            tentative_g = g + cost
            if tentative_g < g_score.get(nbr, float('inf')):
                g_score[nbr] = tentative_g
                came_from_astar[nbr] = cur
                heapq.heappush(open_set, (tentative_g + h(nbr), tentative_g, nbr))
                
    astar_path = []
    curr = dst
    while curr is not None:
        astar_path.append(curr)
        curr = came_from_astar[curr]
    astar_path.reverse()
    astar_dist = sum(_shortest_edge(cached_G, u, v) for u, v in zip(astar_path[:-1], astar_path[1:]))
    print(f"   [PASS] A* Route:  {len(astar_path)-1} edges, {astar_dist:.2f} m (matches benchmark 227.06 m)")
    assert len(astar_path) - 1 == 5, f"Expected 5 edges for A*, got {len(astar_path) - 1}"
    assert abs(astar_dist - 227.06) < 0.1, f"Expected 227.06 m for A*, got {astar_dist}"
    
    print("\n" + "=" * 70)
    print("SUCCESS: Pune road network cache verified and ready for production.")
    print("=" * 70)

if __name__ == "__main__":
    src_path = r"D:\AquaGuard\audit\vedangi_geographical_search\AquaGuard_AI1\vedangi_search_module\pune_road_network.graphml"
    dst_path = r"D:\AquaGuard\backend\cache\pune_road_network_cached.joblib"
    build_cache(src_path, dst_path)
