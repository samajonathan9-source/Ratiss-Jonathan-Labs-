from pathlib import Path
import importlib.util
import numpy as np


MODULE = Path(__file__).resolve().parents[1] / "scripts" / "run_bio_yeast.py"
SPEC = importlib.util.spec_from_file_location("bio_yeast", MODULE)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


def test_gse4987_parser_returns_measured_rows():
    source = Path(__file__).resolve().parents[1] / "data" / "gse4987" / "raw" / "expression_files_for_S3" / "Pramila_2006_PMID_16912276" / "GSE4987_setA_family.pcl"
    labels, values = module.read_pcl(source, 4)
    assert labels == ["YDR473C", "YDR130C", "YKL175W", "YDR098C"]
    assert values.shape[0] == 4
    assert values.shape[1] > 10


def test_normalized_pearson_is_symmetric_with_unit_diagonal():
    expression = np.asarray([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [3.0, 2.0, 1.0]])
    pearson, normalized = module.normalized_pearson(expression)
    assert np.allclose(pearson, pearson.T)
    assert np.allclose(normalized, normalized.T)
    assert np.allclose(np.diag(normalized), 1.0)
