from pathlib import Path
import importlib.util
import numpy as np


MODULE = Path(__file__).resolve().parents[1] / "scripts" / "run_tsp_ratiss.py"
SPEC = importlib.util.spec_from_file_location("tsp_ratiss", MODULE)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


def test_parser_reads_real_berlin52_coordinates():
    name, points = module.parse_tsplib(Path(__file__).resolve().parents[1] / "data" / "berlin52.tsp")
    assert name == "berlin52"
    assert points.shape == (52, 2)


def test_affinity_is_symmetric_and_has_unit_diagonal():
    points = np.asarray([[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    affinity = module.geometric_affinity(module.distance(points))
    assert np.allclose(affinity, affinity.T)
    assert np.allclose(np.diag(affinity), 1.0)
