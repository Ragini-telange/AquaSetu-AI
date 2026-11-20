import sys
import os
import json
import pandas as pd
import networkx as nx

module_path = os.path.abspath('vedangi_search_module')
if module_path not in sys.path:
    sys.path.insert(0, module_path)

from bfs_search import _load_graph, _load_snap_csv

G = _load_graph()
snap_df = _load_snap_csv()
matched = snap_df[snap_df['match_status'] == 'Matched']

# We want 5 pairs with varied sources and destinations:
# E.g.
# Pair 1: Very short (Sarati to Sarati - same village)
# Pair 2: Short (Sarati to Bawada - neighboring villages in Indapur)
# Pair 3: Medium-short
# Let's test pairs between different villages
candidates = [
    # (src_idx, dst_idx)
    (0, 1), # Sarati -> Sarati
    (0, 2), # Sarati -> Bawada (hops ~19)
    (14, 17), # Indapur -> Indapur
    (5, 6), # Sangavi -> Sangavi
    (2, 14), # Bawada -> Indapur
    (14, 11), # Indapur -> Anthurne
    (11, 7), # Anthurne -> Tawashi
]

results = []
for i1, i2 in candidates:
    u = int(matched.iloc[i1]['nearest_node_id'])
    v = int(matched.iloc[i2]['nearest_node_id'])
    if nx.has_path(G, u, v):
        hops = nx.shortest_path_length(G, u, v)
        dist = nx.shortest_path_length(G, u, v, weight='length')
        results.append({
            'src_id': u,
            'dst_id': v,
            'src_village': matched.iloc[i1]['villages'],
            'src_block': matched.iloc[i1]['blocks'],
            'dst_village': matched.iloc[i2]['villages'],
            'dst_block': matched.iloc[i2]['blocks'],
            'hops': hops,
            'dist_m': round(dist, 2)
        })

print(pd.DataFrame(results).to_string())
