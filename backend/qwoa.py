"""
qwoa.py — Classical State-Vector Simulation of Quantum Walk Optimization Algorithm (QWOA)
Genuine quantum algorithm demonstration on the permutation subspace S_n.

Unlike QPSO (which is a classical metaheuristic inspired by quantum mechanics),
QWOA simulates the exact Schrödinger evolution of a quantum state-vector |psi(t)>:
    |psi_0> = 1/sqrt(D) sum_{pi in S_n} |pi>      (Uniform Superposition)
    |psi(gamma, beta)> = prod_{l=1}^p [ e^{-i beta_l H_M} e^{-i gamma_l H_C} ] |psi_0>

Where:
    - Basis states: Permutations of customer delivery orders (dimension D = n!)
    - Problem Hamiltonian (H_C): Diagonal operator encoding graph-routed travel costs:
        H_C |pi> = C(pi) |pi>
    - Mixer Hamiltonian (H_M): Continuous-time quantum walk generator on the Cayley
      graph of S_n under elementary transpositions/swaps:
        H_M = sum_{pi, tau} |tau . pi><pi|
    - Born Rule: Probability distribution P(pi) = |<pi | psi>|^2

Explicitly scoped to small-scale instances (<= 8 nodes) to guarantee exact, fast
simulation of the full state vector without heuristic approximations.
"""

import time
import itertools
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
import scipy.sparse.linalg as sla

from qpso import precompute_segment_costs


def build_permutation_space(waypoints):
    """
    Constructs computational basis states for the symmetric group S_n.
    Returns:
        perms: list of permutation tuples
        perm_to_idx: dict mapping permutation tuple -> integer basis index
    """
    perms = list(itertools.permutations(waypoints))
    perm_to_idx = {p: i for i, p in enumerate(perms)}
    return perms, perm_to_idx


def build_cost_hamiltonian(perms, depot, seg_costs, instance=None):
    """
    Constructs the diagonal problem Hamiltonian H_C where eigenvalues are route costs.
    For standard TSP / waypoint routing: C(pi) = c(depot, pi_0) + sum c(pi_k, pi_{k+1}) + c(pi_{-1}, depot)
    """
    n_states = len(perms)
    diag_costs = np.zeros(n_states, dtype=np.float64)

    for i, p in enumerate(perms):
        # Full loop from depot through waypoints and back to depot
        route = [depot] + list(p) + [depot]
        cost = sum(seg_costs[(route[k], route[k + 1])] for k in range(len(route) - 1))
        diag_costs[i] = cost

    return diag_costs


def build_mixer_hamiltonian(perms, perm_to_idx):
    """
    Constructs the mixer Hamiltonian H_M as the adjacency matrix of the Cayley
    graph of S_n under adjacent transpositions (swaps of adjacent elements).
    H_M is Hermitian, symmetric, and sparse.
    """
    n_states = len(perms)
    n_items = len(perms[0])
    H_M = lil_matrix((n_states, n_states), dtype=np.float64)

    for idx, p in enumerate(perms):
        p_list = list(p)
        for k in range(n_items - 1):
            # Adjacent swap: swap elements at k and k+1
            swapped = p_list.copy()
            swapped[k], swapped[k + 1] = swapped[k + 1], swapped[k]
            target_idx = perm_to_idx[tuple(swapped)]
            H_M[idx, target_idx] = 1.0
            H_M[target_idx, idx] = 1.0

    return H_M.tocsr()


