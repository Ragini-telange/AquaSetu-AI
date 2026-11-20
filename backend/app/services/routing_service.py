import os
import time
import math
import heapq
from collections import deque
from typing import Optional, List, Dict, Any, Tuple
import networkx as nx
import joblib
from fastapi import HTTPException

from app.core.config import settings
from app.schemas.routing import (
    PuneRoutingRequest,
    PuneRoutingResponse,
    SearchAlgorithm
)

def shortest_edge_length(G: nx.MultiDiGraph, u: int, v: int) -> float:
    data = G.get_edge_data(u, v, default={})
    if not data:
        return float("inf")
    lengths = [attr.get("length", float("inf")) for attr in data.values()]
    return min(lengths)

class RoutingService:
    def __init__(self):
        self.G: Optional[nx.MultiDiGraph] = None
        self.is_initialized = False

    def initialize(self):
        if self.is_initialized:
            return

        cache_path = settings.get_absolute_path(settings.PUNE_GRAPH_CACHE_PATH)
        raw_graphml_path = settings.get_absolute_path(settings.PUNE_GRAPH_RAW_PATH)

        if os.path.exists(cache_path):
            print(f"[RoutingService] Loading pre-parsed binary Pune road graph cache from {cache_path}...")
            t0 = time.time()
            self.G = joblib.load(cache_path)
            print(f"[RoutingService] Graph cache loaded in {time.time()-t0:.2f}s ({self.G.number_of_nodes():,} nodes, {self.G.number_of_edges():,} edges).")
        elif os.path.exists(raw_graphml_path):
            print(f"[RoutingService] Cache not found. Parsing raw GraphML from {raw_graphml_path}...")
            t0 = time.time()
            raw_G = nx.read_graphml(raw_graphml_path)
            self.G = nx.MultiDiGraph()
            for node, data in raw_G.nodes(data=True):
                self.G.add_node(int(node), x=float(data.get('x', 0)), y=float(data.get('y', 0)))
            for u, v, k, data in raw_G.edges(keys=True, data=True):
                self.G.add_edge(int(u), int(v), key=k, length=float(data.get('length', 0)))
            print(f"[RoutingService] Raw graph parsed in {time.time()-t0:.2f}s.")
        else:
            raise FileNotFoundError(f"Neither Pune graph cache ({cache_path}) nor raw GraphML ({raw_graphml_path}) was found.")

        self.is_initialized = True

    def find_route(self, req: PuneRoutingRequest) -> PuneRoutingResponse:
        if not self.is_initialized:
            self.initialize()

        start = req.start_node_id
        target = req.target_node_id
        algo = req.algorithm

        # Strict boundary validation: Pune road graph only
        if start not in self.G:
            raise HTTPException(
                status_code=404,
                detail=f"Start node ID {start} not found in Pune road network graph. Road routing is strictly restricted to Pune District."
            )
        if target not in self.G:
            raise HTTPException(
                status_code=404,
                detail=f"Target node ID {target} not found in Pune road network graph. Road routing is strictly restricted to Pune District."
            )

        if algo == SearchAlgorithm.ASTAR:
            res = self._astar(start, target)
        elif algo == SearchAlgorithm.BIDIRECTIONAL:
            res = self._bidirectional(start, target)
        elif algo == SearchAlgorithm.BFS:
            res = self._bfs(start, target)
        elif algo == SearchAlgorithm.GREEDY_BEST_FIRST:
            res = self._greedy_best_first(start, target)
        elif algo == SearchAlgorithm.IDDFS:
            res = self._iddfs(start, target, max_depth=req.max_depth or 25)
        elif algo == SearchAlgorithm.DFS:
            res = self._dfs(start, target)
        else:
            res = self._astar(start, target)

        # Build coordinate geometry for frontend mapping
        route_nodes = res.get('route')
        geom: Optional[List[List[float]]] = None
        if route_nodes:
            geom = []
            for n in route_nodes:
                ndata = self.G.nodes.get(n, {})
                # Note: 'y' is latitude, 'x' is longitude in OSM coordinates
                lat = ndata.get('y')
                lon = ndata.get('x')
                if lat is not None and lon is not None:
                    geom.append([round(float(lat), 6), round(float(lon), 6)])

        dist_m = res.get('distance_m')
        dist_km = round(dist_m / 1000.0, 3) if dist_m is not None else None

        return PuneRoutingResponse(
            success=res.get('success', False),
            algorithm=algo.value,
            start_node_id=start,
            target_node_id=target,
            total_distance_m=round(dist_m, 2) if dist_m is not None else None,
            total_distance_km=dist_km,
            edge_count=res.get('edge_count'),
            expanded_nodes=res.get('expanded_nodes', 0),
            execution_time_ms=round(res.get('time_s', 0.0) * 1000.0, 3),
            route_node_ids=route_nodes,
            route_geometry=geom,
            error_message=res.get('error')
        )

    # 1. A* SEARCH (Distance-Optimal)
    def _astar(self, start: int, target: int) -> Dict[str, Any]:
        target_x = self.G.nodes[target]['x']
        target_y = self.G.nodes[target]['y']
        def h(n):
            return math.hypot(self.G.nodes[n]['x'] - target_x, self.G.nodes[n]['y'] - target_y)

        t0 = time.time()
        open_set = []
        heapq.heappush(open_set, (h(start), 0.0, start))
        came_from = {start: None}
        g_score = {start: 0.0}
        expanded = 0

        while open_set:
            f, g, cur = heapq.heappop(open_set)
            expanded += 1
            if cur == target:
                break
            if g > g_score.get(cur, float('inf')):
                continue
            for nbr in self.G.successors(cur):
                cost = shortest_edge_length(self.G, cur, nbr)
                tentative_g = g + cost
                if tentative_g < g_score.get(nbr, float('inf')):
                    g_score[nbr] = tentative_g
                    came_from[nbr] = cur
                    heapq.heappush(open_set, (tentative_g + h(nbr), tentative_g, nbr))

        if target in came_from:
            path = []
            curr = target
            while curr is not None:
                path.append(curr)
                curr = came_from[curr]
            path.reverse()
            total_dist = sum(shortest_edge_length(self.G, u, v) for u, v in zip(path[:-1], path[1:]))
            return {
                'success': True,
                'route': path,
                'distance_m': total_dist,
                'expanded_nodes': expanded,
                'edge_count': len(path) - 1,
                'time_s': time.time() - t0
            }
        return {'success': False, 'expanded_nodes': expanded, 'time_s': time.time() - t0, 'error': 'No path found.'}

    # 2. BIDIRECTIONAL SEARCH (Hop-Optimal with Low Expansion)
    def _bidirectional(self, start: int, target: int) -> Dict[str, Any]:
        t0 = time.time()
        if start == target:
            return {'success': True, 'route': [start], 'distance_m': 0.0, 'expanded_nodes': 0, 'edge_count': 0, 'time_s': time.time() - t0}

        q_f = deque([start])
        q_b = deque([target])
        came_from_f = {start: None}
        came_from_b = {target: None}
        expanded = 0
        meeting_node = None

        while q_f and q_b:
            # Forward expansion
            for _ in range(len(q_f)):
                cur_f = q_f.popleft()
                expanded += 1
                for succ in self.G.successors(cur_f):
                    if succ not in came_from_f:
                        came_from_f[succ] = cur_f
                        if succ in came_from_b:
                            meeting_node = succ
                            break
                        q_f.append(succ)
                if meeting_node is not None:
                    break
            if meeting_node is not None:
                break

            # Backward expansion (traversing predecessors to strictly respect one-way directed edges)
            for _ in range(len(q_b)):
                cur_b = q_b.popleft()
                expanded += 1
                for pred in self.G.predecessors(cur_b):
                    if pred not in came_from_b:
                        came_from_b[pred] = cur_b
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

            full_route = path_f + path_b
            total_dist = sum(shortest_edge_length(self.G, u, v) for u, v in zip(full_route[:-1], full_route[1:]))
            return {
                'success': True,
                'route': full_route,
                'distance_m': total_dist,
                'expanded_nodes': expanded,
                'edge_count': len(full_route) - 1,
                'time_s': time.time() - t0
            }
        return {'success': False, 'expanded_nodes': expanded, 'time_s': time.time() - t0, 'error': 'No meeting node found.'}

    # 3. BFS (Hop-Optimal Benchmark)
    def _bfs(self, start: int, target: int) -> Dict[str, Any]:
        t0 = time.time()
        frontier = deque([start])
        came_from = {start: None}
        expanded = 0

        while frontier:
            cur = frontier.popleft()
            expanded += 1
            if cur == target:
                break
            for nbr in self.G.successors(cur):
                if nbr not in came_from:
                    frontier.append(nbr)
                    came_from[nbr] = cur

        if target in came_from:
            path = []
            curr = target
            while curr is not None:
                path.append(curr)
                curr = came_from[curr]
            path.reverse()
            total_dist = sum(shortest_edge_length(self.G, u, v) for u, v in zip(path[:-1], path[1:]))
            return {
                'success': True,
                'route': path,
                'distance_m': total_dist,
                'expanded_nodes': expanded,
                'edge_count': len(path) - 1,
                'time_s': time.time() - t0
            }
        return {'success': False, 'expanded_nodes': expanded, 'time_s': time.time() - t0, 'error': 'Target unreachable.'}

    # 4. GREEDY BEST-FIRST SEARCH
    def _greedy_best_first(self, start: int, target: int) -> Dict[str, Any]:
        target_x = self.G.nodes[target]['x']
        target_y = self.G.nodes[target]['y']
        def h(n):
            return math.hypot(self.G.nodes[n]['x'] - target_x, self.G.nodes[n]['y'] - target_y)

        t0 = time.time()
        frontier = []
        heapq.heappush(frontier, (h(start), start))
        came_from = {start: None}
        expanded = 0

        while frontier:
            _, cur = heapq.heappop(frontier)
            expanded += 1
            if cur == target:
                break
            for nbr in self.G.successors(cur):
                if nbr not in came_from:
                    heapq.heappush(frontier, (h(nbr), nbr))
                    came_from[nbr] = cur

        if target in came_from:
            path = []
            curr = target
            while curr is not None:
                path.append(curr)
                curr = came_from[curr]
            path.reverse()
            total_dist = sum(shortest_edge_length(self.G, u, v) for u, v in zip(path[:-1], path[1:]))
            return {
                'success': True,
                'route': path,
                'distance_m': total_dist,
                'expanded_nodes': expanded,
                'edge_count': len(path) - 1,
                'time_s': time.time() - t0
            }
        return {'success': False, 'expanded_nodes': expanded, 'time_s': time.time() - t0, 'error': 'Target unreachable.'}

    # 5. IDDFS (Iterative Deepening Depth-First Search)
    def _iddfs(self, start: int, target: int, max_depth: int = 25) -> Dict[str, Any]:
        t0 = time.time()
        total_expanded = 0

        def dls(node, depth, path, visited):
            nonlocal total_expanded
            total_expanded += 1
            if node == target:
                return path
            if depth <= 0:
                return None
            for nbr in self.G.successors(node):
                if nbr not in visited:
                    visited.add(nbr)
                    found = dls(nbr, depth - 1, path + [nbr], visited)
                    if found is not None:
                        return found
            return None

        for d in range(1, max_depth + 1):
            visited = {start}
            route = dls(start, d, [start], visited)
            if route is not None:
                total_dist = sum(shortest_edge_length(self.G, u, v) for u, v in zip(route[:-1], route[1:]))
                return {
                    'success': True,
                    'route': route,
                    'distance_m': total_dist,
                    'expanded_nodes': total_expanded,
                    'edge_count': len(route) - 1,
                    'time_s': time.time() - t0
                }

        return {
            'success': False,
            'expanded_nodes': total_expanded,
            'time_s': time.time() - t0,
            'error': f"No route found within depth limit {max_depth}."
        }

    # 6. DFS (Depth-First Search)
    def _dfs(self, start: int, target: int) -> Dict[str, Any]:
        t0 = time.time()
        stack = [start]
        came_from = {start: None}
        expanded = 0

        while stack:
            cur = stack.pop()
            expanded += 1
            if cur == target:
                break
            for nbr in self.G.successors(cur):
                if nbr not in came_from:
                    stack.append(nbr)
                    came_from[nbr] = cur

        if target in came_from:
            path = []
            curr = target
            while curr is not None:
                path.append(curr)
                curr = came_from[curr]
            path.reverse()
            total_dist = sum(shortest_edge_length(self.G, u, v) for u, v in zip(path[:-1], path[1:]))
            return {
                'success': True,
                'route': path,
                'distance_m': total_dist,
                'expanded_nodes': expanded,
                'edge_count': len(path) - 1,
                'time_s': time.time() - t0
            }
        return {'success': False, 'expanded_nodes': expanded, 'time_s': time.time() - t0, 'error': 'Target unreachable.'}

routing_service = RoutingService()
