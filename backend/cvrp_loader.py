
"""
cvrp_loader.py
Loads the CVRP benchmark dataset (data/cvrp_10.npz) and exposes single
instances in a convenient form.

Dataset shape (per the uploaded file):
  locations          (N, 11, 2)  uint16   x/y coords, node 0 = depot
  demands            (N, 11)     uint16   demand per node (depot = 0)
  num_vehicles       (N,)        int64    always 1 in this dataset
  vehicle_capacities (N, 1)      int64    capacity per instance
  appear_times       (N, 11)     int64    all 0 (static, no time windows)
  map_size           (2,)        int64    e.g. [1000, 1000]
"""

import os
import numpy as np


def load_dataset(path=None):
    if path is None:
        local_path = os.path.join(os.path.dirname(__file__), "data", "cvrp_10.npz")
        if os.path.exists(local_path):
            path = local_path
        elif os.path.exists("backend/data/cvrp_10.npz"):
            path = "backend/data/cvrp_10.npz"
        else:
            path = "data/cvrp_10.npz"
    return np.load(path, allow_pickle=True)


def get_instance(data, idx):
    """Return a single CVRP instance as a plain dict:
      locations: (11, 2) array, node 0 is the depot
      demands:   (11,) array, demand per node (depot = 0)
      capacity:  scalar vehicle capacity
      customers: list of node indices 1..10 (excludes depot)
    """
    locations = data["locations"][idx]
    demands = data["demands"][idx]
    capacity = int(data["vehicle_capacities"][idx][0])
    n_nodes = locations.shape[0]
    customers = list(range(1, n_nodes))  # node 0 = depot

    return {
        "locations": locations,
        "demands": demands,
        "capacity": capacity,
        "customers": customers,
        "depot": 0,
    }


def num_instances(data):
    return data["locations"].shape[0]


if __name__ == "__main__":
    data = load_dataset()
    print(f"Total instances: {num_instances(data)}")
    inst = get_instance(data, 0)
    print(f"Instance 0: {len(inst['customers'])} customers, capacity={inst['capacity']}")
    print(f"Demands: {inst['demands']}")
    print(f"Total demand: {inst['demands'].sum()}")
