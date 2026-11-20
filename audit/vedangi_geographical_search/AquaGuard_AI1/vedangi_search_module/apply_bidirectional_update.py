import json, sys, os

nb_path = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module\AI_Search_Algorithms.ipynb'

with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Locate the placeholder markdown for Bidirectional Search
placeholder_idx = None
for i, cell in enumerate(nb.get('cells', [])):
    if cell.get('cell_type') == 'markdown' and any('Bidirectional Search' in line for line in cell.get('source', [])):
        placeholder_idx = i
        break
if placeholder_idx is None:
    print('Placeholder not found')
    sys.exit(1)

# Replace placeholder with explanation markdown
md_cell = {
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "### 6️⃣ Bidirectional Search\n",
        "\n",
        "**Explanation**\\n",
        "Bidirectional Search runs two simultaneous searches: one forward from the start node following outgoing edges, and one backward from the goal node following incoming edges (predecessors). When the two frontiers intersect, a complete path from start to goal is obtained by concatenating the forward and backward partial paths.\\n",
        "\n",
        "- The algorithm is complete once the frontiers meet; the first meeting yields a shortest‑edge path because each side expands in BFS order.\\n",
        "- It is efficient when the start and goal are far apart, as each search explores roughly half the graph.\\n",
        "- The backward search respects one‑way restrictions by traversing predecessor links only.\\n"
    ]
}
nb['cells'][placeholder_idx] = md_cell

# Code cell implementing bidirectional BFS
code_cell = {
    "cell_type": "code",
    "metadata": {},
    "execution_count": None,
    "source": [
        "import time, collections\\n",
        "\n",
        "def bidirectional_route(start_node: int, target_node: int, G: nx.MultiDiGraph = None) -> dict:\n",
        "    \"\"\"Bidirectional BFS on a directed MultiDiGraph. Returns dict with keys: success, route, distance_m, expanded_nodes, edge_count, time_s.\"\"\"\\n",
        "    if G is None:\n",
        "        G = globals().get('G')\\n",
        "    result = {\n",
        "        'success': False,\n",
        "        'route': [],\n",
        "        'distance_m': 0.0,\n",
        "        'expanded_nodes': 0,\n",
        "        'edge_count': 0,\n",
        "        'time_s': 0.0,\n",
        "    }\n",
        "    if start_node not in G or target_node not in G:\n",
        "        return result\n",
        "    if start_node == target_node:\n",
        "        result.update({\n",
        "            'success': True,\n",
        "            'route': [start_node],\n",
        "            'expanded_nodes': 0,\n",
        "            'edge_count': 0,\n",
        "            'time_s': 0.0,\n",
        "        })\n",
        "        return result\n",
        "    start_time = time.time()\n",
        "    # Frontiers and visited dictionaries\n",
        "    frontier_f = collections.deque([start_node])\n",
        "    frontier_b = collections.deque([target_node])\n",
        "    visited_f = {start_node: None}  # node -> predecessor\n",
        "    visited_b = {target_node: None}  # node -> successor towards target\n",
        "    expanded = 0\n",
        "    meeting_node = None\n",
        "    while frontier_f and frontier_b:\n",
        "        # Expand forward layer\n",
        "        for _ in range(len(frontier_f)):\n",
        "            current = frontier_f.popleft()\n",
        "            expanded += 1\n",
        "            for succ in G.successors(current):\n",
        "                if succ not in visited_f:\n",
        "                    visited_f[succ] = current\n",
        "                    frontier_f.append(succ)\n",
        "                if succ in visited_b:\n",
        "                    meeting_node = succ\n",
        "                    break\n",
        "            if meeting_node is not None:\n",
        "                break\n",
        "        if meeting_node is not None:\n",
        "            break\n",
        "        # Expand backward layer (predecessors)\n",
        "        for _ in range(len(frontier_b)):\n",
        "            current = frontier_b.popleft()\n",
        "            expanded += 1\n",
        "            for pred in G.predecessors(current):\n",
        "                if pred not in visited_b:\n",
        "                    visited_b[pred] = current\n",
        "                    frontier_b.append(pred)\n",
        "                if pred in visited_f:\n",
        "                    meeting_node = pred\n",
        "                    break\n",
        "            if meeting_node is not None:\n",
        "                break\n",
        "        if meeting_node is not None:\n",
        "            break\n",
        "    # Reconstruct full path if meeting found\n",
        "    if meeting_node is not None:\n",
        "        # forward path start -> meeting\n",
        "        path_f = []\n",
        "        node = meeting_node\n",
        "        while node is not None:\n",
        "            path_f.append(node)\n",
        "            node = visited_f[node]\n",
        "        path_f.reverse()\n",
        "        # backward path meeting -> target\n",
        "        path_b = []\n",
        "        node = meeting_node\n",
        "        while node is not None:\n",
        "            nxt = visited_b[node]\n",
        "            if nxt is None:\n",
        "                break\n",
        "            path_b.append(nxt)\n",
        "            node = nxt\n",
        "        full_path = path_f + path_b\n",
        "        # compute distance using shortest edge lengths\n",
        "        total_dist = 0.0\n",
        "        for u, v in zip(full_path[:-1], full_path[1:]):\n",
        "            total_dist += _shortest_edge_length(G, u, v)\n",
        "        result.update({\n",
        "            'success': True,\n",
        "            'route': full_path,\n",
        "            'distance_m': total_dist,\n",
        "            'expanded_nodes': expanded,\n",
        "            'edge_count': len(full_path) - 1,\n",
        "            'time_s': time.time() - start_time,\n",
        "        })\n",
        "    else:\n",
        "        result.update({\n",
        "            'expanded_nodes': expanded,\n",
        "            'time_s': time.time() - start_time,\n",
        "        })\n",
        "    return result\n"
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
        "# Synthetic bidirectional test\n",
        "import networkx as nx\n",
        "G_test = nx.DiGraph()\n",
        "G_test.add_edges_from([\n",
        "    (1, 2), (2, 3), (3, 6),\n",
        "    (1, 4), (4, 5), (5, 6)\n",
        "])\n",
        "# parallel edges with lengths\n",
        "G_test.add_edge(2, 3, length=2)\n",
        "G_test.add_edge(2, 3, length=5)\n",
        "for u, v in G_test.edges():\n",
        "    if 'length' not in G_test[u][v]:\n",
        "        G_test[u][v]['length'] = 1\n",
        "def _shortest_edge_length(G, u, v):\n",
        "    data = G.get_edge_data(u, v)\n",
        "    if data is None:\n",
        "        return float('inf')\n",
        "    if isinstance(data, dict) and any(isinstance(k, int) for k in data):\n",
        "        return min(d.get('length', float('inf')) for d in data.values())\n",
        "    return data.get('length', float('inf'))\n",
        "res = bidirectional_route(1, 6, G_test)\n",
        "print('Synthetic Bidirectional result:', res)\n"
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
        "    print(f'Running Bidirectional Search from {src} to {dst} …')\n",
        "    real_res = bidirectional_route(src, dst, G)\n",
        "    print('Real‑world Bidirectional result:', real_res)\n",
        "else:\n",
        "    print('Not enough matched locations for real‑world demo.')\n"
    ],
    "outputs": []
}
nb['cells'].insert(placeholder_idx + 3, real_cell)

# Write back the updated notebook
with open(nb_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print('Bidirectional Search added to notebook.')
