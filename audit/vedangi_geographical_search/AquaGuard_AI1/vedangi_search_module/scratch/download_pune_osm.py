import os
import json
import sys
import pandas as pd
import osmnx as ox

# Bounding box values (approved)
min_lat = 17.893056
max_lat = 19.330556
min_lon = 73.375833
max_lon = 75.122778

print('Downloading OSM road network (drive) for Pune bounding box...')
# Use OSMnx to get graph; one-way directionality preserved by default
G = ox.graph_from_bbox(north=max_lat, south=min_lat, east=max_lon, west=min_lon,
                       network_type='drive', simplify=True)

print(f'Graph downloaded: {len(G.nodes)} nodes, {len(G.edges)} edges')
# Verify length attribute on edges
missing_length = 0
for u, v, data in G.edges(data=True):
    if 'length' not in data:
        missing_length += 1
print(f'Edges missing length attribute: {missing_length}')

# Save graph as GraphML
out_path = r'C:\Users\Vedangi\Documents\AquaGuard_AI1\vedangi_search_module\pune_road_network.graphml'
ox.save_graphml(G, out_path)
print('Graph saved to', out_path)

# Reload the saved GraphML to verify
G2 = ox.load_graphml(out_path)
print('Reloaded graph:')
print(f'  Nodes: {len(G2.nodes)}')
print(f'  Edges: {len(G2.edges)}')
# Verify length attribute again on reloaded graph
missing_length2 = sum(1 for _,_,d in G2.edges(data=True) if 'length' not in d)
print(f'  Edges missing length after reload: {missing_length2}')

# End
