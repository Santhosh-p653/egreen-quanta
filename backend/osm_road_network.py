"""
osm_road_network.py — Real Coimbatore Road Network Graph
Provides authentic GPS coordinates (latitudes ~11.00-11.08° N, longitudes ~76.92-77.05° E)
and real arterial corridors of Coimbatore, Tamil Nadu, India.

Landmarks:
- Gandhipuram Central Bus Stand
- RS Puram (DB Road)
- Ukkadam Bus Stand
- Peelamedu (PSG Tech / Avinashi Road)
- Hope College Junction
- Singanallur Junction (Trichy Road)
- Saravanampatti Tech Corridor (Sathy Road)
- Coimbatore Junction Railway Station
- Coimbatore International Airport (CJB)
- Saibaba Colony (Mettupalayam Road)
- Ganapathy Bus Stop
- Ramanathapuram Junction
"""

import math
import numpy as np
import networkx as nx

# Real Coimbatore GPS coordinates (lat, lon) — Expanded Greater Metropolitan Network (~30 km radius)
COIMBATORE_LANDMARKS = {
    0: {"id": 0, "name": "Gandhipuram Central Hub", "lat": 11.0168, "lon": 76.9678, "desc": "Central Bus Terminus & Commercial Core"},
    1: {"id": 1, "name": "RS Puram (DB Road)", "lat": 11.0095, "lon": 76.9485, "desc": "Western Residential & Retail District"},
    2: {"id": 2, "name": "Ukkadam Transit Hub", "lat": 10.9890, "lon": 76.9610, "desc": "Southern Inter-City Bus Stand & Lake Corridor"},
    3: {"id": 3, "name": "Coimbatore Junction Railway", "lat": 10.9995, "lon": 76.9632, "desc": "Major Rail Terminus"},
    4: {"id": 4, "name": "Peelamedu (PSG Tech)", "lat": 11.0245, "lon": 77.0028, "desc": "Educational & Commercial Zone, Avinashi Rd"},
    5: {"id": 5, "name": "Hope College Junction", "lat": 11.0282, "lon": 77.0185, "desc": "Arterial Intersection, Avinashi Rd"},
    6: {"id": 6, "name": "Coimbatore Int. Airport (CJB)", "lat": 11.0300, "lon": 77.0434, "desc": "Civil Aerodrome & Eastern Gateway"},
    7: {"id": 7, "name": "Singanallur Junction", "lat": 10.9984, "lon": 77.0255, "desc": "Trichy Road Terminal & Industrial Corridor"},
    8: {"id": 8, "name": "Ramanathapuram Junction", "lat": 11.0025, "lon": 76.9890, "desc": "Trichy Road Central Connector"},
    9: {"id": 9, "name": "Saibaba Colony", "lat": 11.0289, "lon": 76.9421, "desc": "Mettupalayam Road North-West Hub"},
    10: {"id": 10, "name": "Ganapathy Commercial Hub", "lat": 11.0345, "lon": 76.9745, "desc": "Sathy Road Arterial Junction"},
    11: {"id": 11, "name": "Saravanampatti Tech Zone", "lat": 11.0792, "lon": 76.9964, "desc": "Northern IT Special Economic Zone"},
    12: {"id": 12, "name": "Kovaipudur Transit Hub", "lat": 10.9325, "lon": 76.9388, "desc": "South-West Residential & Institutional Valley"},
    13: {"id": 13, "name": "Kuniyamuthur Junction", "lat": 10.9632, "lon": 76.9530, "desc": "Palakkad Road Gateway & Western Ring Link"},
    14: {"id": 14, "name": "Sundarapuram Hub", "lat": 10.9520, "lon": 76.9810, "desc": "Pollachi Road Arterial Junction"},
    15: {"id": 15, "name": "Eachanari Industrial Zone", "lat": 10.9312, "lon": 76.9865, "desc": "Southern Heavy Engineering & SIDCO Industrial Hub"},
    16: {"id": 16, "name": "Podanur Rail Junction", "lat": 10.9645, "lon": 76.9892, "desc": "Historic Railway Division Terminus"},
    17: {"id": 17, "name": "Ondipudur Freight Terminal", "lat": 10.9992, "lon": 77.0515, "desc": "Eastern Trichy Road Logistics Yard"},
    18: {"id": 18, "name": "Sulur Aero Logistics Hub", "lat": 11.0280, "lon": 77.1260, "desc": "Far-East National Highway & Logistics Zone"},
    19: {"id": 19, "name": "Neelambur NH-544 Bypass", "lat": 11.0660, "lon": 77.0980, "desc": "National Highway 544 Express Interchange"},
    20: {"id": 20, "name": "Kalapatti Aerospace Zone", "lat": 11.0682, "lon": 77.0320, "desc": "Northern Precision Valve & Aerospace Cluster"},
    21: {"id": 21, "name": "CHIL SEZ (Keeranatham)", "lat": 11.0995, "lon": 77.0085, "desc": "Major Global IT Campus & Tech Park"},
    22: {"id": 22, "name": "Thudiyalur Junction", "lat": 11.0815, "lon": 76.9580, "desc": "Mettupalayam Highway (NH-181) Commercial Hub"},
    23: {"id": 23, "name": "Vadavalli Gateway", "lat": 11.0260, "lon": 76.9045, "desc": "Western Marudhamalai Foothills Arterial Link"},
    # Expanded Regional Logistics Corridor (50–70+ km Regional Radius)
    24: {"id": 24, "name": "Pollachi Logistics Terminal", "lat": 10.6609, "lon": 77.0048, "desc": "Southern Tier-2 Agro-Industrial & Kerala Gateway Hub (~42 km)"},
    25: {"id": 25, "name": "Kinathukadavu Industrial Bypass", "lat": 10.8214, "lon": 77.0201, "desc": "NH-83 Southern Manufacturing & Rail Bypass (~25 km)"},
    26: {"id": 26, "name": "Madukkarai Cement Corridor", "lat": 10.9020, "lon": 76.9580, "desc": "Heavy Minerals & Southern NH-544 Bypass Interchange (~18 km)"},
    27: {"id": 27, "name": "Walayar Interstate Border Post", "lat": 10.8520, "lon": 76.8550, "desc": "Tamil Nadu-Kerala Commercial Interstate Freight Gate (~28 km)"},
    28: {"id": 28, "name": "Siruvani Eco Valley (Alandurai)", "lat": 10.9410, "lon": 76.7950, "desc": "South-Western Western Ghats Foothills & Water Basin (~30 km)"},
    29: {"id": 29, "name": "Karamadai Agro Wholesale Market", "lat": 11.2435, "lon": 76.9582, "desc": "Northern Produce Exchange & NH-181 Freight Station (~28 km)"},
    30: {"id": 30, "name": "Mettupalayam Nilgiris Gateway", "lat": 11.3015, "lon": 76.9465, "desc": "Northern Mountain Freight Terminal & Rail Interchange (~36 km)"},
    31: {"id": 31, "name": "Annur Highway Junction", "lat": 11.2335, "lon": 77.1332, "desc": "North-Eastern Expressway Cross-Link & Powerloom Cluster (~32 km)"},
    32: {"id": 32, "name": "Karumathampatti Logistics Park", "lat": 11.1090, "lon": 77.1820, "desc": "Major 6-Lane NH-544 Central Warehouse & Distribution Terminal (~30 km)"},
    33: {"id": 33, "name": "Avinashi Industrial & Textile Hub", "lat": 11.1925, "lon": 77.2690, "desc": "Far North-Eastern National Expressway Freight Interchange (~42 km)"},
    34: {"id": 34, "name": "Tiruppur Border (Perumanallur)", "lat": 11.1780, "lon": 77.3340, "desc": "Global Export Apparel & Eastbound Freight Gateway (~48 km)"},
    35: {"id": 35, "name": "Palladam Freight Interchange", "lat": 11.0045, "lon": 77.2885, "desc": "South-Eastern Multi-Arterial Logistics & Poultry Exchange (~38 km)"},
}

