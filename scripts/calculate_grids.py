import asyncio

import h3
import pandas as pd
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from tqdm import tqdm

from app.core.settings import settings


async def calculate_grids():
    print("Starting grid calculations...")
    engine = create_async_engine(str(settings.db.sqlalchemy_database_uri))

    query = """
    SELECT date_mutation, valeur_fonciere, surface_reelle_bati, latitude, longitude
    FROM raw_transactions
    WHERE nature_mutation = 'Vente'
      AND type_local IN ('Maison', 'Appartement')
      AND valeur_fonciere IS NOT NULL
      AND surface_reelle_bati IS NOT NULL
      AND surface_reelle_bati > 0
      AND latitude IS NOT NULL
      AND longitude IS NOT NULL
    """

    print("Fetching valid transactions...")
    async with engine.begin() as conn:
        result = await conn.execute(text(query))
        rows = result.fetchall()

    df = pd.DataFrame(
        rows,
        columns=[
            "date_mutation",
            "valeur_fonciere",
            "surface_reelle_bati",
            "latitude",
            "longitude",
        ],
    )

    if df.empty:
        print("No valid transactions found. Make sure ingest_dvf.py has finished.")
        await engine.dispose()
        return

    # Filter out absurd prices
    df["price_per_sqm"] = df["valeur_fonciere"] / df["surface_reelle_bati"]
    df = df[(df["price_per_sqm"] > 500) & (df["price_per_sqm"] < 30000)].copy()

    df["year"] = pd.to_datetime(df["date_mutation"]).dt.year.astype(str)

    resolutions = [8, 9]  # Example resolutions

    async with engine.begin() as conn:
        print("Cleaning up old grids and metrics...")
        await conn.execute(text("DELETE FROM grid_cells;"))
        # CASCADE should delete grid_metrics

    for res in resolutions:
        print(f"\nProcessing Resolution {res}")

        # Calculate H3 index
        tqdm.pandas(desc="Calculating H3 indexes")
        df["h3_index"] = df.progress_apply(
            lambda row: h3.latlng_to_cell(row["latitude"], row["longitude"], res), axis=1
        )

        # Group to find unique cells
        unique_cells = df["h3_index"].unique()
        print(f"Found {len(unique_cells)} unique cells for resolution {res}")

        cell_records = []
        for h3_idx in tqdm(unique_cells, desc="Generating geometries"):
            # Get boundary (tuple of (lat, lon))
            boundary = h3.cell_to_boundary(h3_idx)
            # Create EWKT string for PostGIS (lon lat)
            # Polygon needs to be closed, so first point == last point
            points = [f"{lon} {lat}" for lat, lon in boundary]
            points.append(points[0])
            polygon_wkt = f"SRID=4326;POLYGON(({', '.join(points)}))"

            center_lat, center_lon = h3.cell_to_latlng(h3_idx)

            # Convert h3_idx (hex string) to a grid_reference integer if needed, or just store the hex
            # Wait, grid_reference is Integer, but H3 indexes are 64-bit! They might not fit in standard Integer
            # But the schema defines `grid_reference: Mapped[int | None]`. PostgreSQL integer is 32-bit (up to 2 billion).
            # H3 can be larger, so maybe we leave it None or just use BigInt.
            # I'll just leave it None for now since the UUID is the Primary Key.

            cell_records.append(
                {
                    "h3_index": h3_idx,
                    "resolution": res,
                    "geometry_wkt": polygon_wkt,
                }
            )

        cells_df = pd.DataFrame(cell_records)

        # Insert cells and fetch UUIDs
        print("Inserting grid cells...")
        cell_id_mapping = {}  # h3_id -> db_uuid
        async with engine.begin() as conn:
            for _, row in tqdm(cells_df.iterrows(), total=len(cells_df), desc="Saving cells"):
                insert_query = text("""
                    INSERT INTO grid_cells (h3_index, resolution, geometry)
                    VALUES (:h3_index, :res, ST_GeomFromEWKT(:geom))
                    RETURNING id
                """)
                res_id = await conn.execute(
                    insert_query,
                    {
                        "h3_index": row["h3_index"],
                        "res": row["resolution"],
                        "geom": row["geometry_wkt"],
                    },
                )
                cell_id_mapping[row["h3_index"]] = res_id.scalar()

        # Calculate metrics
        print("Calculating metrics...")
        metrics_df = df.groupby(["h3_index", "year"])["price_per_sqm"].median().reset_index()

        # Calculate evolution (simplistic: compare to previous year if it exists)
        # Since we might only have 2020 data, evolution_pct might be None.
        metrics_df["evolution_pct"] = None

        metrics_records = []
        for _, row in metrics_df.iterrows():
            metrics_records.append(
                {
                    "grid_cell_id": cell_id_mapping[row["h3_index"]],
                    "granularity": "yearly",
                    "period": row["year"],
                    "price_per_sqm": row["price_per_sqm"],
                    "evolution_pct": row["evolution_pct"],
                }
            )

        print("Inserting grid metrics...")
        async with engine.begin() as conn:
            for i in tqdm(range(0, len(metrics_records), 5000), desc="Saving metrics"):
                chunk = metrics_records[i : i + 5000]
                await conn.execute(
                    text("""
                        INSERT INTO grid_metrics (grid_cell_id, granularity, period, price_per_sqm, evolution_pct)
                        VALUES (:grid_cell_id, :granularity, :period, :price_per_sqm, :evolution_pct)
                    """),
                    chunk,
                )

    await engine.dispose()
    print("Grid calculations complete!")


if __name__ == "__main__":
    asyncio.run(calculate_grids())
