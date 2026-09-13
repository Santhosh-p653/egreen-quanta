# Intuition, Mathematics, and Failure Modes

This document goes one level deeper than `algorithms.md`. For every
algorithm used in the project, it covers:
- the **mathematical formulation** (the actual equations),
- the **underlying concept** (why the math is shaped this way),
- **edge cases and known failure modes**,
- what happens if a step in the algorithm were **removed or skipped**.

---

## 1. Sparse graph construction (k-Nearest-Neighbor connectivity)

### Mathematical formulation

Given a set of points `V = {v_1, ..., v_n}` with coordinates in 2D
space, define the distance between any two points as:

```
d(v_i, v_j) = sqrt( (x_i - x_j)^2 + (y_i - y_j)^2 )
```

For each node `v_i`, let `N_k(v_i)` be the set of its `k` nearest
neighbors by `d`. The graph's edge set is:

```
E = { (v_i, v_j) : v_j ∈ N_k(v_i) }  ∪  connectivity-repair edges
```

Edge weight (before congestion) is simply `d(v_i, v_j)`.

### Underlying concept

Real road networks are **sparse** — you can't drive in a straight
line from any point to any other point; you follow actual roads. A
full mesh (every point connected to every other point) would let any
algorithm "cheat" by taking a straight line, which erases the whole
reason to use Dijkstra or model traffic at all. The k-NN construction
forces the algorithm to actually route through intermediate points,
which is what makes shortest-path search meaningful in the first
place.

### Edge cases / where it can fail

- **Disconnected components:** with a small `k` and unlucky point
  placement, the graph can naturally split into separate "islands"
  that k-NN alone never connects (A's nearest neighbors might not
  include B, and vice versa, even though they're both isolated
  together). This is why a connectivity-repair step is required — see
  below.
- **k too small (e.g. k=1 or k=2):** the graph becomes close to a
  simple path or tree. Very few alternate routes exist, so Dijkstra's
  answer and the "obvious" answer converge — QPSO has almost nothing
  to optimize over, since there's barely more than one way to get
  anywhere.
- **k too large (approaching n-1):** the graph approaches a full mesh,
  which (as above) defeats the purpose — congestion and routing choices
  stop mattering much, because there's almost always a near-direct
  edge available.
- **Asymmetric neighbor relationships:** k-NN is not symmetric in
  general — `v_j` being one of `v_i`'s nearest neighbors doesn't mean
  `v_i` is one of `v_j`'s nearest neighbors. The implementation here
  adds the edge in both directions once either side qualifies, which
  is a deliberate simplification (real roads are usually two-way
  anyway) — but it means the resulting graph is slightly denser than a
  strict "mutual k-NN" graph would be.

### What happens if a step is removed

- **If the connectivity-repair step is removed:** Dijkstra will throw
  an error or silently return "unreachable" for any pair of nodes in
  different components. In `qpso_optimize`, this would surface as an
  infinite/undefined cost the moment a particle's route tries to cross
  between islands — either crashing the run or corrupting the
  optimization (since `∞` cost dominates and no particle can ever
  improve past it if the islands are unlucky).
- **If congestion is skipped (weights = raw distance only):** the
  problem reduces to a static shortest-path/TSP-like problem. QPSO and
  Dijkstra baselines would still work, but the "real-time traffic"
  framing from the problem statement is lost entirely — every run
  would give the identical graph, removing the need for repeated
  benchmarking runs at all (one run would represent every future run).

---

## 2. Congestion simulation

### Mathematical formulation

For each edge `(u, v)` with base weight `w_base(u, v) = d(u, v)`, draw
a congestion factor:

```
c(u, v) ~ Uniform(1.0, 2.5)
w(u, v) = w_base(u, v) × c(u, v)
```

### Underlying concept

Congestion is modelled as **multiplicative noise on top of distance**,
not as a completely separate quantity. This keeps the relative
ordering of "close" vs. "far" mostly intact (a nearby point rarely
becomes cheaper to reach than a far one purely from congestion, since
the multiplier range is bounded), while still injecting enough
variance that the optimal route can change between runs — which is
what makes multi-seed benchmarking meaningful instead of redundant.

### Edge cases / where it can fail

- **Congestion range too narrow:** if the multiplier range were, say,
  `(1.0, 1.05)`, congestion would barely perturb the graph, and QPSO
  vs. baseline results would look almost identical to the no-congestion
  case — congestion stops being a meaningful part of the problem.
