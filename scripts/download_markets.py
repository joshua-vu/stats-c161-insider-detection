import os
import time
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
db_url = os.environ["JUNE_DB_URL"]
engine = create_engine(db_url, connect_args={"sslmode": "require"})

output_path = "data/catalog/markets.parquet"
temp_output = "data/catalog/markets_temp.parquet"

print("Starting download of 'markets' table in chunks of 100,000 rows...")
t_start = time.time()

chunk_size = 100_000
writer = None
total_rows = 0

query = "SELECT * FROM markets"

try:
    with engine.connect().execution_options(stream_results=True) as conn:
        for i, chunk in enumerate(pd.read_sql(query, conn, chunksize=chunk_size)):
            # Convert jsonb / dict objects to string for stable parquet schema
            for col in chunk.columns:
                if chunk[col].dtype == object and len(chunk) > 0:
                    sample = chunk[col].dropna().iloc[0] if not chunk[col].dropna().empty else None
                    if isinstance(sample, (dict, list)):
                        import json
                        chunk[col] = chunk[col].apply(lambda x: json.dumps(x) if x is not None else None)

            table = pa.Table.from_pandas(chunk, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(temp_output, table.schema, compression="snappy")
            writer.write_table(table)
            total_rows += len(chunk)
            print(f"Downloaded chunk {i+1}: {total_rows:,} rows total ({time.time() - t_start:.1f}s)")
finally:
    if writer:
        writer.close()

if os.path.exists(temp_output):
    os.replace(temp_output, output_path)
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Finished! Successfully saved {total_rows:,} rows to {output_path} ({file_size_mb:.2f} MB) in {time.time() - t_start:.1f}s")
