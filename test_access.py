import os
import duckdb
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# 1. Load the database password from the .env file
load_dotenv()
db_url = os.getenv("JUNE_DB_URL")

# --- TEST 1: Querying Postgres (Supabase - Market Metadata) ---
print("=== 1. Testing Postgres (Supabase) ===")
try:
    engine = create_engine(db_url, connect_args={"sslmode": "require"})
    
    # Query 5 active markets
    query = """
        SELECT slug, title, best_bid, best_ask, volume_1wk 
        FROM markets 
        WHERE end_date > now() 
        ORDER BY volume_1wk DESC NULLS LAST 
        LIMIT 5;
    """
    with engine.connect() as conn:
        df_markets = pd.read_sql(text(query), conn)
    
    print("Success! Top 5 markets by 1-week volume:")
    print(df_markets)
except Exception as e:
    print(f"Error connecting to Postgres: {e}")

# --- TEST 2: Querying S3 / CloudFront Order Books via DuckDB ---
print("\n=== 2. Testing S3/CloudFront Order Books (DuckDB) ===")
try:
    import base64
    USER = "polymarketdatabase"
    PASS = "PolymarketData2026!"
    HOST = "d1yyqbluk0oz0t.cloudfront.net"
    
    # Enable HTTP file system support and configure Basic Auth in DuckDB
    duckdb.sql("INSTALL httpfs; LOAD httpfs;")
    auth_b64 = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
    duckdb.sql(f"CREATE SECRET IF NOT EXISTS cf_auth (TYPE HTTP, EXTRA_HTTP_HEADERS MAP {{'Authorization': 'Basic {auth_b64}'}});")
    
    events_url = f"https://{HOST}/events-2026-05-30T21.parquet"
    
    # Inspect the first 5 order book changes
    df_events = duckdb.sql(f"""
        SELECT ts_ms, side, price, size 
        FROM '{events_url}' 
        LIMIT 5;
    """).df()
    
    print("Success! Sample order-book delta rows:")
    print(df_events)
except Exception as e:
    print(f"Error querying CloudFront Parquet: {e}")

# --- TEST 3: Querying Wallet Trades via DuckDB ---
print("\n=== 3. Testing S3/CloudFront Wallet Trades (DuckDB) ===")
try:
    trades_url = f"https://{HOST}/wallet_trades/trades-2026-10-05.parquet"
    
    # Group top 5 wallets by volume in a tennis match
    df_trades = duckdb.sql(f"""
        SELECT wallet, round(sum(dollars)) AS volume, count(*) AS trades
        FROM '{trades_url}'
        WHERE market = 'atp-djokovi-medvede-2026-10-05'
        GROUP BY wallet 
        ORDER BY volume DESC 
        LIMIT 5;
    """).df()
    
    print("Success! Sample wallet trade volume:")
    print(df_trades)
except Exception as e:
    print(f"Error querying Wallet Trades: {e}")