# Real arterial road segments connecting landmarks (bidirectional edges with road names & speed limits)
COIMBATORE_ROAD_SEGMENTS = [
    # Avinashi Road Corridor (Eastbound arterial spine)
    (0, 4, {"road": "Avinashi Road", "speed_kmh": 45}),
    (4, 5, {"road": "Avinashi Road", "speed_kmh": 45}),
    (5, 6, {"road": "Avinashi Road / Airport Bypass", "speed_kmh": 55}),
    (6, 19, {"road": "Avinashi Road NH-544 Link", "speed_kmh": 65}),
    (19, 18, {"road": "NH-544 to Sulur Express Bypass", "speed_kmh": 70}),

    # DB Road / Cowley Brown Road / Cross Cut Road (Central-West connectors)
    (0, 1, {"road": "Cross Cut Rd / DB Rd", "speed_kmh": 35}),
    (1, 3, {"road": "Brooke Bond Rd / State Bank Rd", "speed_kmh": 35}),
    (0, 3, {"road": "Dr. Nanjappa Road", "speed_kmh": 40}),

    # Southern corridors (Ukkadam / Trichy Road / Palakkad Road)
    (3, 2, {"road": "Collectorate / Ukkadam Bypass", "speed_kmh": 40}),
    (2, 8, {"road": "Sungam Bypass / Valankulam Lake Rd", "speed_kmh": 50}),
    (3, 8, {"road": "Trichy Road (Flyover)", "speed_kmh": 45}),
    (8, 7, {"road": "Trichy Road Arterial", "speed_kmh": 50}),
    (7, 5, {"road": "Kamarajar Road (Singanallur-Hope College)", "speed_kmh": 40}),
    (7, 17, {"road": "Trichy Road Express", "speed_kmh": 55}),
    (17, 18, {"road": "Trichy Road (NH-81) to Sulur", "speed_kmh": 65}),

    # South-West & South Arterials (Kuniyamuthur, Kovaipudur, Eachanari)
    (2, 13, {"road": "Palakkad Main Road (NH-544)", "speed_kmh": 45}),
    (13, 12, {"road": "Kovaipudur Main Road", "speed_kmh": 45}),
    (13, 14, {"road": "Sundarapuram-Kuniyamuthur Link", "speed_kmh": 40}),
    (2, 14, {"road": "Pollachi Main Road (NH-83)", "speed_kmh": 45}),
    (14, 15, {"road": "Pollachi Road / Eachanari Bypass", "speed_kmh": 55}),
    (14, 16, {"road": "Madukkarai-Podanur Link", "speed_kmh": 40}),
    (16, 7, {"road": "Podanur-Singanallur Road", "speed_kmh": 40}),
    (15, 16, {"road": "Chettipalayam Industrial Link", "speed_kmh": 50}),

    # Northern Corridors (Mettupalayam Rd / Sathy Rd / IT Corridor)
    (1, 9, {"road": "NSR Road / Mettupalayam Rd", "speed_kmh": 40}),
    (0, 9, {"road": "100 Feet Road / NSR Connector", "speed_kmh": 40}),
    (9, 22, {"road": "Mettupalayam Road (NH-181)", "speed_kmh": 55}),
    (22, 11, {"road": "Vellakinar-Saravanampatti Link", "speed_kmh": 45}),
    (0, 10, {"road": "Sathy Road / Ganapathy Flyover", "speed_kmh": 45}),
    (9, 10, {"road": "Sanganoor Road / New 100ft Rd", "speed_kmh": 40}),
    (10, 11, {"road": "Sathy Road (NH 209)", "speed_kmh": 50}),
    (4, 10, {"road": "Peelamedu-Ganapathy Link", "speed_kmh": 35}),
    (11, 21, {"road": "Saravanampatti-CHIL SEZ Main Rd", "speed_kmh": 50}),
    (21, 20, {"road": "Keeranatham-Kalapatti Link", "speed_kmh": 50}),
    (5, 20, {"road": "Kalapatti Main Road", "speed_kmh": 45}),
    (20, 19, {"road": "Kalapatti-Neelambur Bypass", "speed_kmh": 60}),
    (6, 11, {"road": "Thottipalayam / IT Corridor Bypass", "speed_kmh": 50}),

    # Western Gateway Corridors (Vadavalli / Marudhamalai)
    (1, 23, {"road": "Thondamuthur / Vadavalli Road", "speed_kmh": 45}),
    (9, 23, {"road": "Edayarpalayam-Vadavalli Road", "speed_kmh": 40}),
    (23, 22, {"road": "Vadavalli-Thudiyalur Western Ring", "speed_kmh": 50}),
    (23, 13, {"road": "Perur-Kuniyamuthur Western Bypass", "speed_kmh": 45}),

    # Regional Corridors: South & Interstate West (~70 km scale)
    (15, 26, {"road": "NH-544 / Coimbatore Industrial Bypass", "speed_kmh": 65}),
    (26, 27, {"road": "NH-544 4-Lane Express (Walayar Border)", "speed_kmh": 75}),
    (15, 25, {"road": "NH-83 4-Lane to Kinathukadavu", "speed_kmh": 70}),
    (25, 24, {"road": "NH-83 Expressway to Pollachi Terminal", "speed_kmh": 75}),
    (12, 28, {"road": "Kovaipudur-Alandurai Foothills Link", "speed_kmh": 50}),
    (23, 28, {"road": "Thondamuthur-Siruvani Main Road", "speed_kmh": 50}),

    # Regional Corridors: North Nilgiris Expressway
    (22, 29, {"road": "NH-181 4-Lane to Karamadai Agro Market", "speed_kmh": 65}),
    (29, 30, {"road": "NH-181 Express to Mettupalayam Nilgiris Hub", "speed_kmh": 70}),

    # Regional Corridors: North-East & East Expressways (NH-544 6-Lane & State Highways)
    (21, 31, {"road": "SH-80 Express to Annur Highway Junction", "speed_kmh": 60}),
    (30, 31, {"road": "Mettupalayam-Annur State Highway", "speed_kmh": 65}),
    (31, 33, {"road": "Annur-Avinashi Connector Road", "speed_kmh": 65}),
    (19, 32, {"road": "NH-544 6-Lane to Karumathampatti Logistics Park", "speed_kmh": 80}),
    (32, 33, {"road": "NH-544 6-Lane to Avinashi Industrial Hub", "speed_kmh": 80}),
    (33, 34, {"road": "NH-544 / Perumanallur Tiruppur Freight Corridor", "speed_kmh": 75}),
    (18, 35, {"road": "NH-81 Trichy Corridor to Palladam Freight Interchange", "speed_kmh": 70}),
    (32, 35, {"road": "SH-166 Karumathampatti-Palladam Bypass", "speed_kmh": 65}),
    (24, 35, {"road": "SH-19 Pollachi-Palladam Regional Express", "speed_kmh": 70}),
]

