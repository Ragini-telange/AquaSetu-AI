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

# Find all connected pairs with hop count <= 25 among the first 25 locations
nodes_info = matched.iloc[:35][['nearest_node_id', 'villages', 'blocks']].to_dict('records')

results = []
for i, u_info in enumerate(nodes_info):
    u = int(u_info['nearest_node_id'])
    for j, v_info in enumerate(nodes_info):
        if i == j:
            continue
        v = int(v_info['nearest_node_id'])
        if nx.has_path(G, u, v):
            hops = nx.shortest_path_length(G, u, v)
            if hops <= 25:
                dist = nx.shortest_path_length(G, u, v, weight='length')
                results.append({
                    'src_id': u,
                    'dst_id': v,
                    'src_village': u_info['villages'],
                    'src_block': u_info['blocks'],
                    'dst_village': v_info['villages'],
                    'dst_block': v_info['blocks'],
                    'hops': hops,
                    'dist_m': round(dist, 2)
                })

df_pairs = pd.DataFrame(results)
print(f"Total pairs found with <= 25 hops: {len(df_pairs)}")
print(df_pairs.sort_values('hops').drop_duplicates(subset=['hops']).to_string())
