# La France face à ses voisins


En ligne : https://djac57.github.io/france-voisins/

Mise à jour automatique : le workflow GitHub Actions retélécharge les séries le 3 de chaque mois (et à chaque push), régénère `site/data.js` et déploie `site/` sur GitHub Pages. Les séries brutes sont versionnées dans `data/raw/` : si une source est indisponible, le site garde les données précédentes.

Atlas comparatif : 35 indicateurs officiels (éducation, économie, santé, social, fiscalité, écologie, logement) comparant la France à l'Allemagne, la Belgique, le Luxembourg, la Suisse, l'Italie, l'Espagne, le Royaume-Uni, les Pays-Bas, la Suède, le Danemark et la moyenne de l'UE ; et 16 politiques publiques étrangères documentées (« Et si on faisait comme eux ? »).

## Reconstruire

```sh
python3 scripts/fetch.py /chemin/brut          # Eurostat, Banque mondiale, FMI, Our World in Data
python3 scripts/build.py /chemin/brut          # -> site/data.js (+ empreinte anti-cache dans index.html)
python3 scripts/build_geo.py countries-50m.json # fond de carte (world-atlas 2.0.2), à lancer une fois
open site/index.html
```

Bibliothèque standard Python uniquement.

## Fichiers

- `scripts/indicators.py` : catalogue des indicateurs (source, code, sens « mieux »), PISA 2022, tranches OCDE du logement social.
- `scripts/policies.json` : les fiches de politiques publiques, avec leurs sources.
- `scripts/build.py` : méthode des classements et des scores de domaine (documentée en tête de fichier).

## Méthode

Une source par indicateur pour tous les pays. Valeur la plus récente datant de 5 ans au plus. Score d'un pays sur un indicateur = 100 × (n − rang) / (n − 1). Score de domaine = moyenne simple des indicateurs orientés, si le pays est mesuré sur au moins 60 % d'entre eux. Les repères de contexte sont affichés mais exclus des scores.
