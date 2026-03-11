import asyncio
import subprocess

import pandas as pd
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from app.core.settings import settings
from app.domains.data_pipeline.infrastructure.models import RawTransactionModel


async def ingest() -> None:
    print("Starting DVF data ingestion...")
    engine = create_async_engine(str(settings.db.sqlalchemy_database_uri))
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    file_path = "data/raw/2020/full.csv"
    chunksize = 20000

    # Quick line count for progress bar
    result = subprocess.run(["wc", "-l", file_path], capture_output=True, text=True)
    total_rows = int(result.stdout.split()[0]) - 1  # minus header

    float_cols = [
        "valeur_fonciere",
        "lot1_surface_carrez",
        "lot2_surface_carrez",
        "lot3_surface_carrez",
        "lot4_surface_carrez",
        "lot5_surface_carrez",
        "nombre_lots",
        "surface_reelle_bati",
        "nombre_pieces_principales",
        "surface_terrain",
        "longitude",
        "latitude",
    ]

    # We first empty the table to ensure idempotency
    print("Truncating table raw_transactions...")
    async with engine.begin() as conn:
        await conn.execute(RawTransactionModel.__table__.delete())

    print(f"Ingesting {total_rows} rows from {file_path}...")

    # Use pandas chunking
    with pd.read_csv(file_path, chunksize=chunksize, dtype=str, low_memory=False) as reader:
        for chunk in tqdm(reader, total=(total_rows // chunksize) + 1):
            # Convert float columns
            for col in float_cols:
                if col in chunk.columns:
                    chunk[col] = pd.to_numeric(chunk[col], errors="coerce")

            # Convert date
            if "date_mutation" in chunk.columns:
                chunk["date_mutation"] = pd.to_datetime(chunk["date_mutation"]).dt.date

            # Convert to list of dictionaries
            records = chunk.to_dict(orient="records")

            # Clean up NaNs / NaTs
            for record in records:
                for k, v in record.items():
                    if pd.isna(v):
                        record[k] = None

            async with async_session() as session, session.begin():
                # Fast bulk insert
                await session.execute(insert(RawTransactionModel), records)

    await engine.dispose()
    print("Ingestion complete.")


if __name__ == "__main__":
    asyncio.run(ingest())
