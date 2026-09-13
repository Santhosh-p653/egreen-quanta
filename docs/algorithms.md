# Algorithms used in this project

This document explains every algorithm used in the project, in plain
English, as simple numbered steps. Diagrams/images for each will be
added here later.

---

## 1. Building a road network from a set of points

**Used in:** `graph_model.py` (Phase 1, random points), `cvrp_graph.py`
(Phase 2, real coordinates)

We don't assume every location is directly connected to every other
location by a road — that's not realistic. Instead we build a **sparse
graph** where each point only connects to its nearest neighbors.

**Steps:**
1. Take a list of points (intersections, or customer locations).
2. For each point, measure the distance to every other point.
3. Connect each point to its `k` closest points only (e.g. its 4
   nearest neighbors) — not to every point.
4. Check if the whole network is connected (you can reach any point
   from any other point). If some points are cut off into separate
   islands, add one extra connecting road between each island so the
   whole map is reachable.
5. Store the straight-line distance of each road as its base travel
   time/cost.

**Result:** a realistic road network graph, not a "fly directly
anywhere" map.

---

## 2. Simulating traffic congestion

**Used in:** `graph_model.py` (`apply_congestion`)

**Steps:**
1. For every road (edge) in the graph, pick a random congestion
   multiplier between 1.0 (free-flowing) and 2.5 (heavy traffic).
2. Multiply the road's base travel time by this multiplier to get its
   actual current travel time.
3. This is redone every time you run a new simulation, so each run
   represents a different traffic snapshot.

**Result:** the same road network behaves differently each time,
mimicking real-world traffic variation.

---

## 3. Dijkstra's algorithm (finding the shortest path)

**Used in:** `baseline.py`, and internally inside `qpso.py` /
`cvrp_qpso.py` to work out the cost between any two points

This is a well-known, exact algorithm — it always finds the truly
shortest path, guaranteed, no guessing involved.

**Steps:**
1. Start at the source point. Mark its distance as 0, and every other
   point's distance as "unknown/infinite" for now.
2. Look at all the roads leading out of the current point. For each
   neighbor, check: is going through the current point a shorter way
   to reach that neighbor than what we already know?
3. If yes, update that neighbor's distance to the shorter value.
4. Mark the current point as "done," and move to the nearest point
   that isn't done yet.
5. Repeat steps 2–4 until every reachable point has been visited.
6. The recorded distance to each point is now the shortest possible
   distance from the source.

**Why we use it here:** whenever QPSO or the baseline needs to know
"what's the cheapest way to get from point A to point B on this
graph," Dijkstra gives the exact answer. We precompute this for every
pair of important points (depot + waypoints/customers) once per run,
so it doesn't need to be recalculated over and over.

---

## 4. Nearest-Neighbor heuristic (classical baseline)

**Used in:** `baseline.py` (Phase 1), `cvrp_baseline.py` (Phase 2)

This is the simplest possible route-building strategy — it's what
QPSO is benchmarked against.

**Steps:**
1. Start at the depot.
2. Look at every unvisited waypoint/customer. Pick whichever one is
   closest to your current location.
3. Travel there. Mark it as visited.
4. Repeat steps 2–3 until every waypoint/customer has been visited.
5. (Phase 2 only) Before picking the next customer, check if their
   demand would overload the vehicle. If it would, first return to
   the depot to reload, then continue.

**Why it's a fair but weak baseline:** it's fast and simple, but
"always go to the nearest place" is a greedy strategy — it can walk
itself into bad situations later in the route because it never plans
ahead. That's exactly the gap a smarter algorithm like QPSO is
expected to close.

---

## 5. QPSO — Quantum-behaved Particle Swarm Optimization

**Used in:** `qpso.py` (Phase 1), `cvrp_qpso.py` (Phase 2)

**Reference:** Sun, J., Feng, B., & Xu, W. (2004), *Particle swarm
optimization with particles having quantum behavior*, CEC 2004.

This is the core algorithm of the whole project. It's a real, published
optimization method — not something invented for this problem
statement. "Quantum-inspired" means it borrows the *mathematical shape*
of a quantum physics model to decide how solutions should move and
improve — it does not run on quantum hardware and does not need a
quantum computer or simulator.

### The idea in plain words

Imagine a swarm of "particles," where each particle represents one
possible route. All particles start with a random guess. On every
round:
- Each particle remembers the best route *it personally* has found so
  far.
- The whole swarm remembers the best route *anyone* has found so far.
- Every particle then nudges itself toward a blend of its own best
  and the swarm's best — with some randomness sprinkled in so the
  swarm doesn't all collapse onto the same answer too quickly.

Over many rounds, the swarm gradually converges on a very good route.

### Steps

1. Create a swarm of particles. Each particle is a list of random
   numbers — one number per waypoint/customer.
