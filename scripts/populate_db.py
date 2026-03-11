import asyncio
import json

import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.settings import settings
from app.domains.market_data.domain.services import lisser_tendance_spatiale
from app.domains.market_data.infrastructure.models import GridCellModel, MarketDataModel
from app.infrastructure.database import Base

# Note: this script needs to be run via `python -m scripts.populate_db`


async def populate_db():
    print(f"Connecting to {settings.DATABASE_URL}...")
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = async_sessionmaker(bind=engine)

    async with AsyncSessionLocal() as session:
        for res in settings.RESOLUTIONS:
            geojson_path = settings.INPUT_DIR / f"grille_{res}.geojson"
            csv_path = settings.INPUT_DIR / f"data_{res}.csv"

            if not (geojson_path.exists() and csv_path.exists()):
                print(f"⚠️ Missing files for resolution {res}.")
                continue

            print(f"Processing resolution {res}...")

            # Load GeoJSON
            with open(geojson_path) as f:
                geojson_data = json.load(f)

            grid_cells_db = []
            grid_id_to_db_id = {}

            print("  Inserting grid cells...")
            for feature in geojson_data["features"]:
                gid = feature["properties"]["Grid_ID"]
                coords = feature["geometry"]["coordinates"][0]
                c_lon = sum([c[0] for c in coords]) / len(coords)
                c_lat = sum([c[1] for c in coords]) / len(coords)

                grid_cell = GridCellModel(
                    resolution=res,
                    grid_id=gid,
                    center_lat=c_lat,
                    center_lon=c_lon,
                    geojson_feature=feature,
                )
                session.add(grid_cell)
                grid_cells_db.append(grid_cell)

            await session.commit()

            # Re-fetch to get IDs
            for gc in grid_cells_db:
                grid_id_to_db_id[gc.grid_id] = gc.id

            # Process Data
            df_base = pd.read_csv(csv_path)
            df_base["Annee"] = df_base["periode"].str.split("-").str[0].astype(int)

            # --- 6 Mois ---
            df_6m = df_base.copy()
            df_6m["periode_aff"] = df_6m["periode"]
            df_6m = df_6m.sort_values(by=["Grid_ID", "periode_aff"])
            df_6m["Prix_avant"] = df_6m.groupby("Grid_ID")["Prix_Interpolé"].shift(2)
            df_6m["Evolution_brute"] = (
                (df_6m["Prix_Interpolé"] - df_6m["Prix_avant"]) / df_6m["Prix_avant"]
            ) * 100
            df_6m["Log_Prix"] = np.log10(df_6m["Prix_Interpolé"])
            lisse_list = [
                lisser_tendance_spatiale(df_6m[df_6m["periode_aff"] == p], res)
                for p in df_6m["periode_aff"].unique()
            ]
            df_6m_final = pd.concat(lisse_list, ignore_index=True)
            df_6m_final["granularity"] = "6m"

            # --- 1 An ---
            df_1y = df_base.groupby(["Grid_ID", "Annee"])["Prix_Interpolé"].mean().reset_index()
            df_1y["periode_aff"] = df_1y["Annee"].astype(str)
            df_1y = df_1y.sort_values(by=["Grid_ID", "periode_aff"])
            df_1y["Prix_avant"] = df_1y.groupby("Grid_ID")["Prix_Interpolé"].shift(1)
            df_1y["Evolution_brute"] = (
                (df_1y["Prix_Interpolé"] - df_1y["Prix_avant"]) / df_1y["Prix_avant"]
            ) * 100
            df_1y["Log_Prix"] = np.log10(df_1y["Prix_Interpolé"])
            lisse_list = [
                lisser_tendance_spatiale(df_1y[df_1y["periode_aff"] == p], res)
                for p in df_1y["periode_aff"].unique()
            ]
            df_1y_final = pd.concat(lisse_list, ignore_index=True)
            df_1y_final["granularity"] = "1y"

            # --- 2 Ans ---
            min_y = df_base["Annee"].min()
            df_temp = df_base.copy()
            df_temp["Bin_start"] = ((df_temp["Annee"] - min_y) // 2) * 2 + min_y
            df_temp["Bin_end"] = np.minimum(df_temp["Bin_start"] + 1, df_base["Annee"].max())
            df_temp["periode_aff"] = np.where(
                df_temp["Bin_start"] == df_temp["Bin_end"],
                df_temp["Bin_start"].astype(str),
                df_temp["Bin_start"].astype(str) + "-" + df_temp["Bin_end"].astype(str),
            )
            df_2y = (
                df_temp.groupby(["Grid_ID", "periode_aff"])["Prix_Interpolé"].mean().reset_index()
            )
            df_2y = df_2y.sort_values(by=["Grid_ID", "periode_aff"])
            df_2y["Prix_avant"] = df_2y.groupby("Grid_ID")["Prix_Interpolé"].shift(1)
            df_2y["Evolution_brute"] = (
                (df_2y["Prix_Interpolé"] - df_2y["Prix_avant"]) / df_2y["Prix_avant"]
            ) * 100
            df_2y["Log_Prix"] = np.log10(df_2y["Prix_Interpolé"])
            lisse_list = [
                lisser_tendance_spatiale(df_2y[df_2y["periode_aff"] == p], res)
                for p in df_2y["periode_aff"].unique()
            ]
            df_2y_final = pd.concat(lisse_list, ignore_index=True)
            df_2y_final["granularity"] = "2y"

            # Combine all
            all_market_data = pd.concat([df_6m_final, df_1y_final, df_2y_final], ignore_index=True)

            print(f"  Inserting market data ({len(all_market_data)} rows)...")
            # Batch insert to avoid huge memory usage
            batch_size = 5000
            models_to_insert = []

            for _, row in all_market_data.iterrows():
                grid_id = int(row["Grid_ID"])
                if grid_id not in grid_id_to_db_id:
                    continue

                models_to_insert.append(
                    MarketDataModel(
                        grid_cell_id=grid_id_to_db_id[grid_id],
                        granularity=row["granularity"],
                        period=str(row["periode_aff"]),
                        price=float(row["Prix_Interpolé"])
                        if pd.notna(row["Prix_Interpolé"])
                        else None,
                        evolution=float(row["Evolution"]) if pd.notna(row["Evolution"]) else None,
                        log_price=float(row["Log_Prix"])
                        if "Log_Prix" in row and pd.notna(row["Log_Prix"])
                        else None,
                    )
                )

                if len(models_to_insert) >= batch_size:
                    session.add_all(models_to_insert)
                    await session.commit()
                    models_to_insert.clear()

            if models_to_insert:
                session.add_all(models_to_insert)
                await session.commit()

    print("✅ Database population complete!")


if __name__ == "__main__":
    asyncio.run(populate_db())
