import os, time
import pandas as pd
import networkx as nx
import osmnx as ox

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bfs_search import _load_graph, _load_snap_csv, _shortest_edge_length

# DFS implementation (same as notebook)
def dfs_route(start_node: int, target_node: int, G: nx.MultiDiGraph = None) -> dict:
    if G is None:
        G = globals().get('G')
    result = {'success': False, 'route': None, 'distance_m': None, 'expanded_nodes': 0, 'edge_count': None, 'time_s': None}
    if start_node not in G or target_node not in G:
        result['time_s'] = 0.0
        return result
    start_time = time.time()
    stack = [start_node]
    came_from = {start_node: None}
    expanded = 0
    while stack:
        current = stack.pop()
        expanded += 1
        if current == target_node:
            break
        for neighbor in G.successors(current):
            if neighbor not in came_from:
                stack.append(neighbor)
                came_from[neighbor] = current
    if target_node in came_from:
        path = []
        node = target_node
        while node is not None:
            path.append(node)
            node = came_from[node]
        path.reverse()
        total_dist = sum(_shortest_edge_length(G, u, v) for u, v in zip(path[:-1], path[1:]))
        result.update({
            'success': True,
            'route': path,
            'distance_m': total_dist,
            'expanded_nodes': expanded,
            'edge_count': len(path)-1,
            'time_s': time.time() - start_time,
        })
    else:
        result.update({'expanded_nodes': expanded, 'time_s': time.time() - start_time})
    return result

# Synthetic test
G_test = nx.MultiDiGraph()
G_test.add_edge(1, 2, length=10)
G_test.add_edge(1, 3, length=5)
G_test.add_edge(1, 3, length=3)
G_test.add_edge(2, 4, length=7)
G_test.add_edge(3, 4, length=12)
print('Running synthetic DFS test…')
print(dfs_route(1, 4, G_test))

# Real Pune test using first two matched locations
G = _load_graph()
snap_df = _load_snap_csv()
if len(snap_df) >= 2:
    src = int(snap_df.iloc[0]['nearest_node_id'])
    dst = int(snap_df.iloc[1]['nearest_node_id'])
    print(f'Running DFS on Pune graph from {src} to {dst} …')
    print(dfs_route(src, dst, G))
else:
    print('Not enough matched locations')