BENCHMARK_SCENARIOS = {
    "cbd_express": {
        "name": "CBD Commercial Express (5 Stops, ~8 km)",
        "desc": "Short-radius central logistics loop across Gandhipuram core business hubs.",
        "source_id": 0,
        "stops": [1, 3, 4, 9, 10],
    },
    "metro_greater": {
        "name": "Greater Coimbatore Metro (12 Stops, ~32 km)",
        "desc": "Wide 32km metropolitan logistics circuit spanning North, South, East, and West hubs.",
        "source_id": 0,
        "stops": [1, 2, 6, 7, 11, 14, 15, 18, 19, 21, 22, 23],
    },
    "regional_conglomerate": {
        "name": "Regional Conglomerate (16 Stops, ~65 km — Maximum Scale)",
        "desc": "Cross-district regional supply chain spanning Pollachi, Mettupalayam, Avinashi, and Walayar.",
        "source_id": 0,
        "stops": [1, 6, 11, 15, 18, 19, 21, 24, 25, 27, 28, 29, 30, 32, 33, 34],
    },
    "interstate_cargo": {
        "name": "Interstate Freight Corridor (10 Stops, ~50 km)",
        "desc": "National highway freight transit connecting Walayar Kerala Border to Tiruppur Export Hub.",
        "source_id": 0,
        "stops": [2, 6, 15, 18, 19, 26, 27, 32, 33, 34],
    },
    "industrial_cargo": {
        "name": "Airport & Eastern Industrial Cargo (8 Stops, ~24 km)",
        "desc": "High-speed freight corridor connecting IT SEZ, Airport, and NH-544 logistics depots.",
        "source_id": 0,
        "stops": [4, 5, 6, 17, 18, 19, 20, 21],
    },
    "north_south": {
        "name": "North-South Arterial Spine (8 Stops, ~26 km)",
        "desc": "Traverses heavy commercial traffic corridors from Thudiyalur down to Eachanari SEZ.",
        "source_id": 0,
        "stops": [2, 7, 8, 9, 10, 14, 15, 22],
    },
    "western_suburbs": {
        "name": "Western Suburbs & Tech Valley (6 Stops, ~18 km)",
        "desc": "Western arterial transit loop connecting Vadavalli, Kovaipudur, and Peelamedu.",
        "source_id": 0,
        "stops": [1, 4, 9, 12, 13, 23],
    },
}


