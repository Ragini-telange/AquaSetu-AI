import sys
import os
import json
import pandas as pd
import networkx as nx

module_path = os.path.abspath('vedangi_search_module')
if module_path not in sys.path:
    sys.path.insert(0, module_path)

from bfs_search import _load_graph, _shortest_edge_length

G = _load_graph()
s5, d5 = 12788595845, 2125144688

nb_path = os.path.join(module_path, 'AI_Search_Algorithms.ipynb')
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

ns = {'G': G, '_shortest_edge_length': _shortest_edge_length}
exec(''.join(nb['cells'][26]['source']), ns)
_dls = ns['_dls']
iddfs_route = ns['iddfs_route']

for d in range(31, 36):
    res = iddfs_route(s5, d5, G=G, max_depth=d)
    print(f"max_depth={d}: success={res['success']}, edge_count={res['edge_count']}, expanded={res['expanded_nodes']}, dist={res['distance_m']}")
    if res['success']:
        print("First successful depth found:", d)
        break
