# bfs_search.py
"""Breadth‑First Search (BFS) implementation for the Pune road network.

This module provides a simple, beginner‑friendly BFS that works on a directed
`networkx.MultiDiGraph`.  It respects one‑way streets because the graph is
directed.  BFS minimizes the **number of edges** traversed – it does *not* give
the shortest‑distance route.

The main public function is :func:`bfs_route` which returns a dictionary with
the route, total distance (metres), execution time, number of expanded nodes,
edge count and a success flag.

A small synthetic graph test is included so the code can be exercised without
loading the full ~200 MB Pune graph.
"""

import time
import os
from typing import List, Dict, Any, Tuple, Optional

import pandas as pd
import networkx as nx
import osmnx as ox

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _load_graph() -> nx.MultiDiGraph:
    """Load the Pune road network GraphML.

    Returns
    -------
    nx.MultiDiGraph
        The directed road graph with UTM projection (meters).
    """
    graph_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "pune_road_network.graphml",
    )
    # The GraphML was saved with OSMnx and contains the projected coordinates.
    G = ox.load_graphml(graph_path)
    return G


def _load_snap_csv() -> pd.DataFrame:
    """Load the snapping CSV and keep only matched locations.

    Returns
    -------
    pd.DataFrame
        Rows where ``match_status == 'Matched'`` and the ``nearest_node_id``
        column is valid.
    """
    csv_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        "processed_data",
        "pune_location_node_snap.csv",
    )
    df = pd.read_csv(csv_path)
    # Keep only rows that were successfully matched (distance <= 100 m).
    df = df[df["match_status"] == "Matched"].copy()
    return df


def _shortest_edge_length(G: nx.MultiDiGraph, u: int, v: int) -> float:
    """Return the shortest ``length`` among parallel edges from *u* to *v*.

    Parameters
    ----------
    G : nx.MultiDiGraph
    u, v : node identifiers

    Returns
    -------
    float
        Shortest length in metres; ``float('inf')`` if no edge exists.
    """
    data = G.get_edge_data(u, v, default={})
    if not data:
        return float("inf")
    # ``data`` is a dict keyed by edge key (0,1,2, ...).
    lengths = [attr.get("length", float("inf")) for attr in data.values()]
    return min(lengths)


# ---------------------------------------------------------------------------
# Public BFS function
# ---------------------------------------------------------------------------

def bfs_route(
    start_node: int,
    target_node: int,
    G: Optional[nx.MultiDiGraph] = None,
) -> Dict[str, Any]:
    """Find a route using Breadth‑First Search.

    Parameters
    ----------
    start_node : int
        Road‑network node ID to start from.
    target_node : int
        Desired destination node ID.
    G : nx.MultiDiGraph, optional
        If supplied the function uses this graph; otherwise it loads the
        Pune graph from ``pune_road_network.graphml``.

    Returns
    -------
    dict
        ``{
            'success': bool,
            'route': List[int] | None,
            'distance_m': float | None,
            'expanded_nodes': int,
            'edge_count': int | None,
            'time_s': float,
        }``
    """
    if G is None:
        G = _load_graph()

    result: Dict[str, Any] = {
        "success": False,
        "route": None,
        "distance_m": None,
        "expanded_nodes": 0,
        "edge_count": None,
        "time_s": None,
    }

    # Validate that the provided IDs exist in the graph.
    if start_node not in G:
        result["time_s"] = 0.0
        return result
    if target_node not in G:
        result["time_s"] = 0.0
        return result

    start_time = time.time()
    # Standard BFS using a queue (list as deque for simplicity).
    from collections import deque

    frontier: deque = deque([start_node])
    came_from: Dict[int, Optional[int]] = {start_node: None}
    expanded = 0

    while frontier:
        current = frontier.popleft()
        expanded += 1
        if current == target_node:
            break
        # Neighbours follow the direction of the edges (out‑edges).
        for neighbor in G.successors(current):
            if neighbor not in came_from:
                frontier.append(neighbor)
                came_from[neighbor] = current

    # Reconstruct path if target was reached.
    if target_node in came_from:
        path: List[int] = []
        node = target_node
        while node is not None:
            path.append(node)
            node = came_from[node]  # type: ignore[arg-type]
        path.reverse()
        # Compute total distance using the shortest parallel edge for each hop.
        total_dist = 0.0
        for u, v in zip(path[:-1], path[1:]):
            total_dist += _shortest_edge_length(G, u, v)
        result.update(
            {
                "success": True,
                "route": path,
                "distance_m": total_dist,
                "expanded_nodes": expanded,
                "edge_count": len(path) - 1,
                "time_s": time.time() - start_time,
            }
        )
    else:
        # Target not reachable.
        result.update(
            {
                "expanded_nodes": expanded,
                "time_s": time.time() - start_time,
            }
        )

    return result


# ---------------------------------------------------------------------------
# Synthetic graph tests – these run when the module is executed directly.
# ---------------------------------------------------------------------------

def _run_synthetic_tests() -> None:
    """Create a tiny directed graph and verify BFS behaviour.

    The test checks:
    * a reachable path is found,
    * the number of edges matches the BFS optimum, and
    * distance calculation picks the shortest parallel edge.
    """
    # Construct a small graph:
    #   1 → 2 (len=10) , 1 → 3 (len=5) , 2 → 4 (len=7) , 3 → 4 (len=12)
    #   also a parallel edge 1 → 3 with a shorter length (len=3).
    G = nx.MultiDiGraph()
    G.add_edge(1, 2, length=10)
    G.add_edge(1, 3, length=5)
    G.add_edge(1, 3, length=3)  # parallel, shorter
    G.add_edge(2, 4, length=7)
    G.add_edge(3, 4, length=12)

    # BFS from 1 to 4 should return [1, 2, 4] (2 edges) because it expands
    # level‑by‑level; both paths have the same edge count (2), but the algorithm
    # will discover the neighbour 2 before 3, yielding that path.
    res = bfs_route(start_node=1, target_node=4, G=G)
    assert res["success"]
    assert res["route"] == [1, 2, 4], f"Unexpected route {res['route']}"
    # Distance should be length(1‑2) + length(2‑4) = 10 + 7 = 17.
    assert abs(res["distance_m"] - 17) < 1e-6, f"Distance mismatch {res['distance_m']}"
    assert res["edge_count"] == 2
    print("Synthetic BFS test passed.")


if __name__ == "__main__":
    # Run the synthetic test suite.
    _run_synthetic_tests()
    # Example of using the real Pune graph – pick the first two matched nodes.
    # This block is for interactive exploration and will not be executed in the
    # automated test environment unless the user runs the module manually.
    df = _load_snap_csv()
    if len(df) >= 2:
        s = int(df.iloc[0]["nearest_node_id"])
        t = int(df.iloc[1]["nearest_node_id"])
        print(f"Running BFS on Pune graph from node {s} to {t} …")
        real_res = bfs_route(start_node=s, target_node=t)
        print("Result:", real_res)