- **Congestion range too wide (e.g. up to 10x):** a normally-short edge
  could become drastically more expensive than a normally-long detour,
  which can make the "nearest neighbor" baseline behave almost
  randomly (its whole strategy — go to what's geometrically closest —
  stops correlating with what's actually cheapest). This isn't wrong,
  but it changes what's being tested: less "traffic-aware routing,"
  more "routing under near-total distance/cost decorrelation."
- **Independence assumption:** each edge's congestion is drawn
  independently. Real traffic is spatially correlated — a jam on one
  road usually means nearby roads are also affected (an accident,
  rush hour across a whole district). This model doesn't capture that;
  it's closer to random noise than realistic traffic propagation.

### What happens if this step is removed

Without congestion, `w(u, v) = w_base(u, v)` always, so the graph is
static across every seed. Every "different seed" run would produce the
same graph structure and the same optimal answer (modulo the random
depot/waypoint sampling), making the multi-seed benchmark's whole
purpose — checking that QPSO's advantage isn't a fluke of one random
draw — much weaker, since the only randomness left would be *which*
points are chosen, not the cost of reaching them.

---

## 3. Dijkstra's algorithm

### Mathematical formulation

Given graph `G = (V, E)` with non-negative weights `w: E → ℝ⁺`, and a
source `s`, Dijkstra computes `dist(s, v)` for all `v ∈ V`, defined as
the minimum-weight path sum:

```
dist(s, v) = min over all paths P from s to v of  Σ_{(a,b) ∈ P} w(a, b)
```

It does this via the relaxation rule: for every edge `(u, v)`,

```
if dist(s, u) + w(u, v) < dist(s, v):
    dist(s, v) ← dist(s, u) + w(u, v)
```

applied in order of increasing `dist(s, u)` (always finalizing the
closest unfinalized node next).

### Underlying concept

The algorithm's correctness relies entirely on **non-negative edge
weights**. Once a node is finalized (its shortest distance is locked
in), Dijkstra never revisits it — this is only safe because no later
edge can make an already-found path even shorter (which would require
a negative weight to "undo" distance already travelled). This greedy
"finalize the closest node next" strategy is what makes it efficient.

### Edge cases / where it can fail

- **Negative edge weights:** would break correctness outright — a
  node could be finalized too early, before a cheaper path through a
  negative edge is discovered later. Not a concern here since all
  weights are distances × a positive congestion multiplier, both
  always positive, but worth noting if the model is ever extended
  (e.g. modelling a "reward" for using an HOV lane as a negative
  cost — that would silently break Dijkstra).
- **Ties in shortest distance:** when two paths have identical cost,
  Dijkstra returns whichever it happens to finalize first (an
  implementation/ordering detail) — this is invisible in the output
  but means "the shortest path" isn't always unique, only "a" shortest
  path is guaranteed.
- **Disconnected target:** if `v` isn't reachable from `s` at all
  (see graph construction edge cases above), `dist(s, v) = ∞`. Any
  code that doesn't check for this (like a route-cost function summing
  segment costs) will silently propagate `∞` or crash on arithmetic
  with it.

### What happens if this step is removed / replaced

If segment costs were computed as straight-line (Euclidean) distance
instead of Dijkstra shortest-path, the graph's sparsity and congestion
would become meaningless for the *optimization* — QPSO would only be
optimizing visiting order, with the underlying "cost" ignoring the
actual road network entirely (this was in fact the first version of
the CVRP integration, before Phase 2 explicitly required Dijkstra
routing — see `docs/algorithms.md`).

---

## 4. Nearest-Neighbor heuristic

### Mathematical formulation

Given current position `c` and remaining unvisited set `R`, the next
stop is:

```
next = argmin_{r ∈ R} cost(c, r)
```

repeated until `R = ∅`. Total route cost is the sum of all chosen
`cost(c, next)` transitions.

### Underlying concept

This is a **greedy algorithm** — it always makes the locally best
choice (closest next stop) without any lookahead or backtracking. It's
a reasonable baseline exactly because it's the simplest strategy a
human might intuitively use, and because its weakness (no global
planning) is precisely the gap a metaheuristic like QPSO is supposed
to close.

### Edge cases / where it can fail

- **The "long last edge" problem:** greedy nearest-neighbor
  construction is well known to strand the last one or two stops far
  from everything else, because early greedy choices "use up" the
  nearby options first. This can make its final route noticeably worse
  than optimal, even though every individual step looked reasonable at
  the time.
