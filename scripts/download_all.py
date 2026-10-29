import subprocess
import sys
import time

python_bin = sys.executable

print("=== Step 1: Downloading Markets Table ===")
t0 = time.time()
res1 = subprocess.run([python_bin, "scripts/download_markets.py"])
if res1.returncode != 0:
    print(f"Failed with return code {res1.returncode}")
    sys.exit(res1.returncode)

print(f"\nMarkets completed in {time.time() - t0:.1f}s.")

print("\n=== Step 2: Downloading Wallet Trades ===")
t1 = time.time()
res2 = subprocess.run([python_bin, "scripts/download_wallet_trades.py"])
if res2.returncode != 0:
    print(f"Failed with return code {res2.returncode}")
    sys.exit(res2.returncode)

print(f"\nAll downloads completed successfully in {time.time() - t0:.1f}s!")
