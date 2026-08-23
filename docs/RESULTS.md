# Résultats observés — Berlin52 et GSE4987

## Berlin52 : route d’inspection RATISS

L’expérience lit les 52 coordonnées publiques Berlin52, calcule une affinité géométrique normalisée puis sélectionne les dix villes au plus faible support moyen pour une route d’inspection exacte. Le fichier complet est [`artifacts/berlin52_ratiss_inspection.json`](../artifacts/berlin52_ratiss_inspection.json).

| Mesure | Valeur observée |
|---|---:|
| Nombre de villes | 52 |
| P sig du graphe d’affinité | 0.3806296964 |
| Betti | `[1, 0, 0]` |
| Sous-ensemble d’inspection | `51, 13, 10, 1, 32, 12, 6, 46, 41, 50` |
| Route d’inspection | Held–Karp exact sur 10 villes |
| Coût de la route d’inspection | 4666.323392758 |
| Baseline globale | Plus proche voisin + 2-opt sur 52 villes |
| Coût de la baseline globale | 8060.651582561 |

Les deux coûts ne doivent pas être comparés comme s’ils optimisaient le même problème : la route RATISS visite un sous-ensemble de dix villes destiné à l’inspection, tandis que la baseline visite les 52 villes. L’expérience montre une sélection et un parcours reproductibles, pas un avantage TSP global.

## GSE4987 : association d’expression de levure

L’ingestion lit douze profils complets mesurés dans le jeu de cycle cellulaire de levure GSE4987, calcule leurs corrélations de Pearson et les normalise dans l’intervalle `[0,1]` pour le contrat RATISS. L’artefact est [`artifacts/bio_yeast_gse4987.json`](../artifacts/bio_yeast_gse4987.json).

| Mesure | Valeur observée |
|---|---:|
| Organisme | *Saccharomyces cerevisiae* |
| Profils sélectionnés | 12 profils complets, labels versionnés dans l’artefact |
| P sig du graphe d’associations | 0.099482859 |
| P sig logique RATISS | `null` |
| Métriques densité | Non disponibles |

`P sig logique=null` est le comportement attendu par le contrat pour un import d’association bio. L’artefact ne produit aucune conclusion clinique, causale ou de cohérence quantique.

## Reproduction

```bash
PYTHONPATH=/path/to/ratiss-topological-decoherence-engine/src \
python3 scripts/run_tsp_ratiss.py \
  --engine-src /path/to/ratiss-topological-decoherence-engine/src

PYTHONPATH=/path/to/ratiss-topological-decoherence-engine/src \
python3 scripts/run_bio_yeast.py \
  --engine-src /path/to/ratiss-topological-decoherence-engine/src
```

## Références

[1] [TSPLIB](https://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/)

[2] [Saccharomyces Genome Database — GSE4987](https://yeastgenome.org/dataset/GSE4987)
