"""Temporal drift and topological-resilience experiment on the real Berlin52 input."""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np


@dataclass(frozen=True)
class ResilienceProfile:
    steps: int = 10
    seed: int = 20260823
    coordinate_drift_fraction_of_median_distance: float = 0.003
    final_association_noise_std: float = 0.22
    final_false_edge_fraction: float = 0.06
    collapse_ratio: float = 0.50


def load_engine(engine_src: str | None):
    candidate = engine_src or os.environ.get("RATISS_ENGINE_SRC")
    if candidate:
        sys.path.insert(0, str(Path(candidate).expanduser().resolve()))
    try:
        from ratiss_topological_decoherence.topology import topology_from_correlation
    except ImportError as error:
        raise RuntimeError("Set RATISS_ENGINE_SRC or --engine-src to the Studio Cloud src directory.") from error
    return topology_from_correlation


def parse_tsplib(path: str | Path) -> tuple[str, np.ndarray]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    name = next((line.split(":", 1)[1].strip() for line in lines if line.startswith("NAME")), "unknown")
    start = lines.index("NODE_COORD_SECTION") + 1
    points: list[list[float]] = []
    for line in lines[start:]:
        if line.strip() == "EOF":
            break
        tokens = line.split()
        if len(tokens) >= 3:
            points.append([float(tokens[1]), float(tokens[2])])
    return name, np.asarray(points, dtype=float)


def pairwise_distance(points: np.ndarray) -> np.ndarray:
    delta = points[:, None, :] - points[None, :, :]
    return np.linalg.norm(delta, axis=2)


def geometric_affinity(distance: np.ndarray) -> np.ndarray:
    positive = distance[np.triu_indices(len(distance), 1)]
    scale = float(np.median(positive))
    affinity = np.exp(-distance / max(scale, 1e-12))
    np.fill_diagonal(affinity, 1.0)
    return affinity


def noisy_association(base: np.ndarray, *, gaussian_std: float, false_edge_fraction: float, rng: np.random.Generator) -> tuple[np.ndarray, int]:
    """Return an observed association without altering the supplied baseline matrix."""
    if not 0.0 <= false_edge_fraction <= 1.0:
        raise ValueError("false_edge_fraction must be in [0, 1].")
    perturbation = rng.normal(0.0, gaussian_std, size=base.shape)
    perturbation = (perturbation + perturbation.T) / 2.0
    observed = np.clip(base + perturbation, 0.0, 1.0)
    upper = list(zip(*np.triu_indices(len(base), 1)))
    edge_count = int(round(false_edge_fraction * len(upper)))
    if edge_count:
        selection = rng.choice(len(upper), size=edge_count, replace=False)
        for index in np.asarray(selection, dtype=int):
            first, second = upper[index]
            observed[first, second] = observed[second, first] = max(observed[first, second], float(rng.uniform(0.70, 1.0)))
    np.fill_diagonal(observed, 1.0)
    return observed, edge_count


def _topology_dict(value: Any) -> dict[str, Any]:
    return value.to_dict() if hasattr(value, "to_dict") else value


def _psig(topology: dict[str, Any]) -> float:
    return float(topology["psig"])


