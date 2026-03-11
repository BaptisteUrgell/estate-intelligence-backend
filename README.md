# Analyse Dynamique du Marché Immobilier (DVF)

Ce projet permet de visualiser et d'analyser l'évolution des prix de l'immobilier en Haute-Garonne (31) à partir des données DVF (Demande de Valeur Foncière). Il utilise une interpolation spatiale pour générer des cartes de chaleur (heatmaps) interactives permettant d'observer les tendances locales à différentes échelles.

## Fonctionnalités

- **Visualisation interactive** : Cartographie des prix au m² et des tendances d'évolution.
- **Résolution ajustable** : Passage dynamique d'une grille grossière à une grille très fine (de 25x25 à 100x100).
- **Granularité temporelle** : Analyse par semestre (6 mois), par an ou par période de 2 ans.
- **Interpolation spatiale** : Estimation des prix sur l'ensemble du territoire par la méthode IDW (Inverse Distance Weighting).
- **Lissage spatial** : Réduction du bruit pour une meilleure lecture des tendances de fond.

## Installation

### Prérequis

- Python 3.12 ou supérieur
- Les données DVF brutes (fichiers `full.csv` par année) placées dans `data/raw/` (ex: `data/raw/2023/full.csv`)

### Installation des dépendances

```bash
# Installation classique via pip
pip install .

# Ou si vous utilisez uv (recommandé pour la rapidité)
uv sync
```

## Préparation des données

Avant de lancer l'application, vous devez traiter les données brutes pour générer les grilles et les interpolations :

1.  **Données DVF** : Téléchargez les données DVF au format CSV (fichiers `full.csv`) sur [data.gouv.fr](https://www.data.gouv.fr/fr/datasets/demandes-de-valeur-fonciere/).
2.  **Organisation** : Placez les fichiers dans `data/raw/` par année (ex: `data/raw/2023/full.csv`).
3.  **Traitement** :

```bash
python scripts/data_cleaning.py
```

Ce script va :
1. Filtrer les données pour la Haute-Garonne (31) et les types de biens (Maison/Appartement).
2. Créer des grilles géométriques (GeoJSON) pour chaque résolution.
3. Calculer les prix interpolés pour chaque cellule de la grille et chaque période.
4. Sauvegarder les résultats dans `data/processed/`.

## Utilisation

Lancez l'application Dash :

```bash
python app.py
```

L'interface sera accessible par défaut sur `http://127.0.0.1:8050/`.

### Contrôles de l'interface

- **Taille des carrés** : Ajuste la précision géographique de l'analyse.
- **Granularité temporelle** : Change le pas de temps pour l'agrégation des données.
- **Mode d'analyse** :
  - **Prix au m²** : Affiche les prix absolus (échelle logarithmique pour mieux distinguer les zones).
  - **Tendance** : Affiche l'évolution en pourcentage par rapport à la période précédente.
- **Slider de période** : Permet de naviguer dans le temps.

## Détails Techniques

- **Interpolation** : Utilise `scipy.spatial.cKDTree` pour une recherche rapide des voisins les plus proches et une pondération par l'inverse du carré de la distance.
- **Interface** : Développée avec **Dash** (Plotly) pour une réactivité optimale sans rechargement de page.
- **Géographie** : Utilisation de **GeoPandas** et **Shapely** pour la manipulation des polygones et des projections.

## Structure du projet

```text
├── app.py                # Application Dash principale
├── scripts/
│   └── data_cleaning.py  # Script de traitement et d'interpolation
├── data/
│   ├── raw/             # Données DVF brutes (non incluses)
│   └── processed/       # Données générées (GeoJSON, CSV)
├── pyproject.toml        # Configuration du projet et dépendances
└── README.md             # Ce fichier
```