- **Ties:** if multiple unvisited points are equally close, the
  implementation picks whichever comes first in iteration order — an
  arbitrary tie-break, not a principled one.
- **Capacity interaction (Phase 2):** the greedy "closest next" rule
  and the "must reload before exceeding capacity" rule can conflict —
  the nearest unvisited customer might be exactly the one that would
  overload the vehicle, forcing a reload trip that a smarter,
  capacity-aware ordering might have avoided by visiting a
  slightly-farther, lower-demand customer first.

### What happens if this step is removed

There would be no baseline at all — QPSO's "improvement %" would have
nothing to be measured against, making every benchmark number
meaningless (a percentage improvement over nothing isn't a number).

---

## 5. QPSO — Quantum-behaved Particle Swarm Optimization

### Mathematical formulation

For particle `i`, dimension `d`, at iteration `t`:

```
mbest_t     = (1/M) Σ_{j=1}^{M} pbest_j,t          (mean of all personal bests)

φ ~ Uniform(0, 1)
p_{i,d}     = φ · pbest_{i,d} + (1 - φ) · gbest_d    (local attractor point)

u ~ Uniform(0, 1)
sign        = +1 or -1, each with probability 0.5
x_{i,d,t+1} = p_{i,d} + sign · β_t · |mbest_{t,d} - x_{i,d,t}| · ln(1/u)

β_t = β_max - (β_max - β_min) · (t / T)              (linear annealing)
```

where `M` = swarm size, `T` = total iterations, `pbest_i` = particle
`i`'s best-ever position, `gbest` = swarm's best-ever position.

### Underlying concept: why this specific form?

This update rule comes from modelling each particle as a quantum
particle trapped in a **delta-potential well** centered at `p`. In
quantum mechanics, such a particle doesn't have a fixed position — it
has a probability distribution over where it might be found, and that
distribution is a Laplace distribution with scale controlled by `β`.
Sampling from that distribution is exactly what the
`p ± β·|mbest - x|·ln(1/u)` formula does (this is the standard
inverse-CDF trick for sampling a Laplace-distributed random variable).

The practical effect: instead of "drifting" toward a good answer
(what velocity-based PSO does), each particle **teleports**
probabilistically, more likely near `p` but with a real chance of
landing far away. This is what gives QPSO stronger global exploration
than classical PSO — it doesn't get trapped following a single
momentum-driven trajectory.

`mbest` (the mean of all particles' personal bests) acts as a
population-level anchor — it keeps particles loosely aware of "where
the swarm as a whole has been succeeding," which is additional
information beyond just `pbest`/`gbest` alone, and is part of what
gives QPSO its improved global search behavior over plain PSO variants
that only use `pbest`/`gbest`.

`β`'s linear annealing from `β_max` to `β_min` controls the
**exploration-exploitation trade-off** over time: early on, `β` is
large, so jumps are big and the swarm spreads out and explores broadly.
Late in the run, `β` is small, so jumps shrink and particles fine-tune
around good solutions instead of jumping past them.

### Edge cases / where it can fail

- **Premature convergence anyway:** if `gbest` gets stuck in a local
  optimum early (bad luck in the first few iterations) and the swarm
  size is small, `mbest` and `pbest` values can all cluster around
  that same local optimum, shrinking the effective search radius even
  though `β` hasn't decayed much yet — the theoretical exploration
  guarantee is probabilistic, not absolute.
- **`u` near 0:** `ln(1/u)` blows up as `u → 0`, which would produce a
  huge, effectively-random jump. The implementation clips `u` to
  `[1e-6, 1]` specifically to prevent this from producing `inf`/`nan`
  positions — without this clip, a single unlucky `u` draw close to 0
  could occasionally send a particle to an absurd position, wasting
  that particle's turn (and, rarely, corrupting `gbest` if the
  resulting decoded route is nonsensically evaluated as good, though
  the fitness function's own bounds make that unlikely here).
- **Too few iterations for the problem size:** annealing `β` from max
  to min over `T` iterations assumes `T` is long enough for the swarm
  to actually converge. For larger problems (more customers/nodes), a
  fixed `T=100` may cut off the anneal schedule before the swarm has
  actually settled, leaving both exploration and exploitation
  under-done — this is visible directly in the convergence curve if it
  hasn't flattened by the last iteration.
- **Swarm size too small:** `mbest` is an average over `M` particles;
  with very small `M` (e.g. `M=5`), `mbest` is a noisy estimate and can
  swing a lot between iterations, making the search less stable.

### What happens if a step is removed

- **If `mbest` were removed (using only `pbest`/`gbest`):** this
  degrades toward something closer to a simpler PSO-like search — the
  swarm loses the population-level signal about where things have been
  working collectively, and is more prone to premature convergence
  around whichever single particle got lucky first.
- **If `β` annealing were removed (fixed `β` throughout):** a fixed
  high `β` means the swarm never settles — it keeps making large jumps
  even late in the run, so it may never fine-tune into a precise
  optimum (visible as a convergence curve that keeps jittering instead
  of flattening). A fixed low `β` means the swarm barely explores at
  all from the start, making it highly dependent on a lucky initial
  random spread — much more likely to converge to a mediocre local
  optimum.
- **If the random `sign` were removed (always `+`):** every particle
  would only ever move toward one side of `p`, halving the effective
  exploration space and introducing a directional bias with no
  theoretical justification — the Laplace-sampling interpretation
  would no longer hold.

---

## 6. Priority-based permutation encoding

### Mathematical formulation

Given a real-valued vector `x ∈ ℝ^n` (one value per
waypoint/customer), the decoded visiting order is:

```
order = argsort(x)
```

i.e., the permutation of indices that would sort `x` from smallest to
largest.

### Underlying concept

`argsort` is a **many-to-one mapping**: infinitely many real-valued
vectors decode to the same permutation (any vector with the same
relative ranking of values gives the same order). This is actually
useful — it means QPSO's continuous search space is smoothly connected
to the discrete space of permutations. Small moves in `x`-space
*usually* produce the same or a very similar order (since a small
nudge rarely changes which value is bigger than which), but
occasionally cross a "ranking boundary" and produce a genuinely
different order. This gives the search a mix of local refinement (most
moves) and occasional larger structural changes (rank-order flips) —
without those two behaviors being separately programmed.

### Edge cases / where it can fail

- **Redundant search space:** because many different `x` vectors
  decode to the identical order, QPSO can spend effort moving a
  particle within this "redundant" region without ever changing the
  actual route being evaluated — effectively wasted search steps
  from the route-quality perspective (though not wasted from the
  underlying continuous optimization's perspective).
- **Near-tied values:** when two entries in `x` are very close to
  each other, tiny floating-point differences decide their relative
  order — this makes the encoding sensitive to numerical precision
  right at rank boundaries, though it doesn't cause incorrect
  behavior, just added sensitivity there.
- **No direct control over "how different" two orders are:** a single
  small nudge could, in principle, swap the rank of the very first vs.
  very last customer if their values happen to cross — an encoding
  that guarantees only "nearby" swaps (like a true permutation-based
  operator) would behave more predictably, but priority-based encoding
  makes no such guarantee.

### What happens if this step is removed / replaced

Without an encoding scheme, QPSO's continuous position updates simply
couldn't be applied to a route-ordering problem at all — QPSO's math
is defined over real vectors, and "visit customer A, then B, then C"
isn't a real vector. Some encoding step is mandatory for applying
PSO-family algorithms to any ordering/permutation problem; priority-
based encoding is one common choice (others exist, like random-key
encoding — which this effectively is — or explicit swap/insertion
operators built directly for permutations, which would require
modifying QPSO's update rule itself rather than just the
encode/decode step).

---

## 7. Multi-trip capacity handling

### Mathematical formulation

Given a visiting order `(c_1, c_2, ..., c_m)`, current load `L`
(initialized to 0), and vehicle capacity `Q`:

```
for each customer c_i in order:
    if L + demand(c_i) > Q:
        route ← route + [depot]     (forced reload)
        L ← 0
    route ← route + [c_i]
    L ← L + demand(c_i)
route ← route + [depot]             (final return)
```

Total cost = sum of graph shortest-path costs between consecutive
stops in the resulting `route`.

### Underlying concept

This is a **repair mechanism**, not a penalty. Rather than letting an
infeasible route exist and punishing it with an added cost term (as
the very first version of this project did), this approach makes every
decoded route *automatically feasible* by construction — infeasibility
is architecturally impossible, because the moment a violation would
occur, a reload is inserted instead of allowing the violation. This
avoids needing to hand-tune a penalty weight (too small: infeasible
routes look artificially cheap; too large: it distorts the search
landscape and can make the optimizer overly conservative).

### Edge cases / where it can fail

- **A single customer's demand exceeds vehicle capacity:**
  `demand(c_i) > Q` on its own. This is a genuinely infeasible
  problem instance — no amount of reloading fixes it, since the
  vehicle can never carry that much even starting empty. The current
  implementation does not explicitly detect or flag this case; it
  would silently produce a route where that one delivery still
  "happens" in the cost sum despite being physically impossible in
  reality. This is a real gap, not just a theoretical one — worth an
  explicit check before treating results as valid.
- **Reload timing is locked to the given order:** the repair logic
  only ever *inserts* reloads, in the exact position dictated by the
  order QPSO/NN produced — it never reconsiders whether reloading
  *earlier* (before it's strictly forced) might produce a cheaper
  overall route (e.g., picking up a large order slightly out of
  otherwise-optimal sequence to avoid an awkward, expensive reload
  trip later). This means the algorithm optimizes order first and
  treats reload placement as a downstream consequence, not a jointly
  optimized decision — a real, if subtle, limitation.
- **Interaction with Nearest-Neighbor's greedy choice:** as noted in
  section 4, NN's "always pick the nearest feasible customer" rule can
  be forced into an early reload that a different, non-greedy choice
  might have delayed or avoided — meaning NN's trip count is not just
  a property of the instance, but partly an artifact of its own greedy
  strategy interacting with capacity.

### What happens if this step is removed

Without any capacity handling, both algorithms would happily construct
routes that violate vehicle capacity — over-promising what a single
vehicle can actually carry. This is precisely the deliverable gap
identified earlier in the project (see the "Constraint handling" row
in the deliverables table) — the problem statement explicitly requires
constraint handling, and removing this step means the "solution" isn't
actually implementable in the real world it claims to model.

---

## 8. Benchmarking methods

### Mathematical formulation

For a set of `N` trials (seeds or dataset instances) with QPSO cost
`q_i` and baseline cost `n_i`:

```
improvement_i = (n_i - q_i) / n_i × 100%

mean_improvement = (1/N) Σ improvement_i
std_improvement  = sqrt( (1/N) Σ (improvement_i - mean_improvement)^2 )
win_rate          = (count of i where q_i ≤ n_i) / N
```

### Underlying concept

A single `improvement_i` value is a **sample from a random process**
(random graph, random congestion, random depot/waypoint choice, or
random dataset instance) — reporting only one such sample is
statistically unfounded reasoning: you cannot distinguish "QPSO is
genuinely better" from "this particular random draw happened to favor
QPSO" without seeing the spread across multiple draws. `mean` and `std`
together describe both the central tendency and the reliability of
that tendency; `win_rate` is a simpler, more robust companion metric
that doesn't get distorted by one unusually large or small
`improvement_i` value (a mean can be pulled by outliers; a win rate
can't).

### Edge cases / where it can fail

- **Small `N`:** with very few trials (e.g. `N=3`), `std_improvement`
  and `win_rate` are both extremely noisy estimates themselves — a
  95%+ win rate from only 3 trials is far weaker evidence than the
  same win rate from 30 trials, even though the number looks identical.
- **Non-independent trials:** if `base_seed` values are close together
  or the random generator has hidden correlations between "different"
  seeds, trials aren't truly independent samples, which would make
  `std_improvement` an underestimate of the real variability.
- **Instance selection bias (Phase 2):** the multi-instance benchmark
  currently draws instances by index (e.g., `start_idx` through
  `start_idx + n_instances`), not by random sampling from the dataset.
  If the dataset's instances aren't randomly ordered (e.g., grouped by
  difficulty or capacity tightness), a fixed index range could
  systematically over- or under-represent certain instance types,
  biasing the benchmark's conclusions without it being obvious from
  the numbers alone.
- **Scalability sweep confound:** the scalability sweep changes node
  count *and* implicitly changes waypoint density, graph diameter, and
  congestion variance all at once (since a bigger graph naturally has
  different structural properties) — a change in improvement % as
  size grows can't be cleanly attributed to "problem size" alone
  without controlling for these correlated factors.

### What happens if these steps are removed

Without multi-seed/multi-instance repetition, every result in the
project would rest on a single, unrepeatable data point — indistinguishable
from cherry-picking a favorable run, even if no cherry-picking actually
occurred. This is precisely why the earlier single-run results in this
project ("QPSO beat baseline by 12.7%!") needed to be followed up with
these benchmarking methods before being treated as real evidence.
