import time
import networkx as nx
import pandas as pd
from bfs_search import _load_graph, _load_snap_csv, _shortest_edge_length

# IDDFS implementation
def _dls(start, target, depth, G):
    """Depth-limited DFS. Returns (found, path, nodes_expanded)."""
    if depth < 0:
        return False, [], 0
    stack = [(start, [start])]
    visited = set([start])
    nodes_expanded = 0
    while stack:
        node, path = stack.pop()
        nodes_expanded += 1
        if node == target:
            return True, path, nodes_expanded
        if len(path) - 1 == depth:
            continue
        for succ in G.successors(node):
            if succ not in visited:
                visited.add(succ)
                stack.append((succ, path + [succ]))
    return False, [], nodes_expanded

def iddfs_route(start_node, target_node, G, max_depth=20):
    """Iterative Deepening DFS route finder.
    Returns dict with keys: success, route, distance_m, expanded_nodes, edge_count, time_s.
    """
    if start_node not in G or target_node not in G:
        return {'success': False, 'route': [], 'distance_m': 0.0, 'expanded_nodes': 0,
                'edge_count': 0, 'time_s': 0.0, 'error': 'Invalid start or target node'}
    start_time = time.time()
    total_expanded = 0
    for depth in range(max_depth + 1):
        found, path, expanded = _dls(start_node, target_node, depth, G)
        total_expanded += expanded
        if found:
            distance = 0.0
            for u, v in zip(path[:-1], path[1:]):
                distance += _shortest_edge_length(G, u, v)
            return {'success': True, 'route': path, 'distance_m': distance,
                    'expanded_nodes': total_expanded, 'edge_count': len(path)-1,
                    'time_s': time.time() - start_time}
    return {'success': False, 'route': [], 'distance_m': 0.0, 'expanded_nodes': total_expanded,
            'edge_count': 0, 'time_s': time.time() - start_time,
            'error': f'No path found within depth {max_depth}'}

# Synthetic test
G_test = nx.DiGraph()
G_test.add_edges_from([(1,2),(2,3),(3,4),(1,5),(5,4)])
for u,v in G_test.edges():
    G_test[u][v]['length'] = 1
# temporary _shortest_edge_length for test
def _shortest_edge_length(G,u,v):
    data = G.get_edge_data(u,v)
    if data is None:
        return float('inf')
    if isinstance(data, dict) and any(isinstance(k,int) for k in data):
        return min(d.get('length', float('inf')) for d in data.values())
    return data.get('length', float('inf'))

synthetic_res = iddfs_route(1,4,G_test,max_depth=3)
print('Synthetic IDDFS result:', synthetic_res)

# Real-world test
G = _load_graph()
snap_df = _load_snap_csv()
if len(snap_df) >= 2:
    src = int(snap_df.iloc[0]['nearest_node_id'])
    dst = int(snap_df.iloc[1]['nearest_node_id'])
    real_res = iddfs_route(src, dst, G, max_depth=30)
    print('Real-world IDDFS result:', real_res)
else:
    print('Not enough matched locations for real-world demo.')
