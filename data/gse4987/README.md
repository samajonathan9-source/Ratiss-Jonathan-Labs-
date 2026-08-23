# GSE4987 — provenance locale

Les données brutes de cette expérience sont téléchargées depuis l’archive publique de la *Saccharomyces Genome Database* référencée dans le protocole. Elles ne sont pas committées dans ce dépôt ; seules la provenance et une sélection dérivée de profils réellement lus sont exportées dans l’artefact d’expérience.

```bash
mkdir -p data/gse4987/raw
curl -L https://sgd-prod-upload.s3.amazonaws.com/S000204339/Pramila_2006_PMID_16912276.zip -o data/gse4987/source.zip
unzip -o data/gse4987/source.zip -d data/gse4987/raw
```

Source : [GSE4987 — Yeast cell cycle](https://yeastgenome.org/dataset/GSE4987).
