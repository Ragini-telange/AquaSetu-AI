# AquaGuard AI – Search Algorithms

## 1. Project Overview

AquaGuard AI implements and compares six graph-search algorithms for finding routes between groundwater locations using the Pune road network.

The project uses a directed road network represented as a NetworkX MultiDiGraph. This allows the algorithms to respect one-way roads and calculate route distances in metres.

## 2. Search Algorithms Implemented

The project implements six search algorithms:

1. **Breadth-First Search (BFS)** – Finds routes with the minimum number of edges.
2. **Depth-First Search (DFS)** – Explores paths deeply before backtracking.
3. **Greedy Best-First Search (GBFS)** – Uses Euclidean distance as a heuristic to guide the search.
4. **A* Search** – Combines accumulated road distance and heuristic distance to find shortest-distance routes.
5. **Iterative Deepening DFS (IDDFS)** – Repeatedly performs depth-limited searches with increasing depth limits.
6. **Bidirectional Search** – Searches simultaneously from the source and destination.

## 3. Dataset and Road Network

- Geographic area: Pune, Maharashtra, India.
- Road network: Directed road graph.
- Graph representation: NetworkX MultiDiGraph.
- Groundwater locations: Matched to their nearest road-network nodes.
- Distance measurement: Metres.

Only groundwater locations with a successful matching status (`Matched`) are considered.

## 4. Project Structure

The project includes:

- `AI_Search_Algorithms.ipynb` – Main notebook containing all six search algorithms, explanations, and tests.
- `bfs_search.py` – BFS implementation and shared graph-loading and distance helper functions.
- `pune_location_node_snap.csv` – Groundwater locations matched to road-network nodes.
- Road network GraphML data – Directed Pune road network.
- `outputs/` – Benchmark results, summary tables, audit report, and performance charts.

## 5. Performance Evaluation

The algorithms were evaluated using five source-destination route pairs.

The following metrics were recorded:

- Success rate
- Total route distance (metres)
- Number of edges
- Expanded nodes
- Execution time (seconds)

### Benchmark Summary

| Algorithm | Success Rate | Average Distance (m) | Average Edges |
|---|---:|---:|---:|
| BFS | 100% | 5821.516 | 9.4 |
| DFS | 100% | 1141240.026 | 3561.0 |
| Greedy Best-First | 100% | 5477.070 | 14.4 |
| A* | 100% | 5088.742 | 14.2 |
| IDDFS | 80% | 5278.788 | 7.0 |
| Bidirectional Search | 100% | 5821.516 | 9.4 |

Note: Average distance and edge counts for IDDFS are calculated using successful runs only (4 out of 5).

## 6. Important Findings

- BFS and Bidirectional Search achieved 100% success and matched minimum-edge routes across the five benchmark pairs.
- A* successfully found the shortest-distance route in the audited Pair 1 comparison.
- Greedy Best-First Search used a heuristic to guide its exploration.
- DFS explored substantially more nodes and produced longer routes in the benchmark.
- IDDFS achieved an 80% success rate under the configured depth limit of 25.
- IDDFS required a depth limit of 32 to find a route for Pair 5 in the independent depth investigation. Its returned route was not the minimum-edge route.

## 7. Output Files

The `outputs/` directory contains:

- `search_algorithms_summary.csv` – Corrected algorithm performance summary.
- `search_algorithms_performance_comparison.png` – Performance comparison chart.
- `search_algorithms_per_pair_breakdown.png` – Pair-wise performance breakdown.
- `benchmark_audit.txt` – Independent benchmark verification report.

## 8. How to Run the Project

1. Open the project folder in Visual Studio Code.
2. Activate the project's Python virtual environment.
3. Install the required Python packages and Jupyter dependencies.
4. Open `vedangi_search_module/AI_Search_Algorithms.ipynb`.
5. Select the correct Python kernel.
6. Run the notebook cells from top to bottom.
7. Review the algorithm outputs and benchmark results.

Ensure that the road network data, groundwater matching CSV, and helper Python files are available at the paths expected by the project.

## 9. Conclusion

This project demonstrates how different graph-search algorithms perform when routing between groundwater locations on a real-world directed road network.

The comparison highlights the differences between minimum-edge routing, shortest-distance routing, heuristic-guided search, depth-limited search, and bidirectional exploration.

The benchmark results and independent audit provide a basis for evaluating the correctness and performance of the implemented algorithms.