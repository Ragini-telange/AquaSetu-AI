import sys
import os
import json
import math
import heapq
import collections
from collections import deque
import pandas as pd
import networkx as nx

module_path = os.path.abspath('vedangi_search_module')
if module_path not in sys.path:
    sys.path.insert(0, module_path)

from bfs_search import bfs_route, _load_graph, _load_snap_csv, _shortest_edge_length

print("Loading Pune Road Network...")
G = _load_graph()
print(f"Graph loaded: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Load algorithm implementations from notebook
nb_path = os.path.join(module_path, 'AI_Search_Algorithms.ipynb')
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

ns = {
    'nx': nx,
    'time': sys.modules['time'],
    'math': math,
    'heapq': heapq,
    'collections': collections,
    'deque': deque,
    'G': G,
    '_shortest_edge_length': _shortest_edge_length,
    'bfs_route': bfs_route,
}

for idx in [8, 14, 20, 26, 30]:
    code = ''.join(nb['cells'][idx]['source'])
    exec(code, ns)

dfs_route = ns['dfs_route']
greedy_best_first_route = ns['greedy_best_first_route']
astar_route = ns['astar_route']
iddfs_route = ns['iddfs_route']
bidirectional_route = ns['bidirectional_route']

test_pairs = [
    {
        "pair_id": "Pair 1",
        "description": "Sarati to Sarati (Local village hop)",
        "src_node": 12788595845,
        "dst_node": 12788595830,
    },
    {
        "pair_id": "Pair 2",
        "description": "Bhor to Bhor (Town-level short route)",
        "src_node": 1849234040,
        "dst_node": 2542090919,
    },
    {
        "pair_id": "Pair 3",
        "description": "Sakurde to Belsar (Inter-village Purandhar)",
        "src_node": 5983616771,
        "dst_node": 5378450158,
    },
    {
        "pair_id": "Pair 4",
        "description": "Loni Bhapkar to Morgaon (Baramati sub-district route)",
        "src_node": 12785555719,
        "dst_node": 5622278692,
    },
    {
        "pair_id": "Pair 5",
        "description": "Sarati to Bawada (Cross-village Indapur corridor)",
        "src_node": 12788595845,
        "dst_node": 2125144688,
    }
]

algorithms = [
    ("BFS", lambda s, d: bfs_route(s, d, G=G)),
    ("DFS", lambda s, d: dfs_route(s, d, G=G)),
    ("Greedy Best-First", lambda s, d: greedy_best_first_route(s, d, G=G)),
    ("A*", lambda s, d: astar_route(s, d, G=G)),
    ("IDDFS", lambda s, d: iddfs_route(s, d, G=G, max_depth=25)),
    ("Bidirectional Search", lambda s, d: bidirectional_route(s, d, G=G))
]

audit_log = []

def log(msg=""):
    print(msg)
    audit_log.append(msg)

log("================================================================================")
log("AQUAGUARD AI: SEARCH ALGORITHMS BENCHMARK AUDIT REPORT")
log("================================================================================")

# 1 & 2: Audit route validity and distance recalculation
log("\n--- SECTION 1 & 2: ROUTE VALIDITY AND INDEPENDENT DISTANCE VERIFICATION ---")

all_routes_valid = True
discrepancies_found = 0

for p in test_pairs:
    pid = p['pair_id']
    desc = p['description']
    src = p['src_node']
    dst = p['dst_node']
    log(f"\nAuditing {pid}: {desc} ({src} -> {dst})")
    
    for alg_name, alg_fn in algorithms:
        res = alg_fn(src, dst)
        success = res.get('success', False)
        route = res.get('route', [])
        rep_dist = res.get('distance_m', 0.0)
        rep_edges = res.get('edge_count', 0)
        
        if not success:
            log(f"  [{alg_name:20s}] Route status: FAILED (No route returned)")
            continue
            
        # Verify directed edges
        edges_valid = True
        missing_edges = []
        independent_dist = 0.0
        
        for u, v in zip(route[:-1], route[1:]):
            if not G.has_edge(u, v):
                edges_valid = False
                missing_edges.append((u, v))
            else:
                independent_dist += _shortest_edge_length(G, u, v)
                
        num_edges = len(route) - 1
        dist_diff = abs(independent_dist - (rep_dist if rep_dist is not None else 0.0))
        
        if not edges_valid:
            all_routes_valid = False
            log(f"  [{alg_name:20s}] CRITICAL ERROR: Route contains invalid directed edges: {missing_edges[:3]}")
        elif dist_diff > 1e-4:
            discrepancies_found += 1
            log(f"  [{alg_name:20s}] DISCREPANCY: Reported dist={rep_dist:.4f}m vs Independent dist={independent_dist:.4f}m")
        else:
            log(f"  [{alg_name:20s}] OK | Directed edges: 100% valid | Edges: {num_edges} (reported: {rep_edges}) | Dist: {independent_dist:.2f} m (reported: {rep_dist:.2f} m)")

# 3: Deep check of A* vs BFS on Pair 1
log("\n--- SECTION 3: AUDIT OF A* IMPLEMENTATION & PAIR 1 DISTANCE MINIMIZATION ---")
s1, d1 = test_pairs[0]['src_node'], test_pairs[0]['dst_node']
bfs_res1 = bfs_route(s1, d1, G=G)
astar_res1 = astar_route(s1, d1, G=G)
nx_shortest_dist = nx.shortest_path_length(G, s1, d1, weight='length')
nx_shortest_path = nx.shortest_path(G, s1, d1, weight='length')
nx_min_hop_path = nx.shortest_path(G, s1, d1)

log(f"Pair 1 Nodes: Start={s1}, Target={d1}")
log(f"NetworkX Dijkstra shortest road distance: {nx_shortest_dist:.4f} m (Path: {nx_shortest_path})")
log(f"A* reported route distance:               {astar_res1['distance_m']:.4f} m (Path: {astar_res1['route']})")
log(f"BFS reported route distance:              {bfs_res1['distance_m']:.4f} m (Path: {bfs_res1['route']})")
log(f"NetworkX minimum-hop path:                {nx_min_hop_path} ({len(nx_min_hop_path)-1} edges)")

log("\nDetailed Edge Breakdown for Pair 1:")
log("  A* Route (5 edges):")
for u, v in zip(astar_res1['route'][:-1], astar_res1['route'][1:]):
    log(f"    Edge ({u} -> {v}): length = {_shortest_edge_length(G, u, v):.2f} m")
log(f"    Total A* distance: {sum(_shortest_edge_length(G, u, v) for u, v in zip(astar_res1['route'][:-1], astar_res1['route'][1:])):.2f} m")

log("  BFS Route (3 edges):")
for u, v in zip(bfs_res1['route'][:-1], bfs_res1['route'][1:]):
    log(f"    Edge ({u} -> {v}): length = {_shortest_edge_length(G, u, v):.2f} m")
log(f"    Total BFS distance: {sum(_shortest_edge_length(G, u, v) for u, v in zip(bfs_res1['route'][:-1], bfs_res1['route'][1:])):.2f} m")

# 4: Check Bidirectional Search minimum-edge route
log("\n--- SECTION 4: AUDIT OF BIDIRECTIONAL SEARCH ON DIRECTED GRAPH ---")
bidi_min_edge_match = True
for p in test_pairs:
    pid = p['pair_id']
    src, dst = p['src_node'], p['dst_node']
    bidi_res = bidirectional_route(src, dst, G=G)
    bfs_res = bfs_route(src, dst, G=G)
    bidi_edges = bidi_res['edge_count']
    bfs_edges = bfs_res['edge_count']
    log(f"{pid}: Bidirectional edges = {bidi_edges} | BFS edges = {bfs_edges} | Match: {bidi_edges == bfs_edges}")
    if bidi_edges != bfs_edges:
        bidi_min_edge_match = False

# 5: IDDFS Pair 5 Depth Analysis
log("\n--- SECTION 5: IDDFS PAIR 5 FAILURE AUDIT & MINIMUM DEPTH DETERMINATION ---")
s5, d5 = test_pairs[4]['src_node'], test_pairs[4]['dst_node']
nx_hop_len5 = nx.shortest_path_length(G, s5, d5)
log(f"NetworkX minimum hop count between Pair 5 nodes: {nx_hop_len5} edges")

log("Testing IDDFS with incremental depths...")
found_depth = None
for test_depth in [20, 25, 26, 27, 28, 29, 30, 35, 40]:
    t_start = sys.modules['time'].time()
    iddfs_test = iddfs_route(s5, d5, G=G, max_depth=test_depth)
    elapsed = sys.modules['time'].time() - t_start
    log(f"  IDDFS max_depth={test_depth:2d} -> Success: {iddfs_test['success']} | Expanded: {iddfs_test['expanded_nodes']:5d} | Time: {elapsed:.4f}s")
    if iddfs_test['success'] and found_depth is None:
        found_depth = test_depth
        break

# 6: Check summary CSV averages
log("\n--- SECTION 6: CSV SUMMARY AVERAGES AUDIT ---")
df_comp = pd.read_csv(os.path.join(module_path, 'outputs', 'search_algorithms_comparison.csv'))
log("Current summary calculation in run_benchmark.py used df_res.groupby('algorithm').mean()")
log("Notice for IDDFS: distance_m for Pair 5 was recorded as 0.0 on failure.")
iddfs_all = df_comp[df_comp['algorithm'] == 'IDDFS']
log(f"Raw IDDFS distances across 5 pairs: {iddfs_all['distance_m'].tolist()}")
raw_mean_dist = iddfs_all['distance_m'].mean()
succ_mean_dist = iddfs_all[iddfs_all['success'] == True]['distance_m'].mean()
log(f"Mean including 0.0 (raw groupby): {raw_mean_dist:.2f} m")
log(f"Mean of SUCCESSFUL routes only:   {succ_mean_dist:.2f} m")

# Write out full report
report_path = os.path.join(module_path, 'outputs', 'benchmark_audit.txt')
with open(report_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(audit_log))

print(f"\nAudit completed. Report saved to: {report_path}")
