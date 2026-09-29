"""
sampling.py
Design-of-experiments sampling strategies for generating parameter
combinations to test QPSO under — used to build "golden eval" runs
that are reproducible and cover the parameter space systematically,
instead of picking settings by hand or ad-hoc random seeds.

Three methods, each with different coverage properties:

- Latin Hypercube Sampling (LHS): stratifies each parameter dimension
  into equal intervals and ensures every interval is sampled exactly
  once per dimension. Good general-purpose coverage, cheap.
- Sobol sequence: a low-discrepancy quasi-random sequence — fills the
  parameter space more evenly than pure random sampling, and (unlike
  LHS) is deterministic/reproducible in a way that scales smoothly to
  more or fewer samples.
- Orthogonal Array (Taguchi L9(3^4)): a classical design-of-experiments
  table. Instead of continuous coverage, it picks a small, balanced set
  of factor-LEVEL combinations (each parameter discretized into 3
  levels: low/mid/high) such that every pair of factor levels appears
  together an equal number of times. This is the standard technique
  for getting strong signal about which parameters matter most from
  very few runs (9 runs for 4 factors here).
"""

import numpy as np
from scipy.stats import qmc

# Classic Taguchi L9(3^4) orthogonal array: 9 runs, 4 factors, 3 levels
# each (0=low, 1=mid, 2=high). Public-domain standard DOE table.
L9_3_4 = np.array([
    [0, 0, 0, 0],
    [0, 1, 1, 1],
    [0, 2, 2, 2],
    [1, 0, 1, 2],
    [1, 1, 2, 0],
    [1, 2, 0, 1],
    [2, 0, 2, 1],
    [2, 1, 0, 2],
    [2, 2, 1, 0],
])


def _scale_unit_to_range(unit_samples, param_ranges):
    """unit_samples: (n_samples, n_params) array in [0,1].
    param_ranges: list of (low, high, is_int) tuples.
    Returns scaled samples as a list of dicts is done by caller;
    this just scales the raw array."""
    scaled = np.empty_like(unit_samples)
    for j, (low, high, is_int) in enumerate(param_ranges):
        scaled[:, j] = low + unit_samples[:, j] * (high - low)
        if is_int:
            scaled[:, j] = np.round(scaled[:, j])
    return scaled


def lhs_samples(param_names, param_ranges, n_samples, seed=1):
    sampler = qmc.LatinHypercube(d=len(param_names), seed=seed)
    unit = sampler.random(n=n_samples)
    scaled = _scale_unit_to_range(unit, param_ranges)
    return [dict(zip(param_names, row)) for row in scaled]


def sobol_samples(param_names, param_ranges, n_samples, seed=1):
    sampler = qmc.Sobol(d=len(param_names), seed=seed)
    # Sobol works best with power-of-2 sample counts; round up and trim.
    m = int(np.ceil(np.log2(max(n_samples, 1))))
    unit = sampler.random_base2(m=m)[:n_samples]
    scaled = _scale_unit_to_range(unit, param_ranges)
    return [dict(zip(param_names, row)) for row in scaled]


def orthogonal_array_samples(param_names, param_ranges):
    """Uses the fixed L9(3^4) design — always 9 runs, exactly 4 factors.
    param_ranges here give (low, high, is_int) per factor; each factor's
    3 levels are (low, mid, high) of its range."""
    assert len(param_names) == 4, "L9(3^4) requires exactly 4 factors"
    samples = []
    for row in L9_3_4:
        sample = {}
        for j, level in enumerate(row):
            low, high, is_int = param_ranges[j]
            mid = (low + high) / 2
            value = [low, mid, high][level]
            if is_int:
                value = round(value)
            sample[param_names[j]] = value
        samples.append(sample)
    return samples


if __name__ == "__main__":
    names = ["n_particles", "n_iterations", "n_nodes", "k_neighbors"]
    ranges = [(10, 80, True), (20, 300, True), (10, 40, True), (2, 8, True)]

    print("LHS (5 samples):")
    for s in lhs_samples(names, ranges, 5, seed=1):
        print(" ", s)

    print("\nSobol (5 samples, rounded up to power of 2):")
    for s in sobol_samples(names, ranges, 5, seed=1):
        print(" ", s)

    print("\nOrthogonal Array L9(3^4) (9 samples, fixed):")
    for s in orthogonal_array_samples(names, ranges):
        print(" ", s)
