"""Render deterministic documentation figures from Berlin52 and GSE4987 artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PALETTE = {"ink": "#07111c", "panel": "#102433", "mint": "#42d6ad", "blue": "#79b8ff", "coral": "#ff927d", "text": "#eaf2f8", "muted": "#9bb0bf"}


def style(axis) -> None:
    axis.set_facecolor(PALETTE["panel"])
    axis.tick_params(colors=PALETTE["muted"])
    for spine in axis.spines.values(): spine.set_color("#315063")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tsp", default="artifacts/berlin52_ratiss_inspection.json")
    parser.add_argument("--bio", default="artifacts/bio_yeast_gse4987.json")
    parser.add_argument("--output-dir", default="docs/assets")
    args = parser.parse_args()
    tsp = json.loads(Path(args.tsp).read_text(encoding="utf-8"))
    bio = json.loads(Path(args.bio).read_text(encoding="utf-8"))
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "figure.facecolor": PALETTE["ink"], "savefig.facecolor": PALETTE["ink"]})

    points = np.asarray(tsp["instance"]["coordinates"], dtype=float)
    baseline = tsp["global_heuristic_baseline"]["path"]
    inspection = tsp["ratiss_inspection_route"]["path"]
    selected = tsp["inspection_selection"]["nodes"]
    fig, axis = plt.subplots(figsize=(8.2, 6.2))
    style(axis)
    axis.plot(points[baseline, 0], points[baseline, 1], color="#57788c", linewidth=1.0, alpha=0.65, label="Baseline 52 villes")
    axis.scatter(points[:, 0], points[:, 1], s=16, color=PALETTE["text"], alpha=0.8, label="Berlin52")
    axis.scatter(points[selected, 0], points[selected, 1], s=48, color=PALETTE["coral"], label="Sélection RATISS")
    axis.plot(points[inspection, 0], points[inspection, 1], color=PALETTE["mint"], linewidth=2.3, label="Inspection Held–Karp (10)")
    axis.set_title("Berlin52 — sélection topologique et route d’inspection RATISS")
    axis.set_xlabel("Coordonnée x")
    axis.set_ylabel("Coordonnée y")
    legend = axis.legend(frameon=False, fontsize=8)
    for text in legend.get_texts(): text.set_color(PALETTE["text"])
    fig.tight_layout()
    fig.savefig(output / "berlin52-ratiss-inspection.png", dpi=180)
    plt.close(fig)

    matrix = np.asarray(bio["normalized_association"], dtype=float)
    labels = bio["selection"]["labels"]
    fig, axis = plt.subplots(figsize=(8.0, 6.8))
    style(axis)
    image = axis.imshow(matrix, vmin=0.0, vmax=1.0, cmap="viridis")
    axis.set_title("GSE4987 — association Pearson normalisée de 12 profils de levure")
    axis.set_xticks(range(len(labels)), labels, rotation=65, ha="right", fontsize=7)
    axis.set_yticks(range(len(labels)), labels, fontsize=7)
    colorbar = fig.colorbar(image, ax=axis, shrink=0.85)
    colorbar.ax.tick_params(colors=PALETTE["muted"])
    colorbar.set_label("Association normalisée", color=PALETTE["text"])
    fig.tight_layout()
    fig.savefig(output / "gse4987-association-heatmap.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    main()
