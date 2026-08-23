# Berlin52 — contrat de dérive et résilience topologique

## Donnée et séparation des scénarios

L’expérience part des coordonnées Berlin52 TSPLIB déjà versionnées. La baseline historique n’est pas modifiée. Une trajectoire séparée fabrique des matrices **observées** à partir de trois sources de perturbation déclarées : déplacement gaussien cumulatif des coordonnées, bruit gaussien symétrisé dans l’affinité et ajout de fausses arêtes. [1]

Le noyau consensus est la médiane temporelle des matrices observées disponibles au pas courant. Il est produit dans un champ séparé, sans altérer la matrice observée ni devenir une correction de l’entrée.

| Paramètre exécuté | Valeur |
|---|---:|
| Pas de trajectoire | 10 |
| Seed | 20260823 |
| Dérive par incrément | 0.003 × distance médiane Berlin52 |
| Bruit d’association final | écart-type 0.22 |
| Fausses arêtes finales | 80 sur 1 326 paires possibles |
| Seuil de rupture | 50 % du P sig baseline |

## Résultats de l’exécution versionnée

La baseline calculée vaut `P_sig=0.3806296964`; le seuil est donc `0.1903148482`. La branche observée passe sous ce seuil au pas 5, avec `P_sig=0.1497961077`. Le noyau consensus ne franchit pas le seuil dans cette exécution : il vaut `0.4000637981` au même pas. Ces valeurs restent des résultats de ce seed et de ce profil d’injection, pas une propriété universelle de Berlin52.

| Sortie | Valeur observée |
|---|---:|
| Premier franchissement observé | Pas 5 |
| Premier franchissement du noyau consensus | `null` |
| RMS de dérive au dernier pas | 4.757800156 |
| P sig observé au dernier pas | 0.2483562267 |
| P sig noyau au dernier pas | 0.3876389854 |

La trajectoire ne fournit ni diagnostic biologique, ni équivalence à un bruit QPU, ni preuve d’un solveur TSP. Elle sert à visualiser à quel niveau de stress topologique une observation structurée diverge de sa baseline et à conserver cette information dans un artefact reproductible.

## Reproduction

```bash
PYTHONPATH=/chemin/vers/ratiss-topological-decoherence-engine/src \
python3 scripts/run_topology_resilience.py \
  --engine-src /chemin/vers/ratiss-topological-decoherence-engine/src \
  --input data/berlin52.tsp \
  --output artifacts/berlin52_topology_resilience.json
```

## Références

[1] [TSPLIB — bibliothèque d’instances Berlin52](http://comopt.ifi.uni-heidelberg.de/software/TSPLIB95/)
