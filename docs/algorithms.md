# Algorithms used in this prototype

## 1. Problem formulation

The transportation network is modelled as a weighted graph `G = (V, E)`
where nodes are intersections and edge weights are travel time in minutes.
A congestion multiplier (1.0–2.5×) is applied per edge to simulate
real-time traffic (see `graph_model.py`).

The routing problem solved here is a **single-vehicle waypoint-ordering
problem** — a simplified Vehicle Routing Problem (VRP): given a depot and
a set of delivery waypoints, find the visiting order that minimizes total
travel cost, where the cost between any two waypoints is the
shortest-path cost on the traffic graph. This is the smallest version of
VRP that still requires solving an NP-hard combinatorial ordering problem
(it reduces to a Traveling Salesman Problem on the waypoint set), which is
why it's a reasonable Level 1 scope before adding multi-vehicle capacity
constraints.

## 2. QPSO — Quantum-behaved Particle Swarm Optimization

**Reference:** Sun, J., Feng, B., & Xu, W. (2004), *Particle swarm
optimization with particles having quantum behavior*, CEC 2004.

This is the core algorithm this project is required to implement. It is a
real, published metaheuristic — not a name invented for this problem
statement. "Quantum-inspired" means it borrows the *mathematical form* of
a quantum mechanical model (a particle in a delta-potential well) to
derive an update rule for classical, non-quantum computation. It does not
run on quantum hardware and does not need a quantum simulator.

### Why not classical PSO?

Classical PSO updates each particle with a velocity term (inertia +
cognitive + social components). QPSO has **no velocity** — instead, each
particle's position is treated as the outcome of a quantum measurement
around a potential well centered between its personal best and the
swarm's global best. This removes several PSO hyperparameters (inertia
weight, velocity clamping) and, per the original paper and subsequent
literature, gives stronger global search behavior and helps avoid
premature convergence to local optima — which is the "stronger global
search, faster convergence" claim in the problem statement.

### Update rule (implemented in `qpso.py`)

For each particle `i`, each dimension `d`, each iteration:

```
mbest = mean(pbest across all particles)          # mean best position
phi   ~ U(0,1)
p     = phi * pbest[i] + (1 - phi) * gbest         # local attractor point
u     ~ U(0,1)
x[i]  = p ± beta * |mbest - x[i]| * ln(1/u)        # position update
```

- `pbest[i]` — this particle's best-ever position
- `gbest` — swarm's best-ever position
- `beta` — contraction-expansion coefficient, linearly annealed from
  `beta_max` (more exploration) to `beta_min` (more exploitation) over
  the run — this is QPSO's analogue of PSO's inertia weight schedule
- the `±` sign is chosen randomly per dimension (50/50), matching the
  probabilistic "collapse" interpretation in the original paper

### Encoding: how a route becomes a particle

VRP/TSP-style ordering problems aren't naturally continuous, but QPSO
operates on real-valued vectors. This project uses **priority-based
permutation encoding** (a standard technique for applying PSO-family
algorithms to ordering problems):

- Each particle is a real-valued vector, one value per waypoint
- `argsort()` of that vector gives the visiting order
- Fitness = total route cost (sum of shortest-path segment costs for
  depot → waypoint → waypoint → ... in that order)

This lets the continuous QPSO update rule search directly over the space
of possible visiting orders without needing a discrete/combinatorial
variant of the algorithm.

## 3. Classical baselines (`baseline.py`)

Two baselines are implemented, used for different purposes:

- **Dijkstra's algorithm** — exact shortest-path between two nodes. Used
  as (a) the segment-cost function QPSO's fitness relies on, and (b) a
  sanity-check baseline for pure point-to-point routing.
- **Nearest-Neighbor heuristic** — a classical greedy baseline for the
  waypoint-ordering problem: at each step, go to the closest unvisited
  waypoint. This is what QPSO's solution quality is benchmarked against
  in the Level 1 prototype. It's fast (no search/iteration) but generally
  suboptimal, which is exactly the gap a metaheuristic should close.

Per the problem statement's requirement to benchmark "against conventional
metaheuristics and exact methods" — Dijkstra covers the exact-method
requirement for the segment-cost subproblem; Nearest-Neighbor is the
Level 1 stand-in for "conventional metaheuristic," with GA/ACO as a
planned Level 2 addition (see `README.md` scope notes).

## 4. Benchmarking methodology (`benchmark.py`)

A single run's improvement number isn't reliable evidence on its own —
graph structure and waypoint placement are randomized per seed, so one
run could be a lucky or unlucky draw. Two benchmarking modes address this:

- **Multi-seed benchmark** — runs QPSO vs. baseline across N independent
  random seeds at a fixed problem size, and reports mean ± standard
  deviation of the improvement percentage, plus win rate (how many trials
  QPSO matched or beat the baseline in). This is the evidence for
  objective 3 in the problem statement ("improving convergence speed and
  solution quality compared with classical algorithms").
- **Scalability sweep** — runs one trial at each of several increasing
  node counts, tracking both improvement % and runtime as the graph
  grows. This is the evidence for objective 4 ("demonstrate scalability
  for smart-city logistics and intelligent transportation systems").

## 5. Convergence analysis

`qpso_optimize()` records the swarm's best-so-far cost at every iteration
(`history` in the returned dict). Plotting this against iteration count
is the standard way to show a metaheuristic's convergence behavior — how
quickly it approaches a good solution and whether it plateaus (indicating
convergence) or is still improving when the iteration budget runs out
(indicating more iterations, or a larger swarm, might help).
