import json

nb_path = r'vedangi_search_module/AI_Search_Algorithms.ipynb'
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Update top header cell to reflect all 6 algorithms
if nb['cells'] and nb['cells'][0]['cell_type'] == 'markdown':
    nb['cells'][0]['source'] = [
        "# AquaGuard AI Search Algorithms Notebook\n",
        "\n",
        "This notebook gathers all six graph-search algorithms used for routing groundwater locations on the road network:\n",
        "1. Breadth-First Search (BFS)\n",
        "2. Depth-First Search (DFS)\n",
        "3. Greedy Best-First Search (GBFS)\n",
        "4. A* Search (A*)\n",
        "5. Iterative Deepening DFS (IDDFS)\n",
        "6. Bidirectional Search\n"
    ]

# Find the placeholder markdown cell for Bidirectional Search
placeholder_idx = None
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'markdown':
        src = ''.join(cell.get('source', []))
        if 'Bidirectional Search' in src and 'TODO' in src:
            placeholder_idx = i
            break

if placeholder_idx is None:
    raise ValueError("Could not find Bidirectional Search placeholder cell")

# 1. Beginner-friendly explanation markdown
bidi_md_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 6️⃣ Bidirectional Search\n",
        "\n",
        "### What is Bidirectional Search?\n",
        "Bidirectional Search runs two simultaneous searches:\n",
        "1. **Forward Search:** Starts at the `start_node` and searches forward along outgoing directed edges (`G.successors`).\n",
        "2. **Backward Search:** Starts at the `target_node` and searches backward along incoming directed edges (`G.predecessors`).\n",
        "\n",
        "Instead of exploring a large single search ball of radius $d$ with complexity $O(b^d)$, bidirectional search explores two smaller search balls of radius $d/2$, reducing the time and space complexity to $O(b^{d/2})$. The searches stop as soon as their frontiers or visited sets intersect at a common **meeting node**.\n",
        "\n",
        "### Key Principles & Requirements:\n",
        "- **Directionality & One-Way Restrictions:** On a directed graph $G$, the forward search travels from node $u \\to v$ (following $G.successors(u)$). The backward search moves in the reverse direction of the traffic flow, which means traveling from $w \\to current$ (following $G.predecessors(current)$). This strictly guarantees that the resulting path only traverses roads in their legal, permissible directions.\n",
        "- **Completeness & Optimality:** When both directions expand level-by-level (Breadth-First order) on unweighted/uniform-step graphs, bidirectional search is **complete** (guaranteed to find a route if one exists) and finds the path with the **minimum number of edges**.\n",
        "- **Road Distance Calculation:** As with all our routing algorithms, the actual road distance in metres is calculated along the reconstructed route using the shortest parallel edge `length` between consecutive nodes via `_shortest_edge_length`.\n"
    ]
}