def haversine_distance_km(lat1, lon1, lat2, lon2):
    """Calculates great-circle distance between two GPS points in kilometers."""
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def build_coimbatore_graph(traffic_mode="real", seed=None):
    """
    Builds the NetworkX road graph for Coimbatore with genuine GPS coordinates.
    Weights are travel times in minutes = (distance_km / speed_kmh) * 60 * congestion_factor.
    """
    rng = np.random.default_rng(seed)
    G = nx.Graph()

    for node_id, data in COIMBATORE_LANDMARKS.items():
        G.add_node(node_id, **data)

    for u, v, attrs in COIMBATORE_ROAD_SEGMENTS:
        lat1, lon1 = COIMBATORE_LANDMARKS[u]["lat"], COIMBATORE_LANDMARKS[u]["lon"]
        lat2, lon2 = COIMBATORE_LANDMARKS[v]["lat"], COIMBATORE_LANDMARKS[v]["lon"]

        dist_km = haversine_distance_km(lat1, lon1, lat2, lon2)
        base_speed = attrs.get("speed_kmh", 40.0)
        base_time_min = (dist_km / base_speed) * 60.0

        if traffic_mode == "real":
            # Realistic Coimbatore congestion based on corridor location
            # Core commercial hubs (Gandhipuram, Cross Cut, Ukkadam) have higher peak congestion
            is_core = (u in [0, 1, 2, 3] or v in [0, 1, 2, 3])
            c_min = 1.3 if is_core else 1.05
            c_max = 2.4 if is_core else 1.8
            congestion = rng.uniform(c_min, c_max)
        else:
            congestion = 1.0

        effective_time = base_time_min * congestion

        G.add_edge(
            u, v,
            distance_km=dist_km,
            base_time_min=base_time_min,
            congestion=congestion,
            weight=effective_time,
            road=attrs["road"],
        )

    return G


