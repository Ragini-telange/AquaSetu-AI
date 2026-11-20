import sys
import os
import time
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

# Extract algorithm functions from AI_Search_Algorithms.ipynb to ensure 100% exact reuse
nb_path = os.path.join(module_path, 'AI_Search_Algorithms.ipynb')
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

from bfs_search import bfs_route, _load_graph, _load_snap_csv, _shortest_edge_length

print("Loading Pune Road Network...")
t0 = time.time()
G = _load_graph()
print(f"Graph loaded in {time.time() - t0:.2f}s: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Load implementations into namespace with all necessary modules
ns = {
    'nx': nx,
    'time': time,
    'math': math,
    'heapq': heapq,
    'collections': collections,
    'deque': deque,
    'G': G,
    '_shortest_edge_length': _shortest_edge_length,
    'bfs_route': bfs_route,
}

# Execute relevant algorithm cells from notebook
for idx in [8, 14, 20, 26, 30]:
    code = ''.join(nb['cells'][idx]['source'])
    exec(code, ns)

dfs_route = ns['dfs_route']
greedy_best_first_route = ns['greedy_best_first_route']
astar_route = ns['astar_route']
iddfs_route = ns['iddfs_route']
bidirectional_route = ns['bidirectional_route']

# 5 Chosen Pairs
test_pairs = [
    {
        "pair_id": "Pair 1",
        "description": "Sarati to Sarati (Local village hop)",
        "src_node": 12788595845,
        "dst_node": 12788595830,
        "src_village": "Sarati",
        "dst_village": "Sarati",
        "src_block": "INDAPUR",
        "dst_block": "INDAPUR"
    },
    {
        "pair_id": "Pair 2",
        "description": "Bhor to Bhor (Town-level short route)",
        "src_node": 1849234040,
        "dst_node": 2542090919,
        "src_village": "Bhor",
        "dst_village": "Bhor",
        "src_block": "BHOR",
        "dst_block": "BHOR"
    },
    {
        "pair_id": "Pair 3",
        "description": "Sakurde to Belsar (Inter-village Purandhar)",
        "src_node": 5983616771,
        "dst_node": 5378450158,
        "src_village": "Sakurde",
        "dst_village": "Belsar",
        "src_block": "PURANDHAR",
        "dst_block": "PURANDHAR"
    },
    {
        "pair_id": "Pair 4",
        "description": "Loni Bhapkar to Morgaon (Baramati sub-district route)",
        "src_node": 12785555719,
        "dst_node": 5622278692,
        "src_village": "Loni Bhapkar",
        "dst_village": "Morgaon",
        "src_block": "BARAMATI",
        "dst_block": "BARAMATI"
    },
    {
        "pair_id": "Pair 5",
        "description": "Sarati to Bawada (Cross-village Indapur corridor)",
        "src_node": 12788595845,
        "dst_node": 2125144688,
        "src_village": "Sarati",
        "dst_village": "Bawada",
        "src_block": "INDAPUR",
        "dst_block": "INDAPUR"
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

results = []
print("\n" + "="*80)
print("STARTING SEARCH ALGORITHMS BENCHMARK")
print("="*80)

for p in test_pairs:
    p_id = p["pair_id"]
    desc = p["description"]
    src = p["src_node"]
    dst = p["dst_node"]
    print(f"\n--- Testing {p_id}: {desc} ({src} -> {dst}) ---")
    
    for alg_name, alg_fn in algorithms:
        print(f"  Running {alg_name:20s} ... ", end="", flush=True)
        res = alg_fn(src, dst)
        success = res.get('success', False)
        dist = res.get('distance_m', None)
        edges = res.get('edge_count', None)
        expanded = res.get('expanded_nodes', 0)
        time_s = res.get('time_s', 0.0)
        
        print(f"Success: {success} | Distance: {dist if dist is not None else 'N/A'} m | Edges: {edges} | Expanded: {expanded} | Time: {time_s:.5f} s")
        
        results.append({
            "pair_id": p_id,
            "description": desc,
            "src_node": src,
            "dst_node": dst,
            "src_village": p["src_village"],
            "dst_village": p["dst_village"],
            "src_block": p["src_block"],
            "dst_block": p["dst_block"],
            "algorithm": alg_name,
            "success": success,
            "distance_m": round(dist, 2) if dist is not None else None,
            "edge_count": edges,
            "expanded_nodes": expanded,
            "time_s": round(time_s, 6)
        })

df_res = pd.DataFrame(results)

# Save to outputs directory
output_csv = os.path.join(module_path, 'outputs', 'search_algorithms_comparison.csv')
df_res.to_csv(output_csv, index=False)
print(f"\nDetailed comparison results saved to: {output_csv}")

# Summary Table
print("\n" + "="*80)
print("SUMMARY TABLE (Average Across 5 Pairs)")
print("="*80)
summary = df_res.groupby('algorithm').agg({
    'success': lambda x: f"{sum(x)}/{len(x)}",
    'distance_m': 'mean',
    'edge_count': 'mean',
    'expanded_nodes': 'mean',
    'time_s': 'mean'
}).reset_index()

summary.rename(columns={
    'algorithm': 'Algorithm',
    'success': 'Success Rate',
    'distance_m': 'Avg Distance (m)',
    'edge_count': 'Avg Edges',
    'expanded_nodes': 'Avg Expanded Nodes',
    'time_s': 'Avg Time (s)'
}, inplace=True)

# Custom sort order
order = ["BFS", "DFS", "Greedy Best-First", "A*", "IDDFS", "Bidirectional Search"]
summary['sort_key'] = summary['Algorithm'].map(lambda x: order.index(x) if x in order else 99)
summary = summary.sort_values('sort_key').drop(columns=['sort_key'])

print(summary.to_string(index=False))

summary_csv = os.path.join(module_path, 'outputs', 'search_algorithms_summary.csv')
summary.to_csv(summary_csv, index=False)
print(f"Summary table saved to: {summary_csv}")
