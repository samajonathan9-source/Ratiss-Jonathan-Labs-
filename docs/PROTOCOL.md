# Protocoles — graphes RATISS et données bio descriptives

## TSP : rôle exact de RATISS

Le TSP est traité comme une expérience de **priorisation topologique et de parcours**, non comme une preuve que RATISS résout un problème NP-complet plus vite qu’un solveur classique. Le protocole compare, sur une instance publique de coordonnées, trois sorties distinctes :

| Sortie | Méthode | But |
|---|---|---|
| Route complète de référence | Held–Karp sur un sous-ensemble petit | Établir un optimum exact localement vérifiable |
| Baseline constructive | Plus proche voisin puis 2-opt | Produire une baseline heuristique transparente |
| Route RATISS d’inspection | Sous-ensemble prioritaire dérivé de corrélations et topologie | Définir où inspecter, pas résoudre la tournée globale |

Les coûts, tailles de sous-ensemble et méthodes sont tous exportés ; aucun résultat ne sera nommé « avantage » sans benchmark reproductible correspondant.

## Bio : ingestion non clinique

L’axe bio consomme une matrice d’expression de cycle cellulaire de levure issue du jeu public GSE4987. Il construit une corrélation de Pearson sur un ensemble de gènes explicitement listé et l’importe dans le contrat RATISS comme `declared_bio_correlation`.

Les sorties décrivent uniquement une structure d’association fournie : elles ne déduisent ni cohérence quantique, ni causalité, ni diagnostic, ni conclusion biologique. La source, les labels, le filtrage et la matrice finale sont tous versionnés.

## Référence

[Saccharomyces Genome Database — Yeast cell cycle, GSE4987](https://yeastgenome.org/dataset/GSE4987)
