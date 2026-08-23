import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_berlin_and_bio_artifacts_preserve_their_distinct_metric_scope():
    berlin = json.loads((ROOT / "artifacts" / "berlin52_ratiss_inspection.json").read_text(encoding="utf-8"))
    bio = json.loads((ROOT / "artifacts" / "bio_yeast_gse4987.json").read_text(encoding="utf-8"))
    assert berlin["instance"]["n_cities"] == 52
    assert berlin["ratiss_inspection_route"]["method"] == "held_karp_exact"
    step = bio["ratiss_timeline"]["steps"][0]
    assert step["logical_topology"]["P_sig"] is None
    assert step["logical_topology"]["scope"] == "not_applicable_external_non_density_input"
    assert step["topology"]["psig"] >= 0.0


def test_labs_documentation_figures_exist():
    assets = ROOT / "docs" / "assets"
    assert (assets / "berlin52-ratiss-inspection.png").is_file()
    assert (assets / "gse4987-association-heatmap.png").is_file()
