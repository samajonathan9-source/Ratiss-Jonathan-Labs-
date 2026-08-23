"""Convert measured GSE4987 yeast expression profiles to a RATISS bio timeline.

The resulting graph is a declared, normalized Pearson-association structure.
It is not a quantum, causal, clinical or biological-diagnostic model.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np


SOURCE_URL = "https://sgd-prod-upload.s3.amazonaws.com/S000204339/Pramila_2006_PMID_16912276.zip"
DATASET_URL = "https://yeastgenome.org/dataset/GSE4987"


def load_engine(engine_src: str | None):
    candidate = engine_src or os.environ.get("RATISS_ENGINE_SRC")
    if candidate:
        sys.path.insert(0, str(Path(candidate).expanduser().resolve()))
    try:
        from ratiss_topological_decoherence.correlation_import import run_bio_correlation_trajectory
    except ImportError as error:
        raise RuntimeError("Set RATISS_ENGINE_SRC or --engine-src to the Studio Cloud src directory.") from error
    return run_bio_correlation_trajectory


def read_pcl(path: str | Path, n_genes: int) -> tuple[list[str], np.ndarray]:
    if n_genes < 2:
        raise ValueError("n_genes must be at least two.")
    rows: list[list[float]] = []
    labels: list[str] = []
    with Path(path).open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader)
        next(reader)  # EWEIGHT row
        expected = len(header) - 3
        for raw in reader:
            if len(raw) < expected + 3:
                continue
            try:
                values = [float(value) for value in raw[3:3 + expected]]
            except ValueError:
                continue
            if len(values) != expected or not np.all(np.isfinite(values)):
                continue
            labels.append(raw[0])
            rows.append(values)
            if len(rows) == n_genes:
                break
    if len(rows) != n_genes:
        raise ValueError(f"Only {len(rows)} complete profiles were available.")
    return labels, np.asarray(rows, dtype=float)


def normalized_pearson(expression: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    pearson = np.corrcoef(expression)
    pearson = np.nan_to_num(pearson, nan=0.0, posinf=0.0, neginf=0.0)
    pearson = np.clip((pearson + pearson.T) / 2.0, -1.0, 1.0)
    normalized = np.clip((pearson + 1.0) / 2.0, 0.0, 1.0)
    np.fill_diagonal(normalized, 1.0)
    return pearson, normalized


def run_experiment(run_bio_correlation_trajectory: Any, *, pcl: str | Path, n_genes: int) -> dict[str, Any]:
    labels, expression = read_pcl(pcl, n_genes)
    pearson, normalized = normalized_pearson(expression)
    payload = {
        "source": {
            "dataset_accession": "GSE4987",
            "dataset_url": DATASET_URL,
            "download_url": SOURCE_URL,
            "organism": "Saccharomyces cerevisiae",
            "measurement_protocol": "Pramila et al. yeast W303 cell-cycle microarray expression profiles; normalized pairwise Pearson association over selected complete gene profiles.",
            "claim_boundary": "Descriptive association import only; no quantum-coherence, causal, clinical or diagnostic inference.",
        },
        "labels": labels,
        "trajectory": [{"step": 0, "label": "gse4987_selected_gene_association", "correlation_matrix": normalized.tolist()}],
    }
    timeline = run_bio_correlation_trajectory(payload)
    return {
        "schema": "ratiss.bio.gse4987.v1",
        "source": payload["source"],
        "selection": {"rule": "first complete rows in the public PCL file", "n_genes": n_genes, "labels": labels},
        "selected_expression": expression.tolist(),
        "pearson_correlation": pearson.tolist(),
        "normalized_association": normalized.tolist(),
        "ratiss_timeline": timeline,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a descriptive RATISS bio association timeline from GSE4987.")
    parser.add_argument("--engine-src")
    parser.add_argument("--input", default="data/gse4987/raw/expression_files_for_S3/Pramila_2006_PMID_16912276/GSE4987_setA_family.pcl")
    parser.add_argument("--output", default="artifacts/bio_yeast_gse4987.json")
    parser.add_argument("--n-genes", type=int, default=12)
    args = parser.parse_args()
    adapter = load_engine(args.engine_src)
    document = run_experiment(adapter, pcl=args.input, n_genes=args.n_genes)
    destination = Path(args.output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(document, indent=2), encoding="utf-8")
    print(f"Wrote {destination} with {args.n_genes} measured yeast gene profiles.")


if __name__ == "__main__":
    main()
