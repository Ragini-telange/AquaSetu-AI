import sys
import os
import json
import pandas as pd
import networkx as nx

module_path = os.path.abspath('vedangi_search_module')
if module_path not in sys.path:
    sys.path.insert(0, module_path)

from bfs_search import _load_graph, _load_snap_csv, _shortest_edge_length

print("Loading graph and snap CSV...")
G = _load_graph()
snap_df = _load_snap_csv()
matched = snap_df[snap_df['match_status'] == 'Matched']
print(f"Matched snap locations: {len(matched)}")

# Test pairs between nodes
nodes = matched['nearest_node_id'].unique().tolist()
print(f"Unique matched nodes: {len(nodes)}")

# Let's inspect shortest paths using nx.shortest_path to find reachable pairs of varying lengths
found_pairs = []
for i in range(len(nodes)):
    for j in range(i + 1, min(i + 20, len(nodes))):
        u, v = int(nodes[i]), int(nodes[j])
        if nx.has_path(G, u, v):
            try:
                length = nx.shortest_path_length(G, u, v, weight='length')
                hops = nx.shortest_path_length(G, u, v)
                u_info = matched[matched['nearest_node_id'] == u].iloc[0]
                v_info = matched[matched['nearest_node_id'] == v].iloc[0]
                found_pairs.append({
                    'src_id': u,
                    'dst_id': v,
                    'src_village': u_info['villages'],
                    'src_block': u_info['blocks'],
                    'dst_village': v_info['villages'],
                    'dst_block': v_info['blocks'],
                    'hops': hops,
                    'dist_m': length
                })
            except Exception:
                pass
    if len(found_pairs) >= 15:
        break

pdf = pd.DataFrame(found_pairs)
print(pdf.to_string())
