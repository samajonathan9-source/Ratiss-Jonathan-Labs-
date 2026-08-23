"""Run a reproducible RATISS inspection experiment on real Berlin52 coordinates."""
from __future__ import annotations

import argparse
import json
import os
import sys
from itertools import combinations
from pathlib import Path
from typing import Any

import numpy as np


def load_engine(engine_src: str | None):
    candidate = engine_src or os.environ.get("RATISS_ENGINE_SRC")
    if candidate:
        sys.path.insert(0, str(Path(candidate).expanduser().resolve()))
    try:
        from ratiss_topological_decoherence.topology import topology_from_correlation
        from ratiss_topological_decoherence.tsp import inspection_route
    except ImportError as error:
        raise RuntimeError("Set RATISS_ENGINE_SRC or --engine-src to the Studio Cloud src directory.") from error
    return topology_from_correlation, inspection_route


def parse_tsplib(path: str | Path) -> tuple[str, np.ndarray]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    name = next((line.split(":", 1)[1].strip() for line in lines if line.startswith("NAME")), "unknown")
    try:
        start = lines.index("NODE_COORD_SECTION") + 1
    except ValueError as error:
        raise ValueError("TSPLIB coordinate section missing.") from error
    points: list[list[float]] = []
    for line in lines[start:]:
        if line.strip() == "EOF":
            break
        tokens = line.split()
        if len(tokens) >= 3:
            points.append([float(tokens[1]), float(tokens[2])])
    if len(points) < 3:
        raise ValueError("At least three coordinate rows are required.")
    return name, np.asarray(points, dtype=float)


def distance(points: np.ndarray) -> np.ndarray:
    delta = points[:, None, :] - points[None, :, :]
    return np.linalg.norm(delta, axis=2)


def route_cost(route: list[int], dist: np.ndarray) -> float:
    return float(sum(dist[route[index], route[index + 1]] for index in range(len(route) - 1)))


def nearest_neighbor_2opt(dist: np.ndarray) -> dict[str, Any]:
    remaining = set(range(1, len(dist)))
    route = [0]
    while remaining:
        current = route[-1]
        nxt = min(remaining, key=lambda node: (dist[current, node], node))
        route.append(nxt)
        remaining.remove(nxt)
    route.append(0)
    improved = True
    while improved:
        improved = False
        for left, right in combinations(range(1, len(route) - 1), 2):
            a, b, c, d = route[left - 1], route[left], route[right], route[right + 1]
            if dist[a, c] + dist[b, d] + 1e-12 < dist[a, b] + dist[c, d]:
                route[left:right + 1] = reversed(route[left:right + 1])
                improved = True
    return {"path": route, "cost": route_cost(route, dist), "method": "nearest_neighbor_2opt"}


def geometric_affinity(dist: np.ndarray) -> np.ndarray:
    positive = dist[np.triu_indices(len(dist), 1)]
    scale = float(np.median(positive))
    matrix = np.exp(-dist / max(scale, 1e-12))
    np.fill_diagonal(matrix, 1.0)
    return matrix


def run_experiment(topology_from_correlation: Any, inspection_route: Any, path: str | Path, inspection_size: int) -> dict[str, Any]:
    name, points = parse_tsplib(path)
    dist = distance(points)
    affinity = geometric_affinity(dist)
    topology = topology_from_correlation(affinity)
    support = (affinity.sum(axis=1) - 1.0) / max(1, len(points) - 1)
    node_ids = np.argsort(support, kind="stable")[:inspection_size].astype(int).tolist()
    positions = [[float(x), float(y), 0.0] for x, y in points]
    inspection = inspection_route(positions, node_ids)
    baseline = nearest_neighbor_2opt(dist)
    return {
        "schema": "ratiss.tsp.inspection.v1",
        "provenance": {
            "source": "TSPLIB Berlin52 coordinates",
            "source_file": str(path),
            "validated_on_hardware": False,
            "claim_boundary": "RATISS route prioritizes structural inspection; it is not a claim of a faster global TSP solver.",
        },
        "instance": {"name": name, "n_cities": int(len(points)), "coordinates": points.tolist()},
        "geometric_affinity": {"model": "exp_negative_euclidean_distance_over_median", "matrix": affinity.tolist()},
        "ratiss_topology": topology,
        "inspection_selection": {"criterion": "lowest mean geometric affinity", "nodes": node_ids, "support": support.tolist()},
        "ratiss_inspection_route": inspection,
        "global_heuristic_baseline": baseline,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run RATISS inspection route on Berlin52.")
    parser.add_argument("--engine-src")
    parser.add_argument("--input", default="data/berlin52.tsp")
    parser.add_argument("--output", default="artifacts/berlin52_ratiss_inspection.json")
    parser.add_argument("--inspection-size", type=int, default=10)
    args = parser.parse_args()
    if not 2 <= args.inspection_size <= 10:
        raise ValueError("--inspection-size must be between 2 and 10 for an exact local inspection route.")
    topology_from_correlation, inspection_route = load_engine(args.engine_src)
    result = run_experiment(topology_from_correlation, inspection_route, args.input, args.inspection_size)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Wrote {destination} for {result['instance']['n_cities']} cities.")


if __name__ == "__main__":
    main()
