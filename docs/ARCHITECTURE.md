# Architecture des graphes RATISS

```mermaid
flowchart LR
  A[Berlin52 coordinates] --> B[Euclidean distance]
  B --> C[Normalized geometric affinity]
  C --> D[Graph topology and support ranking]
  D --> E[Exact local inspection route]
  F[GSE4987 yeast expression] --> G[Pearson association]
  G --> H[Declared bio correlation adapter]
  E --> I[Versioned experiment artifacts]
  H --> I
```

L’axe Berlin52 traite une structure géométrique de benchmark. L’axe GSE4987 importe une structure descriptive de corrélation. Les deux partagent un contrat d’artefact, mais leurs unités et leur portée restent distinctes.