def run_experiment(topology_from_correlation: Any, *, path: str | Path, profile: ResilienceProfile) -> dict[str, Any]:
    if profile.steps < 2:
        raise ValueError("steps must be at least 2.")
    name, original_points = parse_tsplib(path)
    original_distance = pairwise_distance(original_points)
    baseline_affinity = geometric_affinity(original_distance)
    baseline_topology = _topology_dict(topology_from_correlation(baseline_affinity))
    baseline_psig = _psig(baseline_topology)
    positive = original_distance[np.triu_indices(len(original_distance), 1)]
    median_distance = float(np.median(positive))
    drift_sigma = profile.coordinate_drift_fraction_of_median_distance * median_distance
    rng = np.random.default_rng(profile.seed)
    drifted_points = original_points.copy()
    observed_history: list[np.ndarray] = []
    trajectory: list[dict[str, Any]] = []
    for step in range(profile.steps):
        progress = step / (profile.steps - 1)
        if step:
            drifted_points = drifted_points + rng.normal(0.0, drift_sigma, size=drifted_points.shape)
        association_noise_std = progress * profile.final_association_noise_std
        false_edge_fraction = progress * profile.final_false_edge_fraction
        geometric = geometric_affinity(pairwise_distance(drifted_points))
        observed, injected_edges = noisy_association(
            geometric,
            gaussian_std=association_noise_std,
            false_edge_fraction=false_edge_fraction,
            rng=rng,
        )
        observed_history.append(observed)
        core = np.median(np.stack(observed_history, axis=0), axis=0)
        core = np.clip((core + core.T) / 2.0, 0.0, 1.0)
        np.fill_diagonal(core, 1.0)
        observed_topology = _topology_dict(topology_from_correlation(observed))
        core_topology = _topology_dict(topology_from_correlation(core))
        observed_psig = _psig(observed_topology)
        core_psig = _psig(core_topology)
        coordinate_rms = float(np.sqrt(np.mean((drifted_points - original_points) ** 2)))
        trajectory.append({
            "step": step,
            "progress": progress,
            "injected": {
                "coordinate_drift_distribution": "gaussian_cumulative",
                "coordinate_increment_sigma": drift_sigma,
                "coordinate_rms_from_source": coordinate_rms,
                "association_gaussian_std": association_noise_std,
                "false_edge_fraction_requested": false_edge_fraction,
                "false_edges_injected": injected_edges,
            },
            "observed_topology": observed_topology,
            "consensus_core_topology": core_topology,
            "observed_P_sig_ratio_to_baseline": None if baseline_psig == 0.0 else observed_psig / baseline_psig,
            "consensus_core_P_sig_ratio_to_baseline": None if baseline_psig == 0.0 else core_psig / baseline_psig,
            "observation_matrix": observed.tolist(),
            "consensus_core_matrix": core.tolist(),
        })
    threshold = baseline_psig * profile.collapse_ratio
    first_observed = next((item["step"] for item in trajectory if _psig(item["observed_topology"]) <= threshold), None)
    first_core = next((item["step"] for item in trajectory if _psig(item["consensus_core_topology"]) <= threshold), None)
    return {
        "schema": "ratiss.topology.resilience.v1",
        "provenance": {
            "source": "TSPLIB Berlin52 coordinates",
            "source_file": str(path),
            "validated_on_hardware": False,
            "claim_boundary": "Synthetic drift and observation-noise stress test on real Berlin52 coordinates. It does not claim a physical QPU model, a global TSP advantage or a denoising theorem.",
        },
        "profile": asdict(profile),
        "baseline": {
            "instance": name,
            "n_cities": int(len(original_points)),
            "P_sig": baseline_psig,
            "topology": baseline_topology,
            "median_distance": median_distance,
        },
        "trajectory": trajectory,
        "resilience": {
            "collapse_threshold_P_sig": threshold,
            "collapse_ratio_of_baseline": profile.collapse_ratio,
            "first_observed_threshold_crossing_step": first_observed,
            "first_consensus_core_threshold_crossing_step": first_core,
            "consensus_scope": "Temporal median of observed association matrices; exported separately and never fed back into the observed trajectory.",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Stress Berlin52 topology with temporal drift and observation noise.")
    parser.add_argument("--engine-src")
    parser.add_argument("--input", default="data/berlin52.tsp")
    parser.add_argument("--output", default="artifacts/berlin52_topology_resilience.json")
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--seed", type=int, default=20260823)
    parser.add_argument("--drift-fraction", type=float, default=0.003)
    parser.add_argument("--final-noise-std", type=float, default=0.22)
    parser.add_argument("--final-false-edge-fraction", type=float, default=0.06)
    parser.add_argument("--collapse-ratio", type=float, default=0.50)
    args = parser.parse_args()
    topology_from_correlation = load_engine(args.engine_src)
    profile = ResilienceProfile(
        steps=args.steps,
        seed=args.seed,
        coordinate_drift_fraction_of_median_distance=args.drift_fraction,
        final_association_noise_std=args.final_noise_std,
        final_false_edge_fraction=args.final_false_edge_fraction,
        collapse_ratio=args.collapse_ratio,
    )
    document = run_experiment(topology_from_correlation, path=args.input, profile=profile)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(document, indent=2), encoding="utf-8")
    print(f"Wrote {destination} with {len(document['trajectory'])} drift-and-noise steps.")


if __name__ == "__main__":
    main()