2. Turn each particle's numbers into an actual route: sort the
   numbers from smallest to largest, and visit the waypoints in that
   sorted order. (This trick is called "priority-based encoding" —
   see section 6.)
3. Work out how good each particle's route is (its "cost" — total
   travel time or distance, calculated using Dijkstra's shortest-path
   costs).
4. Remember each particle's personal best route so far, and the whole
   swarm's best route so far.
5. For every particle, on every round:
   a. Pick a random blend point between the particle's personal best
      and the swarm's overall best.
   b. Move the particle's numbers toward that blend point, by a random
      amount that shrinks as the rounds go on (lots of exploring early
      on, more fine-tuning later).
   c. Decode the particle's new numbers into a route again (step 2),
      and check its cost again.
   d. If this is better than the particle's personal best, update it.
      If it's also better than the swarm's overall best, update that
      too.
6. Repeat step 5 for a fixed number of rounds (iterations).
7. After the last round, the swarm's best-ever route is the answer.

### What makes it "quantum-inspired" specifically

Older, classical swarm algorithms move each particle using a
"velocity" (like real-world momentum — it keeps drifting in whatever
direction it was already going). QPSO removes velocity entirely.
Instead, each particle's next position is treated like a
particle-in-a-well from quantum physics: it can jump anywhere around
the blend point, with jumps more likely to land close to it than far
away. This lets the swarm explore more freely and helps it avoid
getting stuck on a decent-but-not-great answer.

---

## 6. Priority-based encoding (turning numbers into a route)

**Used in:** inside `qpso.py` / `cvrp_qpso.py`

QPSO naturally works with lists of real numbers, but a route is an
*order* to visit places in — not a list of numbers. This encoding
bridges the two.

**Steps:**
1. Give each waypoint/customer one random number (its "priority").
2. Sort the waypoints/customers by their number, smallest to largest.
3. The sorted order is the visiting order.

**Why this works:** whenever QPSO nudges a particle's numbers, the
*order* they sort into can change too — so QPSO is really searching
over all possible visiting orders, just represented as numbers instead
of directly as a list of stops.

---

## 7. Multi-trip capacity handling (the constraint)

**Used in:** `cvrp_qpso.py`, `cvrp_baseline.py`

The real CVRP dataset gives each customer a demand (how much they
need delivered) and the vehicle a maximum capacity. A single vehicle
can't just keep loading forever — eventually it has to go back to the
depot to reload. This is the project's constraint-handling piece.

**Steps:**
1. Start at the depot with an empty vehicle (load = 0).
2. Go through the planned visiting order one customer at a time.
3. Before visiting the next customer, check: would delivering to them
   push the vehicle's load over its capacity?
4. If yes — first travel back to the depot, reset the load to 0 (a
   "reload trip"), then continue to that customer.
5. If no — just go straight to that customer and add their demand to
   the current load.
6. After the last customer, return to the depot one final time.

**Why this matters for QPSO specifically:** because the number and
placement of these forced reload trips depends entirely on the
*order* customers are visited in, a smarter visiting order can mean
fewer, better-timed reload trips — which is a real optimization
problem, not just a pass/fail check. This is what QPSO and the
Nearest-Neighbor baseline are both trying to minimize (total travel
cost, including any reload trips).

---

## 8. Benchmarking methods

**Used in:** `benchmark.py` (Phase 1), `cvrp_benchmark.py` (Phase 2)

A single run's result isn't reliable proof — it could just be a lucky
or unlucky roll of the dice. These methods gather enough evidence to
make a real claim.

### Multi-seed benchmark (Phase 1)

**Steps:**
1. Pick a fixed problem size (same number of nodes/waypoints).
2. Run QPSO and the baseline several times, each time with a
   different random seed (different random graph/traffic each time).
3. Record the % improvement of QPSO over the baseline in every run.
4. Report the average improvement, how much it varies (standard
   deviation), and how many runs QPSO actually won.

### Scalability sweep (Phase 1)

**Steps:**
1. Pick a range of problem sizes (e.g. 10, 20, 30, 40, 50 nodes).
2. Run QPSO and the baseline once at each size.
3. Record improvement % and runtime at each size.
4. Plot both against problem size, to see whether QPSO's advantage
   holds up (or grows) as the problem gets bigger, and how much slower
   it gets.

### Multi-instance benchmark (Phase 2)

**Steps:**
1. Take several real instances from the CVRP dataset (not randomly
   generated — actual pre-built test cases).
2. Run QPSO and the baseline on each instance.
3. Record cost, number of reload trips, and improvement % for each.
4. Report the average improvement, how much it varies, and how many
   instances QPSO won — this is evidence the algorithm works on real
   data, not just synthetic test cases built to favor it.
