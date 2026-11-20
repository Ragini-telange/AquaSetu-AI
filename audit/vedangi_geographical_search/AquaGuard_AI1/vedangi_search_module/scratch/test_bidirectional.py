import sys
import os

# Add vedangi_search_module to path
module_path = os.path.abspath('vedangi_search_module')
if module_path not in sys.path:
    sys.path.insert(0, module_path)

import networkx as nx
from bfs_search import _load_graph, _load_snap_csv, _shortest_edge_length

# Import collections and time
from collections import deque
import time

def bidirectional_route(start_node: int, target_node: int, G: nx.MultiDiGraph = None) -> dict:
    if G is None:
        G = globals().get('G')
        
    result = {
        'success': False,
        'route': None,
        'distance_m': None,
        'expanded_nodes': 0,
        'edge_count': None,
        'time_s': None,
    }
    
    if G is None or start_node not in G or target_node not in G:
        result['time_s'] = 0.0
        return result
        
    start_time = time.time()
    
    if start_node == target_node:
        result.update({
            'success': True,
            'route': [start_node],
            'distance_m': 0.0,
            'expanded_nodes': 0,
            'edge_count': 0,
            'time_s': time.time() - start_time,
        })
        return result

    q_f = deque([start_node])
    q_b = deque([target_node])
    
    came_from_f = {start_node: None}
    came_from_b = {target_node: None}
    
    expanded = 0
    meeting_node = None
    
    while q_f and q_b:
        level_size_f = len(q_f)
        for _ in range(level_size_f):
            current_f = q_f.popleft()
            expanded += 1
            
            for succ in G.successors(current_f):
                if succ not in came_from_f:
                    came_from_f[succ] = current_f
                    if succ in came_from_b:
                        meeting_node = succ
                        break
                    q_f.append(succ)
            if meeting_node is not None:
                break
                
        if meeting_node is not None:
            break
            
        level_size_b = len(q_b)
        for _ in range(level_size_b):
            current_b = q_b.popleft()
            expanded += 1
            
            for pred in G.predecessors(current_b):
                if pred not in came_from_b:
                    came_from_b[pred] = current_b
                    if pred in came_from_f:
                        meeting_node = pred
                        break
                    q_b.append(pred)
            if meeting_node is not None:
                break
                
        if meeting_node is not None:
            break

    if meeting_node is not None:
        path_f = []
        curr = meeting_node
        while curr is not None:
            path_f.append(curr)
            curr = came_from_f[curr]
        path_f.reverse()
        
        path_b = []
        curr = came_from_b[meeting_node]
        while curr is not None:
            path_b.append(curr)
            curr = came_from_b[curr]
            
        complete_route = path_f + path_b
        
        total_dist = sum(
            _shortest_edge_length(G, u, v)
            for u, v in zip(complete_route[:-1], complete_route[1:])
        )
        
        result.update({
            'success': True,
            'route': complete_route,
            'distance_m': total_dist,
            'expanded_nodes': expanded,
            'edge_count': len(complete_route) - 1,
            'time_s': time.time() - start_time,
        })
    else:
        result.update({
            'expanded_nodes': expanded,
            'time_s': time.time() - start_time,
        })
        
    return result

# 1. Run Synthetic Test
print("=== Running Synthetic Test ===")
G_test = nx.MultiDiGraph()
G_test.add_edge(1, 2, length=10)
G_test.add_edge(1, 2, length=6)   # Shorter parallel edge
G_test.add_edge(2, 4, length=7)
G_test.add_edge(1, 3, length=5)
G_test.add_edge(3, 4, length=12)

res_synthetic = bidirectional_route(1, 4, G_test)
print("Synthetic Test Result:", res_synthetic)

# 2. Run Real Pune Network Test
print("\n=== Running Real Pune Road Graph Test ===")
G = _load_graph()
snap_df = _load_snap_csv()
print(f"Loaded graph with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
print(f"Matched groundwater locations: {len(snap_df)}")

if len(snap_df) >= 2:
    src = int(snap_df.iloc[0]['nearest_node_id'])
    dst = int(snap_df.iloc[1]['nearest_node_id'])
    print(f"Running Bidirectional Search from node {src} to node {dst}...")
    res_real = bidirectional_route(src, dst, G)
    print("Real-world Test Result:", res_real)
else:
    print("Not enough matched locations.")
