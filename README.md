# Ratiss Jonathan Labs

Laboratoire reproductible pour des expériences de graphes RATISS. Le premier axe utilise les coordonnées publiques **Berlin52** pour comparer une baseline heuristique globale à une route RATISS d’inspection sur un sous-ensemble topologique ; cette route ne prétend pas résoudre le TSP plus vite.

```bash
PYTHONPATH=/path/to/ratiss-topological-decoherence-engine/src \
python3 scripts/run_tsp_ratiss.py \
  --engine-src /path/to/ratiss-topological-decoherence-engine/src
```

Les coordonnées de référence sont versionnées sous `data/berlin52.tsp`. Le contrat détaillé, y compris la future ingestion bio non clinique, est dans [`docs/PROTOCOL.md`](docs/PROTOCOL.md).

Les résultats Berlin52 et GSE4987 réellement calculés sont dans [`docs/RESULTS.md`](docs/RESULTS.md).
