import json, sys

nb_path = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module\AI_Search_Algorithms.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Find placeholder markdown cell for IDDFS
placeholder_idx = None
for i, cell in enumerate(nb.get('cells', [])):
    if cell.get('cell_type') == 'markdown' and any('Iterative Deepening DFS (IDDFS)' in line for line in cell.get('source', [])):
        placeholder_idx = i
        break
if placeholder_idx is None:
    print('Placeholder not found')
    sys.exit(1)

# Replace placeholder markdown with detailed explanation cell
md_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 5️⃣ Iterative Deepening DFS (IDDFS)\n",
        "\n",
        "**Explanation**\n",
        "Iterative Deepening Depth‑First Search (IDDFS) combines the space efficiency of Depth‑First Search with the optimality (in terms of number of edges) of Breadth‑First Search. It repeatedly runs a depth‑limited DFS (DLS) with increasing depth limits until the goal is found or a maximum depth is reached. Each iteration expands nodes up to the current depth limit.\n",
        "\n",
        "- The algorithm expands nodes in a DFS order, but the depth limit ensures that the shallowest solution (fewest edges) is found first.\n",
        "- It does **not** guarantee the shortest road distance, only the minimum‑edge path within the depth bound.\n",
        "- The total number of expanded nodes is the sum of nodes expanded in each depth‑limited iteration.\n"
    ]
}
nb['cells'][placeholder_idx] = md_cell

# Code cell for IDDFS implementation
code_cell = {
    "cell_type": "code",
    "metadata": {},
    "execution_count": None,
    "source": [
        "import time\n",
        "\n",
        "def _dls(start, target, depth, G):\n",
        "    \"\"\"Depth‑limited DFS. Returns (found, path, nodes_expanded).\"\"\"\n",
        "    if depth < 0:\n",
        "        return False, [], 0\n",
        "    stack = [(start, [start])]\n",
        "    visited = set([start])\n",
        "    nodes_expanded = 0\n",
        "    while stack:\n",
        "        node, path = stack.pop()\n",
        "        nodes_expanded += 1\n",
        "        if node == target:\n",
        "            return True, path, nodes_expanded\n",
        "        if len(path) - 1 == depth:\n",
        "            continue\n",
        "        for succ in G.successors(node):\n",
        "            if succ not in visited:\n",
        "                visited.add(succ)\n",
        "                stack.append((succ, path + [succ]))\n",
        "    return False, [], nodes_expanded\n",
        "\n",
        "def iddfs_route(start_node, target_node, G, max_depth=20):\n",
        "    \"\"\"Iterative Deepening DFS route finder.\n",
        "    Returns dict with keys: success, route, distance_m, expanded_nodes, edge_count, time_s.\n",
        "    \"\"\"\n",
        "    if start_node not in G or target_node not in G:\n",
        "        return {\n",
        "            'success': False,\n",
        "            'route': [],\n",
        "            'distance_m': 0.0,\n",
        "            'expanded_nodes': 0,\n",
        "            'edge_count': 0,\n",
        "            'time_s': 0.0,\n",
        "            'error': 'Invalid start or target node'\n",
        "        }\n",
        "    start_time = time.time()\n",
        "    total_expanded = 0\n",
        "    for depth in range(max_depth + 1):\n",
        "        found, path, expanded = _dls(start_node, target_node, depth, G)\n",
        "        total_expanded += expanded\n",
        "        if found:\n",
        "            distance = 0.0\n",
        "            for u, v in zip(path[:-1], path[1:]):\n",
        "                distance += _shortest_edge_length(G, u, v)\n",
        "            return {\n",
        "                'success': True,\n",
        "                'route': path,\n",
        "                'distance_m': distance,\n",
        "                'expanded_nodes': total_expanded,\n",
        "                'edge_count': len(path) - 1,\n",
        "                'time_s': time.time() - start_time,\n",
        "            }\n",
        "    return {\n",
        "        'success': False,\n",
        "        'route': [],\n",
        "        'distance_m': 0.0,\n",
        "        'expanded_nodes': total_expanded,\n",
        "        'edge_count': 0,\n",
        "        'time_s': time.time() - start_time,\n",
        "        'error': f'No path found within depth {max_depth}'\n",
        "    }\n"
    ],
    "outputs": []
}
nb['cells'].insert(placeholder_idx + 1, code_cell)

# Synthetic test cell
synthetic_cell = {
    "cell_type": "code",
    "metadata": {},
    "execution_count": None,
    "source": [
        "# Synthetic graph test for IDDFS\n",
        "import networkx as nx\n",
        "G_test = nx.DiGraph()\n",
        "G_test.add_edges_from([(1, 2), (2, 3), (3, 4), (1, 5), (5, 4)])\n",
        "for u, v in G_test.edges():\n",
        "    G_test[u][v]['length'] = 1\n",
        "def _shortest_edge_length(G, u, v):\n",
        "    data = G.get_edge_data(u, v)\n",
        "    if data is None:\n",
        "        return float('inf')\n",
        "    if isinstance(data, dict) and any(isinstance(k, int) for k in data):\n",
        "        return min(d.get('length', float('inf')) for d in data.values())\n",
        "    return data.get('length', float('inf'))\n",
        "res = iddfs_route(1, 4, G_test, max_depth=3)\n",
        "print('Synthetic IDDFS result:', res)\n"
    ],
    "outputs": []
}
nb['cells'].insert(placeholder_idx + 2, synthetic_cell)

# Real‑world demonstration cell
real_cell = {
    "cell_type": "code",
    "metadata": {},
    "execution_count": None,
    "source": [
        "if len(snap_df) >= 2:\n",
        "    src = int(snap_df.iloc[0]['nearest_node_id'])\n",
        "    dst = int(snap_df.iloc[1]['nearest_node_id'])\n",
        "    print(f'Running IDDFS from {src} to {dst} (max_depth=30)')\n",
        "    real_res = iddfs_route(src, dst, G, max_depth=30)\n",
        "    print('Real‑world IDDFS result:', real_res)\n",
        "else:\n",
        "    print('Not enough matched locations for real‑world demo.')\n"
    ],
    "outputs": []
}
nb['cells'].insert(placeholder_idx + 3, real_cell)

# Write back the notebook
with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print('Notebook updated with IDDFS implementation.')
