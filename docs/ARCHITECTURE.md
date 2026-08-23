# Architecture des graphes RATISS

```mermaid
flowchart LR
  A[Berlin52 coordinates] --> B[Euclidean distance]
  B --> C[Normalized geometric affinity]
  C --> D[Graph topology and support ranking]
  D --> E[Exact local inspection route]
  C --> J[Gaussian drift and observation noise]
  J --> K[Observed topology P sig]
  J --> L[Temporal median consensus core]
  F[GSE4987 yeast expression] --> G[Pearson association]
  G --> H[Declared bio correlation adapter]
  E --> I[Versioned experiment artifacts]
  H --> I
  K --> M[Resilience artifact]
  L --> M
```

L’axe Berlin52 traite une structure géométrique de benchmark. L’axe GSE4987 importe une structure descriptive de corrélation. Les deux partagent un contrat d’artefact, mais leurs unités et leur portée restent distinctes.

La branche de résilience part d’une copie de l’affinité Berlin52 et injecte une dérive et un bruit de manière déclarée. Le `P_sig` observé et le noyau consensus sont exportés séparément : le consensus ne remplace pas l’observation et n’est pas utilisé pour modifier le benchmark historique.
