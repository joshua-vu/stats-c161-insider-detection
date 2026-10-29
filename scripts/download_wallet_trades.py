import os
import base64
import urllib.request
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

USER = "polymarketdatabase"
PASS = "PolymarketData2026!"
HOST = "d1yyqbluk0oz0t.cloudfront.net"

auth_str = base64.b64encode(f"{USER}:{PASS}".encode()).decode()
headers = {"Authorization": f"Basic {auth_str}"}

output_dir = "data/wallet_trades"
os.makedirs(output_dir, exist_ok=True)

start_date = date(2026, 5, 30)
end_date = date(2026, 10, 29)

dates = []
curr = start_date
while curr <= end_date:
    dates.append(curr.strftime("%Y-%m-%d"))
    curr += timedelta(days=1)

def download_day(d):
    file_name = f"trades-{d}.parquet"
    local_path = os.path.join(output_dir, file_name)
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return d, "already_exists", os.path.getsize(local_path)
    
    url = f"https://{HOST}/wallet_trades/{file_name}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            with open(local_path, "wb") as f:
                f.write(content)
            return d, "downloaded", len(content)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return d, "not_found", 0
        return d, f"http_error_{e.code}", 0
    except Exception as e:
        return d, f"error_{str(e)}", 0

print(f"Scanning & downloading wallet trade history across {len(dates)} days...")
total_downloaded = 0
total_bytes = 0

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = {executor.submit(download_day, d): d for d in dates}
    for future in as_completed(futures):
        d, status, sz = future.result()
        if status == "downloaded":
            total_downloaded += 1
            total_bytes += sz
            print(f"[{d}] Downloaded ({sz / (1024*1024):.2f} MB)")
        elif status == "already_exists":
            total_bytes += sz
        elif status != "not_found":
            print(f"[{d}] Status: {status}")

total_mb = total_bytes / (1024 * 1024)
print(f"Finished wallet trades! Total size on disk: {total_mb:.2f} MB ({total_mb / 1024:.2f} GB)")
