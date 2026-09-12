# Setup

## 1. Colab (recommended for first tests)

Upload all 5 Python files to the Colab filesystem (drag into the Files
pane, or `files.upload()`): `graph_model.py`, `baseline.py`, `qpso.py`,
`benchmark.py`, `gradio_app.py`.

```python
!pip install -q networkx numpy matplotlib gradio
```

**Sanity check without any UI** (fastest way to confirm the algorithm works):

```python
from graph_model import build_random_graph, apply_congestion
from baseline import nearest_neighbor_route
from qpso import qpso_optimize

G = apply_congestion(build_random_graph(n_nodes=20, seed=1), seed=1)
depot, waypoints = 0, [3, 7, 11, 14, 18]

result = qpso_optimize(G, depot, waypoints, n_particles=30, n_iterations=100, seed=1)
nn_route, nn_cost, _ = nearest_neighbor_route(G, depot, waypoints)

print("QPSO cost:", result["cost"], "| NN baseline cost:", nn_cost)
```

**Launch the full UI:**

```python
!python gradio_app.py
```

`.launch(share=True)` in `gradio_app.py` prints a public
`https://xxxxx.gradio.live` link directly — no tunnel tool needed. Link is
valid for 72 hours.

**Command-line benchmark run** (no UI, prints a report):

```python
!python benchmark.py
```

## 2. Local machine

```bash
git clone <your-repo-url>
cd <repo>
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python gradio_app.py
```

This opens `http://127.0.0.1:7860` in your browser (and still prints a
`share=True` public link if you want to demo it remotely — remove
`share=True` in `gradio_app.py`'s last line if you don't want that).

## Recommended first test values

To sanity-check against a known result:

| Parameter | Value |
|---|---|
| Number of intersections (nodes) | 20 |
| Number of delivery waypoints | 5 |
| QPSO swarm size | 30 |
| QPSO iterations | 100 |
| Random seed | 1 |

Expect QPSO cost at or below the Nearest-Neighbor baseline, with the
convergence curve dropping sharply in the first ~20 iterations.

## Troubleshooting

- **`ModuleNotFoundError`** — re-run the `pip install` line; make sure all
  5 `.py` files are in the same working directory (Colab or local).
- **Gradio UI loads but plots are blank** — usually a matplotlib backend
  issue on some Colab runtimes; restart the runtime and re-run the pip
  install cell before anything else.
- **Different numbers than the reference table above** — expected if your
  `networkx`/`numpy` versions differ (graph generation RNG is
  version-sensitive); the *shape* of the result (QPSO ≤ baseline) should
  still hold.
