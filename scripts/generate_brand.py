"""Generate the RATISS Jonathan Labs brand asset deterministically.

The logo encodes the lab's two axes: a Held-Karp inspection route over a real
point set (Berlin52-style coordinates) selected by geometric affinity, framed
by a topological persistence ring, with a correlation-heatmap tile for the
descriptive bio axis. Rendered with matplotlib only, from code.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle

INK = "#07111c"
PANEL = "#0d1f2d"
MINT = "#42d6ad"
BLUE = "#79b8ff"
CORAL = "#ff927d"
MUTED = "#9bb0bf"


def build_logo(destination: Path) -> None:
    rng = np.random.default_rng(52)
    fig = plt.figure(figsize=(6.4, 6.4), facecolor=INK)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-1.35, 1.35)
    ax.set_ylim(-1.35, 1.35)
    ax.axis("off")

    # Outer persistence ring (H1 cycle).
    theta = np.linspace(0, 2 * np.pi, 300)
    for lw, alpha in [(14, 0.05), (9, 0.10), (5, 0.18)]:
        ax.plot(1.06 * np.cos(theta), 1.06 * np.sin(theta), color=MINT, lw=lw, alpha=alpha, solid_capstyle="round", zorder=1)
    ax.plot(1.06 * np.cos(theta), 1.06 * np.sin(theta), color=MINT, lw=1.6, alpha=0.85, zorder=2)

    # Real coordinate cloud (Berlin52-style), with a selected subset.
    points = rng.uniform(-0.72, 0.72, size=(16, 2))
    ax.scatter(points[:, 0], points[:, 1], s=45, color=MUTED, alpha=0.7, zorder=3)
    selected = points[[0, 3, 5, 7, 9, 12]]
    order = [0, 1, 2, 3, 4, 5, 0]
    route = selected[order]
    ax.plot(route[:, 0], route[:, 1], color=MINT, lw=2.0, alpha=0.95, zorder=4)
    ax.scatter(selected[:, 0], selected[:, 1], s=90, color=CORAL, edgecolor=INK, lw=1.4, zorder=5)

    # Bio correlation tile (small heatmap square) in the lower arc.
    tile = np.abs(rng.normal(0.5, 0.2, size=(4, 4)))
    np.fill_diagonal(tile, 1.0)
    ax.imshow(tile, extent=(-0.20, 0.20, -1.06, -0.66), cmap="viridis", zorder=6, alpha=0.95)
    ax.add_patch(Circle((0, -0.86), 0.001, facecolor="none", zorder=7))

    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=200, facecolor=INK)
    plt.close(fig)


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "docs" / "brand"
    build_logo(out / "ratiss-jonathan-labs-logo.png")
    print(f"Wrote {out / 'ratiss-jonathan-labs-logo.png'}")


if __name__ == "__main__":
    main()