# 2. Implementation code cell
bidi_code_cell = {
    "cell_type": "code",
    "metadata": {},
    "execution_count": None,
    "source": [
        "from collections import deque\n",
        "import time\n",
        "import networkx as nx\n",
        "\n",
        "def bidirectional_route(start_node: int, target_node: int, G: nx.MultiDiGraph = None) -> dict:\n",
        "    \"\"\"Bidirectional Breadth-First Search on a directed MultiDiGraph.\n",
        "    \n",
        "    Parameters\n",
        "    ----------\n",
        "    start_node : int\n",
        "        Starting road-node ID.\n",
        "    target_node : int\n",
        "        Destination road-node ID.\n",
        "    G : nx.MultiDiGraph, optional\n",
        "        Directed road network. Defaults to global G.\n",
        "        \n",
        "    Returns\n",
        "    -------\n",
        "    dict\n",
        "        Standard result dictionary with keys:\n",
        "        'success', 'route', 'distance_m', 'expanded_nodes', 'edge_count', 'time_s'\n",
        "    \"\"\"\n",
        "    if G is None:\n",
        "        G = globals().get('G')\n",
        "        \n",
        "    result = {\n",
        "        'success': False,\n",
        "        'route': None,\n",
        "        'distance_m': None,\n",
        "        'expanded_nodes': 0,\n",
        "        'edge_count': None,\n",
        "        'time_s': None,\n",
        "    }\n",
        "    \n",
        "    if G is None or start_node not in G or target_node not in G:\n",
        "        result['time_s'] = 0.0\n",
        "        return result\n",
        "        \n",
        "    start_time = time.time()\n",
        "    \n",
        "    # Trivial case: start is already destination\n",
        "    if start_node == target_node:\n",
        "        result.update({\n",
        "            'success': True,\n",
        "            'route': [start_node],\n",
        "            'distance_m': 0.0,\n",
        "            'expanded_nodes': 0,\n",
        "            'edge_count': 0,\n",
        "            'time_s': time.time() - start_time,\n",
        "        })\n",
        "        return result\n",
        "\n",
        "    # Forward and backward queues\n",
        "    q_f = deque([start_node])\n",
        "    q_b = deque([target_node])\n",
        "    \n",
        "    # came_from dictionaries\n",
        "    # forward: came_from_f[n] = predecessor of n in forward tree\n",
        "    # backward: came_from_b[n] = successor of n in forward direction (parent in backward tree)\n",
        "    came_from_f = {start_node: None}\n",
        "    came_from_b = {target_node: None}\n",
        "    \n",
        "    expanded = 0\n",
        "    meeting_node = None\n",
        "    \n",
        "    while q_f and q_b:\n",
        "        # Expand one level from forward search\n",
        "        level_size_f = len(q_f)\n",
        "        for _ in range(level_size_f):\n",
        "            current_f = q_f.popleft()\n",
        "            expanded += 1\n",
        "            \n",
        "            for succ in G.successors(current_f):\n",
        "                if succ not in came_from_f:\n",
        "                    came_from_f[succ] = current_f\n",
        "                    if succ in came_from_b:\n",
        "                        meeting_node = succ\n",
        "                        break\n",
        "                    q_f.append(succ)\n",
        "            if meeting_node is not None:\n",
        "                break\n",
        "                \n",
        "        if meeting_node is not None:\n",
        "            break\n",
        "            \n",
        "        # Expand one level from backward search (traversing predecessors to respect one-way edges)\n",
        "        level_size_b = len(q_b)\n",
        "        for _ in range(level_size_b):\n",
        "            current_b = q_b.popleft()\n",
        "            expanded += 1\n",
        "            \n",
        "            for pred in G.predecessors(current_b):\n",
        "                if pred not in came_from_b:\n",
        "                    came_from_b[pred] = current_b\n",
        "                    if pred in came_from_f:\n",
        "                        meeting_node = pred\n",
        "                        break\n",
        "                    q_b.append(pred)\n",
        "            if meeting_node is not None:\n",
        "                break\n",
        "                \n",
        "        if meeting_node is not None:\n",
        "            break\n",
        "\n",
        "    if meeting_node is not None:\n",
        "        # Reconstruct path from start to meeting_node\n",
        "        path_f = []\n",
        "        curr = meeting_node\n",
        "        while curr is not None:\n",
        "            path_f.append(curr)\n",
        "            curr = came_from_f[curr]\n",
        "        path_f.reverse()\n",
        "        \n",
        "        # Reconstruct path from meeting_node to target_node\n",
        "        path_b = []\n",
        "        curr = came_from_b[meeting_node]\n",
        "        while curr is not None:\n",
        "            path_b.append(curr)\n",
        "            curr = came_from_b[curr]\n",
        "            \n",
        "        complete_route = path_f + path_b\n",
        "        \n",
        "        # Calculate total road distance using shortest parallel edge length\n",
        "        total_dist = sum(\n",
        "            _shortest_edge_length(G, u, v)\n",
        "            for u, v in zip(complete_route[:-1], complete_route[1:])\n",
        "        )\n",
        "        \n",
        "        result.update({\n",
        "            'success': True,\n",
        "            'route': complete_route,\n",
        "            'distance_m': total_dist,\n",
        "            'expanded_nodes': expanded,\n",
        "            'edge_count': len(complete_route) - 1,\n",
        "            'time_s': time.time() - start_time,\n",
        "        })\n",
        "    else:\n",
        "        result.update({\n",
        "            'expanded_nodes': expanded,\n",
        "            'time_s': time.time() - start_time,\n",
        "        })\n",
        "        \n",
        "    return result\n"
    ],
    "outputs": []
}

# 3. Synthetic test markdown & code
synthetic_md_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### Synthetic Bidirectional Search Test\n",
        "\n",
        "We build a small directed test graph with parallel edges and one-way constraints to verify:\n",
        "1. Forward and backward search meet correctly.\n",
        "2. One-way directionality is strictly obeyed (backward search follows predecessors).\n",
        "3. Shortest parallel edge lengths are selected for distance calculation.\n"
    ]
}

synthetic_code_cell = {
    "cell_type": "code",
    "metadata": {},
    "execution_count": None,
    "source": [
        "def synthetic_bidirectional_test():\n",
        "    G_test = nx.MultiDiGraph()\n",
        "    # Edges: 1 -> 2 -> 4 and 1 -> 3 -> 4\n",
        "    # Parallel edge between 1 and 2: lengths 10 and 6\n",
        "    G_test.add_edge(1, 2, length=10)\n",
        "    G_test.add_edge(1, 2, length=6)   # Shorter parallel edge\n",
        "    G_test.add_edge(2, 4, length=7)\n",
        "    G_test.add_edge(1, 3, length=5)\n",
        "    G_test.add_edge(3, 4, length=12)\n",
        "    \n",
        "    res = bidirectional_route(1, 4, G_test)\n",
        "    print('Synthetic Bidirectional Search result:', res)\n",
        "\n",
        "synthetic_bidirectional_test()\n"
    ],
    "outputs": []
}

# 4. Real-world demonstration markdown & code
real_md_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### Real-world Bidirectional Search demonstration on Pune road network\n",
        "\n",
        "We run Bidirectional Search between the first two matched groundwater locations from `pune_location_node_snap.csv` on the full Pune directed road graph.\n"
    ]
}

real_code_cell = {
    "cell_type": "code",
    "metadata": {},
    "execution_count": None,
    "source": [
        "if len(snap_df) >= 2:\n",
        "    src = int(snap_df.iloc[0]['nearest_node_id'])\n",
        "    dst = int(snap_df.iloc[1]['nearest_node_id'])\n",
        "    print(f'Running Bidirectional Search from node {src} to node {dst} …')\n",
        "    bidi_res = bidirectional_route(src, dst, G)\n",
        "    print('Bidirectional Search result:', bidi_res)\n",
        "else:\n",
        "    print('Not enough matched locations for a demo.')\n"
    ],
    "outputs": []
}

# Replace the placeholder cell with the new cells
nb['cells'][placeholder_idx:placeholder_idx+1] = [
    bidi_md_cell,
    bidi_code_cell,
    synthetic_md_cell,
    synthetic_code_cell,
    real_md_cell,
    real_code_cell
]

with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Successfully updated notebook with Bidirectional Search!')
