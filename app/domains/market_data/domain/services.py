import math
import re

import numpy as np


def lisser_tendance_spatiale(df_periode, res_actuelle):
    """Lisse la tendance (évolution) d'un carré avec ses 4 voisins immédiats."""
    df_temp = df_periode.set_index("Grid_ID").copy()
    df_temp["Evolution"] = df_temp.get("Evolution_brute", np.nan)

    for current_id in df_temp.index:
        voisins_ids = [
            current_id - 1,
            current_id + 1,
            current_id - res_actuelle,
            current_id + res_actuelle,
        ]
        ids_valides = [current_id] + [v for v in voisins_ids if v in df_temp.index]
        df_temp.at[current_id, "Evolution"] = df_temp.loc[ids_valides, "Evolution_brute"].mean(
            skipna=True
        )

    return df_temp.reset_index()


def parse_google_maps_coords(coord_str):
    """Convertit une chaîne Google Maps (DMS ou Décimale) en Latitude, Longitude."""
    if not coord_str:
        return None, None
    coord_str = str(coord_str).strip()

    # Format décimal classique (ex: 43.579, 1.390)
    if "," in coord_str and "°" not in coord_str:
        try:
            parts = coord_str.split(",")
            return float(parts[0].strip()), float(parts[1].strip())
        except ValueError:
            pass

    # Format DMS Google Maps (ex: 43°34'47.1"N 1°23'27.2"E)
    dms_pattern = re.compile(r"(\d+)[°\s]+(\d+)['\s]+([\d\.]+)[^NSWE]*([NSWE])", re.I)
    matches = dms_pattern.findall(coord_str)

    if len(matches) == 2:

        def to_dd(m):
            dd = float(m[0]) + float(m[1]) / 60 + float(m[2]) / 3600
            if m[3].upper() in ["S", "W"]:
                dd *= -1
            return dd

        lat = to_dd(matches[0]) if matches[0][3].upper() in ["N", "S"] else to_dd(matches[1])
        lon = to_dd(matches[1]) if matches[1][3].upper() in ["E", "W"] else to_dd(matches[0])
        return lat, lon

    return None, None


def get_nearest_grid_id(lat, lon, res_centers):
    """Trouve le carré géométrique le plus proche d'un point GPS donné."""
    min_dist = float("inf")
    best_id = None
    for gid, (c_lat, c_lon) in res_centers.items():
        dist = math.hypot(lat - c_lat, lon - c_lon)
        if dist < min_dist:
            min_dist, best_id = dist, gid
    return best_id
