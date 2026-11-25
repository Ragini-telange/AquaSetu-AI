import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.services.regression_service import RegressionService
from app.services.spatial_service import SpatialService
from app.services.classification_service import ClassificationService
from app.services.routing_service import RoutingService
from app.schemas.spatial import NearestWellRequest
from app.schemas.routing import PuneRoutingRequest
from app.schemas.classification import WaterPotabilityRequest

print('1. Testing RegressionService...')
reg = RegressionService()
wells = reg.get_wells(limit=10)
dists = reg.get_districts()
details = reg.get_well_details('W153803073591301')
print(f'   Regression wells count: {len(reg.wells_metadata)}, districts: {len(dists)}')
print(f'   Sample well details: ID={details["well_id"]}, village={details["village"]}, records={len(details["historical_records"])}')

print('2. Testing SpatialService...')
spat = SpatialService()
locs = spat.get_locations(limit=10)
spat_dists = spat.get_districts()
nearest_resp = spat.find_nearest_wells(NearestWellRequest(latitude=18.5204, longitude=73.8567, max_results=3))
print(f'   Spatial locations count: {len(spat.locations_metadata)}, districts: {len(spat_dists)}')
print(f'   Nearest to Pune: {[w.village for w in nearest_resp.nearest_wells]}')

print('3. Testing ClassificationService...')
clf = ClassificationService()
sample_params = {
    'pH': 7.2,
    'Electrical_Conductivity': 600.0,
    'TDS': 384.0,
    'Total_Hardness': 180.0,
    'Calcium': 50.0,
    'Magnesium': 25.0,
    'Potassium': 4.5,
    'Chloride': 85.0,
    'Sulphate': 45.0,
    'Iron': 0.15,
    'Bicarbonate': 150.0,
    'Sodium': 35.0
}
res = clf.classify_potability(WaterPotabilityRequest(**sample_params))
print(f'   Classification: label={res.potability_label}, prob={res.probability_potable:.2f}, exceeded={len(res.exceeded_parameters)}')

print('4. Testing RoutingService...')
rout = RoutingService()
route_req = PuneRoutingRequest(start_node_id=12788595845, target_node_id=12788595830, algorithm='A*')
route_res = rout.find_route(route_req)
print(f'   Routing: success={route_res.success}, dist={route_res.total_distance_m:.1f}m, nodes={len(route_res.route_node_ids)}, edges={route_res.edge_count}')

print('\n>>> ALL 4 BACKEND MODULE SERVICES VERIFIED CLEANLY! <<<')
