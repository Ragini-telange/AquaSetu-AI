import os
import json
import sys
import osmnx as ox

# Approved bounding box (west, south, east, north)
min_lat = 17.893056
max_lat = 19.330556
min_lon = 73.375833
max_lon = 75.122778

bbox = (min_lon, min_lat, max_lon, max_lat)  # (west, south, east, north)
print('Downloading OSM road network (drive) for Pune bounding box...')

# Download graph; one‑way directionality is preserved by default for "drive"
G = ox.graph_from_bbox(bbox, network_type='drive', simplify=True)

print(f'Graph downloaded: {len(G.nodes)} nodes, {len(G.edges)} edges')
# Verify that each edge has a length attribute
missing_len = sum(1 for _, _, data in G.edges(data=True) if 'length' not in data)
print(f'Edges missing length attribute: {missing_len}')

# Save to GraphML
out_path = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module\pune_road_network.graphml'
ox.save_graphml(G, out_path)
print('Graph saved to', out_path)

# Reload to verify integrity
G2 = ox.load_graphml(out_path)
print('Reloaded graph:')
print(f'  Nodes: {len(G2.nodes)}')
print(f'  Edges: {len(G2.edges)}')
missing_len2 = sum(1 for _, _, d in G2.edges(data=True) if 'length' not in d)
print(f'  Edges missing length after reload: {missing_len2}')
print('Download and verification complete.')
