import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

output_dir = r"C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module\outputs"
comparison_csv = os.path.join(output_dir, "search_algorithms_comparison.csv")
summary_csv = os.path.join(output_dir, "search_algorithms_summary.csv")

df_comp = pd.read_csv(comparison_csv)
df_sum = pd.read_csv(summary_csv)

# Filter out DFS for distance comparison in chart 1 because DFS traverses 1,141,240 m and skews everything
# We can show a clear bar chart of average distance across the other 5 algorithms, plus a full comparison

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Chart 1: Average Route Distance (excluding DFS outlier to show actual routing differences)
algs = df_sum['Algorithm'].tolist()
distances = df_sum['Avg Distance (m)'].tolist()

# Highlight A* as the true shortest path
colors = ['#4A90E2', '#D0021B', '#F5A623', '#2ECC71', '#9B59B6', '#1ABC9C']

# 1. Route Distance (Log scale to accommodate DFS cleanly)
ax1 = axes[0]
bars1 = ax1.bar(algs, distances, color=colors, edgecolor='black', alpha=0.85)
ax1.set_yscale('log')
ax1.set_ylabel('Average Route Distance in Metres (Log Scale)', fontsize=11, fontweight='bold')
ax1.set_title('Route Distance Comparison\n(A* guarantees shortest distance)', fontsize=12, fontweight='bold')
ax1.set_xticklabels(algs, rotation=35, ha='right', fontsize=9)
for bar in bars1:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval * 1.15, f"{int(yval):,}m", ha='center', va='bottom', fontsize=8, rotation=0)

# 2. Expanded Nodes (Log scale)
expanded = df_sum['Avg Expanded Nodes'].tolist()
ax2 = axes[1]
bars2 = ax2.bar(algs, expanded, color=colors, edgecolor='black', alpha=0.85)
ax2.set_yscale('log')
ax2.set_ylabel('Average Expanded Nodes (Log Scale)', fontsize=11, fontweight='bold')
ax2.set_title('Search Space Exploration\n(Greedy & Bidirectional expand fewest)', fontsize=12, fontweight='bold')
ax2.set_xticklabels(algs, rotation=35, ha='right', fontsize=9)
for bar in bars2:
    yval = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2.0, yval * 1.15, f"{int(yval):,}", ha='center', va='bottom', fontsize=8)

# 3. Execution Time (milliseconds)
time_ms = [t * 1000 for t in df_sum['Avg Time (s)'].tolist()]
ax3 = axes[2]
bars3 = ax3.bar(algs, time_ms, color=colors, edgecolor='black', alpha=0.85)
ax3.set_yscale('log')
ax3.set_ylabel('Average Execution Time in Milliseconds (Log Scale)', fontsize=11, fontweight='bold')
ax3.set_title('Runtime Performance\n(All < 1ms except DFS at ~57ms)', fontsize=12, fontweight='bold')
ax3.set_xticklabels(algs, rotation=35, ha='right', fontsize=9)
for bar in bars3:
    yval = bar.get_height()
    ax3.text(bar.get_x() + bar.get_width()/2.0, yval * 1.15, f"{yval:.3f}ms", ha='center', va='bottom', fontsize=8)

plt.tight_layout()
chart_path = os.path.join(output_dir, "search_algorithms_performance_comparison.png")
plt.savefig(chart_path, dpi=300)
plt.close()
print(f"Comparison chart saved to: {chart_path}")

# Generate a second per-pair breakdown chart
fig, (ax_d, ax_n) = plt.subplots(1, 2, figsize=(15, 6))

# Per pair distance for the 5 sensible routing algorithms (BFS, Greedy, A*, IDDFS, Bidirectional)
sensible_algs = ["BFS", "Greedy Best-First", "A*", "IDDFS", "Bidirectional Search"]
palette = {'BFS': '#4A90E2', 'Greedy Best-First': '#F5A623', 'A*': '#2ECC71', 'IDDFS': '#9B59B6', 'Bidirectional Search': '#1ABC9C'}

pairs = df_comp['pair_id'].unique()
x = np.arange(len(pairs))
width = 0.15

for i, alg in enumerate(sensible_algs):
    subset = df_comp[df_comp['algorithm'] == alg]
    dist_vals = [subset[subset['pair_id'] == p]['distance_m'].values[0] if len(subset[subset['pair_id'] == p]) > 0 else 0 for p in pairs]
    ax_d.bar(x + i*width - 2*width, dist_vals, width, label=alg, color=palette[alg], edgecolor='black', alpha=0.85)

ax_d.set_title('Route Distance by Pair (Metres)\n(A* strictly minimizes total road distance)', fontsize=11, fontweight='bold')
ax_d.set_xticks(x)
ax_d.set_xticklabels([f"{p}\n({df_comp[df_comp['pair_id']==p]['src_village'].iloc[0]}→{df_comp[df_comp['pair_id']==p]['dst_village'].iloc[0]})" for p in pairs], fontsize=9)
ax_d.set_ylabel('Distance (m)', fontsize=10)
ax_d.legend(fontsize=8)

for i, alg in enumerate(sensible_algs):
    subset = df_comp[df_comp['algorithm'] == alg]
    node_vals = [subset[subset['pair_id'] == p]['expanded_nodes'].values[0] if len(subset[subset['pair_id'] == p]) > 0 else 0 for p in pairs]
    ax_n.bar(x + i*width - 2*width, node_vals, width, label=alg, color=palette[alg], edgecolor='black', alpha=0.85)

ax_n.set_title('Nodes Expanded by Pair (Log Scale)\n(Bidirectional expands ~3x fewer than BFS)', fontsize=11, fontweight='bold')
ax_n.set_xticks(x)
ax_n.set_xticklabels([f"{p}\n({df_comp[df_comp['pair_id']==p]['src_village'].iloc[0]}→{df_comp[df_comp['pair_id']==p]['dst_village'].iloc[0]})" for p in pairs], fontsize=9)
ax_n.set_ylabel('Expanded Nodes (Log Scale)', fontsize=10)
ax_n.set_yscale('log')
ax_n.legend(fontsize=8)

plt.tight_layout()
breakdown_chart_path = os.path.join(output_dir, "search_algorithms_per_pair_breakdown.png")
plt.savefig(breakdown_chart_path, dpi=300)
plt.close()
print(f"Per-pair breakdown chart saved to: {breakdown_chart_path}")