def get_route_geometry(G, node_sequence):
    """
    Returns array of real [lat, lon] coordinates and total distance/time along the path.
    Interpolates intermediate road curves between nodes for smooth map rendering.
    """
    coordinates = []
    total_km = 0.0
    total_time_min = 0.0
    roads = []

    for i in range(len(node_sequence) - 1):
        u, v = node_sequence[i], node_sequence[i + 1]

        # Use shortest path on graph if u and v are not directly connected by single edge
        if not G.has_edge(u, v):
            subpath = nx.dijkstra_path(G, u, v, weight="weight")
        else:
            subpath = [u, v]

        for k in range(len(subpath) - 1):
            n1, n2 = subpath[k], subpath[k + 1]
            edge_data = G[n1][n2]
            total_km += edge_data["distance_km"]
            total_time_min += edge_data["weight"]
            if edge_data["road"] not in roads:
                roads.append(edge_data["road"])

            lat1, lon1 = G.nodes[n1]["lat"], G.nodes[n1]["lon"]
            lat2, lon2 = G.nodes[n2]["lat"], G.nodes[n2]["lon"]

            if not coordinates:
                coordinates.append([lat1, lon1])

            # Generate intermediate road points to avoid straight-line cross-country artifacts
            n_subpoints = 4
            for s in range(1, n_subpoints + 1):
                t = s / float(n_subpoints)
                # Apply slight realistic road curvature
                curve = math.sin(t * math.pi) * 0.0012
                inter_lat = (1 - t) * lat1 + t * lat2 + curve
                inter_lon = (1 - t) * lon1 + t * lon2 - curve * 0.5
                coordinates.append([inter_lat, inter_lon])

    return {
        "coordinates": coordinates,
        "total_distance_km": round(total_km, 2),
        "total_time_min": round(total_time_min, 1),
        "corridors": roads,
    }


if __name__ == "__main__":
    G = build_coimbatore_graph(traffic_mode="real", seed=42)
    print(f"Coimbatore Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    route = [0, 4, 5, 6]  # Gandhipuram -> Peelamedu -> Hope College -> Airport
    geom = get_route_geometry(G, route)
    print(f"Route distance: {geom['total_distance_km']} km")
    print(f"Route time: {geom['total_time_min']} min")
    print(f"Waypoints: {len(geom['coordinates'])} GPS coordinates")