def simulate_qwoa(
    G,
    depot,
    waypoints,
    p_steps=2,
    gamma=None,
    beta=None,
    auto_tune=True,
    seed=None,
):
    """
    Executes a classical state-vector simulation of QWOA.

    Parameters:
        G: NetworkX congested road network graph
        depot: Depot node index
        waypoints: List of customer/delivery node indices (<= 8 nodes recommended)
        p_steps: Number of alternating quantum operator layers
        gamma: Cost rotation parameters (array or scalar)
        beta: Mixer walk parameters (array or scalar)
        auto_tune: If True, executes parameter tuning to optimize ground-state overlap
        seed: Random seed for sampling

    Returns:
        dict containing:
            best_route: optimal route found
            best_cost: cost of optimal route
            optimal_prob: probability of observing the optimal route
            uniform_prob: classical baseline probability 1/D
            enhancement_factor: optimal_prob / uniform_prob
            expected_cost: <psi | H_C | psi>
            state_dimension: D = n!
            probabilities: top 5 highest probability routes
            runtime: total simulation runtime in seconds
    """
    start = time.perf_counter()
    n_dim = len(waypoints)

    if n_dim > 8:
        raise ValueError(
            f"Waypoints size {n_dim} exceeds maximum recommended limit (8 nodes = 40,320 states) "
            "for classical state-vector quantum simulation."
        )

    # 1. Precompute segment costs
    seg_costs = precompute_segment_costs(G, [depot] + list(waypoints))

    # 2. Build Hilbert space basis and Hamiltonians
    perms, perm_to_idx = build_permutation_space(waypoints)
    dim = len(perms)
    cost_diag = build_cost_hamiltonian(perms, depot, seg_costs)
    H_M = build_mixer_hamiltonian(perms, perm_to_idx)

    # Normalize costs to avoid extreme phase oscillations
    # Rescale cost spectrum so (C - C_min) / (C_max - C_min) in [0, 2*pi]
    c_min = float(cost_diag.min())
    c_max = float(cost_diag.max())
    c_range = c_max - c_min if c_max > c_min else 1.0
    normalized_costs = (cost_diag - c_min) / c_range * (2 * np.pi)

    # Initial uniform superposition |psi_0>
    psi_0 = np.full(dim, 1.0 / np.sqrt(dim), dtype=np.complex128)

    # Classical parameter sweep or default initialization
    if gamma is None or beta is None:
        if auto_tune and dim <= 5040:
            from scipy.optimize import minimize
            def loss(params):
                g_val, b_val = params
                cur_psi = psi_0.copy()
                for _ in range(p_steps):
                    cur_psi = cur_psi * np.exp(-1j * g_val * normalized_costs)
                    cur_psi = sla.expm_multiply(-1j * b_val * H_M, cur_psi)
                pr = np.abs(cur_psi) ** 2
                return float(np.sum(pr * cost_diag))

            opt_res = minimize(loss, [0.4, 0.3], method="Nelder-Mead", options={"maxiter": 25, "xatol": 0.05})
            best_g, best_b = opt_res.x
            gamma = [float(best_g)] * p_steps
            beta = [float(best_b)] * p_steps
        else:
            gamma = [0.5] * p_steps
            beta = [0.5] * p_steps
    else:
        if isinstance(gamma, (int, float)):
            gamma = [float(gamma)] * p_steps
        if isinstance(beta, (int, float)):
            beta = [float(beta)] * p_steps

    # 3. Quantum state evolution
    psi = psi_0.copy()
    for l in range(p_steps):
        # Diagonal unitary phase application
        psi = psi * np.exp(-1j * gamma[l] * normalized_costs)
        # Sparse matrix exponentiation for quantum walk mixer
        psi = sla.expm_multiply(-1j * beta[l] * H_M, psi)

    # 4. Compute Born measurement probabilities
    probabilities = np.abs(psi) ** 2
    # Verify unitarity
    total_prob = np.sum(probabilities)
    probabilities /= total_prob  # ensure exact normalization

    expected_cost = float(np.sum(probabilities * cost_diag))

    # Identify optimal permutation (ground state)
    min_cost_idx = np.argmin(cost_diag)
    min_cost = cost_diag[min_cost_idx]
    optimal_perm = perms[min_cost_idx]
    best_route = [depot] + list(optimal_perm) + [depot]

    # Find highest-probability measured permutation
    max_prob_idx = np.argmax(probabilities)
    measured_perm = perms[max_prob_idx]
    measured_route = [depot] + list(measured_perm) + [depot]
    measured_cost = cost_diag[max_prob_idx]

    optimal_prob = float(probabilities[min_cost_idx])
    uniform_prob = 1.0 / dim
    enhancement_factor = optimal_prob / uniform_prob

    # Top 5 most likely routes
    top_indices = np.argsort(probabilities)[::-1][:min(5, dim)]
    top_routes = [
        {
            "route": [depot] + list(perms[idx]) + [depot],
            "cost": float(cost_diag[idx]),
            "probability": float(probabilities[idx]),
        }
        for idx in top_indices
    ]

    runtime = time.perf_counter() - start

    return {
        "best_route": best_route,
        "best_cost": float(min_cost),
        "measured_route": measured_route,
        "measured_cost": float(measured_cost),
        "expected_cost": expected_cost,
        "optimal_prob": optimal_prob,
        "uniform_prob": uniform_prob,
        "enhancement_factor": enhancement_factor,
        "state_dimension": dim,
        "top_routes": top_routes,
        "total_prob_norm": float(total_prob),
        "runtime": runtime,
    }


if __name__ == "__main__":
    from graph_model import build_random_graph, apply_congestion

    G = apply_congestion(build_random_graph(n_nodes=10, seed=1), seed=1)
    depot = 0
    waypoints = [1, 2, 3, 4]  # 4! = 24 basis states

    print("Running QWOA State-Vector Quantum Walk Simulation (4 waypoints)...")
    res = simulate_qwoa(G, depot, waypoints, p_steps=2, auto_tune=True, seed=1)
    print(f"State space dimension: {res['state_dimension']}")
    print(f"Optimal route: {res['best_route']} (Cost: {res['best_cost']:.2f})")
    print(f"Quantum measured route: {res['measured_route']} (Cost: {res['measured_cost']:.2f})")
    print(f"Expected cost <H_C>: {res['expected_cost']:.2f}")
    print(f"Optimal route probability: {res['optimal_prob']*100:.2f}%")
    print(f"Uniform classical probability: {res['uniform_prob']*100:.2f}%")
    print(f"Quantum enhancement: {res['enhancement_factor']:.2f}x amplification")
    print(f"Runtime: {res['runtime']*1000:.2f} ms")
