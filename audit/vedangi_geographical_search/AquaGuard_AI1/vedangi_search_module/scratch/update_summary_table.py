import os
import pandas as pd

output_dir = r"C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module\outputs"
comp_csv = os.path.join(output_dir, "search_algorithms_comparison.csv")
summary_csv = os.path.join(output_dir, "search_algorithms_summary.csv")

df_comp = pd.read_csv(comp_csv)

summary_rows = []
order = ["BFS", "DFS", "Greedy Best-First", "A*", "IDDFS", "Bidirectional Search"]

for alg in order:
    sub = df_comp[df_comp['algorithm'] == alg]
    total_runs = len(sub)
    succ_runs = sub[sub['success'] == True]
    num_succ = len(succ_runs)
    
    # Distance and edges from SUCCESSFUL runs only
    avg_dist = succ_runs['distance_m'].mean() if num_succ > 0 else None
    avg_edges = succ_runs['edge_count'].mean() if num_succ > 0 else None
    
    # Expanded nodes and time over all attempts
    avg_nodes = sub['expanded_nodes'].mean()
    avg_time = sub['time_s'].mean()
    
    succ_rate_str = f"{num_succ}/{total_runs} ({int(num_succ/total_runs*100)}%)"
    
    summary_rows.append({
        'Algorithm': alg,
        'Success Rate': succ_rate_str,
        'Avg Distance (m)': round(avg_dist, 3) if avg_dist is not None else None,
        'Avg Edges': round(avg_edges, 1) if avg_edges is not None else None,
        'Avg Expanded Nodes': round(avg_nodes, 1),
        'Avg Time (s)': round(avg_time, 6),
        'Note': 'Failed on Pair 5 at max_depth=25; succeeds at depth 32 (30 edges, 15074.83m vs BFS 19 edges)' if alg == 'IDDFS' else 'All runs succeeded'
    })

df_summary = pd.DataFrame(summary_rows)
df_summary.to_csv(summary_csv, index=False)
print("Updated Summary Table:")
print(df_summary.to_string(index=False))
