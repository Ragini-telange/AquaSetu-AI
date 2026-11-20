import osmnx as ox

G = ox.load_graphml(r"C:\\Users\\Vedangi\\Documents\\AquaGuard_AI1\\vedangi_search_module\\pune_road_network.graphml")
node_attrs = next(iter(G.nodes(data=True)))[1]
edge_attrs = next(iter(G.edges(data=True)))[2]
print('Node attribute keys:', list(node_attrs.keys()))
print('Edge attribute keys:', list(edge_attrs.keys()))
print('Graph size: nodes', G.number_of_nodes(), 'edges', G.number_of_edges())
