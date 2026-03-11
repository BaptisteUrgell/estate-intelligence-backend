import glob
import os

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from shapely.geometry import Polygon

# Paramètres globaux
GRID_MIN_LAT, GRID_MAX_LAT = 43.50, 43.70
GRID_MIN_LON, GRID_MAX_LON = 1.30, 1.55
RESOLUTIONS = [25, 38, 50, 75, 100]

os.makedirs("data/processed", exist_ok=True)

print("1. Nettoyage des données ponctuelles DVF...")
colonnes_utiles = [
    "date_mutation",
    "valeur_fonciere",
    "code_postal",
    "type_local",
    "surface_reelle_bati",
    "longitude",
    "latitude",
]
dataframes = []

fichiers = glob.glob("data/raw/*/full.csv")

for file_path in fichiers:
    print(f"  Lecture de {file_path}...")
    chunk_iter = pd.read_csv(
        file_path, usecols=colonnes_utiles, low_memory=False, chunksize=100000
    )
    for chunk in chunk_iter:
        chunk["code_postal"] = chunk["code_postal"].fillna(0).astype(int).astype(str)
        df_filtered = chunk[chunk["code_postal"].str.startswith("31")].copy()
        df_filtered = df_filtered[
            df_filtered["type_local"].isin(["Maison", "Appartement"])
        ]
        df_filtered.dropna(
            subset=["valeur_fonciere", "surface_reelle_bati", "latitude", "longitude"],
            inplace=True,
        )
        if not df_filtered.empty:
            dataframes.append(df_filtered)

df_final = pd.concat(dataframes, ignore_index=True)
df_final["prix_m2"] = df_final["valeur_fonciere"] / df_final["surface_reelle_bati"]
df_final = df_final[(df_final["prix_m2"] >= 1000) & (df_final["prix_m2"] <= 10000)]
df_final["date_mutation"] = pd.to_datetime(df_final["date_mutation"])
df_final["annee"] = df_final["date_mutation"].dt.year.astype(str)
df_final["semestre"] = np.where(df_final["date_mutation"].dt.month <= 6, "S1", "S2")
df_final["periode"] = df_final["annee"] + "-" + df_final["semestre"]

# BOUCLE SUR LES 3 TAILLES DE GRILLE
for res in RESOLUTIONS:
    print(f"\n--- GÉNÉRATION POUR LA RÉSOLUTION {res}x{res} ---")
    grid_points, grid_polygons = [], []
    lat_range = np.linspace(GRID_MIN_LAT, GRID_MAX_LAT, res)
    lon_range = np.linspace(GRID_MIN_LON, GRID_MAX_LON, res)
    delta_lat = (GRID_MAX_LAT - GRID_MIN_LAT) / (res - 1)
    delta_lon = (GRID_MAX_LON - GRID_MIN_LON) / (res - 1)

    grid_cell_id_counter = 0
    for lat in lat_range:
        for lon in lon_range:
            grid_points.append([lon, lat])
            polygon = Polygon(
                [
                    (lon - delta_lon / 2, lat - delta_lat / 2),
                    (lon + delta_lon / 2, lat - delta_lat / 2),
                    (lon + delta_lon / 2, lat + delta_lat / 2),
                    (lon - delta_lon / 2, lat + delta_lat / 2),
                ]
            )
            grid_polygons.append({"id": grid_cell_id_counter, "geometry": polygon})
            grid_cell_id_counter += 1

    grid_points_arr = np.array(grid_points)
    grille_gdf = gpd.GeoDataFrame(grid_polygons, crs="EPSG:4326")
    grille_gdf.rename(columns={"id": "Grid_ID"}, inplace=True)
    grille_gdf.to_file(f"data/processed/grille_{res}.geojson", driver="GeoJSON")

    print(
        f"  Interpolation spatiale en cours pour la grille {res} (Veuillez patienter)..."
    )
    periodes = sorted(df_final["periode"].unique())
    all_interpolated = []

    for periode in periodes:
        df_periode = df_final[df_final["periode"] == periode]
        if len(df_periode) < 30:
            continue
        points_réels = df_periode[["longitude", "latitude"]].values
        valeurs_réelles = df_periode["prix_m2"].values

        tree = cKDTree(points_réels)
        dist, idx = tree.query(grid_points_arr, k=15)
        interpolated_values = []

        for i in range(len(grid_points_arr)):
            current_dist = dist[i]
            current_idx = idx[i]
            mask_zero = current_dist < 1e-12
            if mask_zero.any():
                interpolated_values.append(valeurs_réelles[current_idx[mask_zero][0]])
                continue
            weights = 1.0 / (current_dist**2)
            weighted_sum = np.sum(weights * valeurs_réelles[current_idx])
            total_weight = np.sum(weights)
            interpolated_values.append(
                weighted_sum / total_weight if total_weight > 0 else np.nan
            )

        all_interpolated.append(
            pd.DataFrame(
                {
                    "Grid_ID": range(len(grid_points_arr)),
                    "periode": [periode] * len(grid_points_arr),
                    "Prix_Interpolé": interpolated_values,
                }
            )
        )

    pd.concat(all_interpolated, ignore_index=True).to_csv(
        f"data/processed/data_{res}.csv", index=False
    )

print("\nTerminé ! Vous pouvez lancer app.py")
