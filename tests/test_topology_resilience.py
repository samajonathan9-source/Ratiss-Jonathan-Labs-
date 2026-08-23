import importlib.util
import sys
from pathlib import Path

import numpy as np


MODULE = Path(__file__).resolve().parents[1] / "scripts" / "run_topology_resilience.py"
SPEC = importlib.util.spec_from_file_location("topology_resilience", MODULE)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def test_noisy_association_preserves_symmetry_and_diagonal_without_mutating_source():
    source = np.eye(4)
    source[0, 1] = source[1, 0] = 0.4
    observed, count = module.noisy_association(source, gaussian_std=0.1, false_edge_fraction=0.5, rng=np.random.default_rng(7))
    assert np.allclose(source[0, 1], 0.4)
    assert np.allclose(observed, observed.T)
    assert np.allclose(np.diag(observed), 1.0)
    assert count == 3


def test_resilience_profile_uses_declared_nonzero_stress_parameters():
    profile = module.ResilienceProfile()
    assert profile.steps == 10
    assert profile.coordinate_drift_fraction_of_median_distance > 0.0
    assert profile.final_association_noise_std > 0.0
