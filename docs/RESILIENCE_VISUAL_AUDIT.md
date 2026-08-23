# Audit visuel — Résilience topologique Berlin52

La figure `berlin52-topology-resilience.png` sépare le `P_sig` observé après dérive et bruit synthétiques du `P_sig` du noyau de consensus temporel. La valeur Berlin52 source et le seuil de rupture à 50 % sont lisibles sur les mêmes axes.

La rupture observée au pas 5 tombe sous le seuil, tandis que le noyau consensus reste au-dessus pour cette exécution. Les deux traces sont des sorties distinctes ; le noyau ne remplace pas la matrice observée et n’est pas réinjecté dans son calcul. La figure documente un stress test sur les coordonnées TSPLIB réelles, non un filtre certifié ni une performance TSP globale.
