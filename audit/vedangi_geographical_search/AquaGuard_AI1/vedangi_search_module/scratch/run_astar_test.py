import os, sys, time, math, heapq
import pandas as pd
import networkx as nx
import osmnx as ox

# Add project root to path for bfs_search import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from bfs_search import _load_graph, _load_snap_csv, _shortest_edge_length

# A* implementation (copied from notebook)
def astar_route(start_node: int, target_node: int, G: nx.MultiDiGraph = None) -> dict:
    if G is None:
        G = globals().get('G')
    result = {'success': False, 'route': None, 'distance_m': None,
              'expanded_nodes': 0, 'edge_count': None, 'time_s': None}
    if start_node not in G or target_node not in G:
        result['time_s'] = 0.0
        return result
    tx = G.nodes[target_node].get('x')
    ty = G.nodes[target_node].get('y')
    if tx is None or ty is None:
        result['time_s'] = 0.0
        return result
    def heuristic(n):
        nx_val = G.nodes[n].get('x')
        ny_val = G.nodes[n].get('y')
        return math.hypot(nx_val - tx, ny_val - ty) if nx_val is not None else float('inf')
    start_time = time.time()
    frontier = []
    heapq.heappush(frontier, (heuristic(start_node), 0.0, start_node))
    came_from = {start_node: None}
    g_score = {start_node: 0.0}
    expanded = 0
    while frontier:
        f_current, g_current, current = heapq.heappop(frontier)
        expanded += 1
        if current == target_node:
            break
        for neighbor in G.successors(current):
            edge_len = _shortest_edge_length(G, current, neighbor)
            tentative_g = g_current + edge_len
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                f_neighbor = tentative_g + heuristic(neighbor)
                heapq.heappush(frontier, (f_neighbor, tentative_g, neighbor))
                came_from[neighbor] = current
    if target_node in came_from:
        path = []
        node = target_node
        while node is not None:
            path.append(node)
            node = came_from[node]
        path.reverse()
        total_dist = g_score[target_node]
        result.update({'success': True, 'route': path, 'distance_m': total_dist,
                       'expanded_nodes': expanded, 'edge_count': len(path)-1,
                       'time_s': time.time() - start_time})
    else:
        result.update({'expanded_nodes': expanded, 'time_s': time.time() - start_time})
    return result

# Synthetic test
def synthetic_astar_test():
    G_test = nx.MultiDiGraph()
    G_test.add_node(1, x=0, y=0)
    G_test.add_node(2, x=5, y=0)
    G_test.add_node(3, x=0, y=5)
    G_test.add_node(4, x=10, y=0)
    G_test.add_edge(1, 2, length=5)
    G_test.add_edge(2, 4, length=5)
    G_test.add_edge(1, 3, length=8)
    G_test.add_edge(3, 4, length=8)
    print('Running synthetic A* test…')
    print(astar_route(1, 4, G_test))

synthetic_astar_test()

# Real Pune test
G = _load_graph()
snap_df = _load_snap_csv()
if len(snap_df) >= 2:
    src = int(snap_df.iloc[0]['nearest_node_id'])
    dst = int(snap_df.iloc[1]['nearest_node_id'])
    print(f'Running A* on Pune graph from {src} to {dst} …')
    print(astar_route(src, dst, G))
else:
    print('Not enough matched locations')
