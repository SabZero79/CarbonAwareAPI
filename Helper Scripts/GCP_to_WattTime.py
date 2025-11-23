#!/usr/bin/env python3
"""
Resolve GCP -> WattTime regions (prints to stdout only).

Usage:
  python gcp_to_watttime.py [--signal co2_moer] [--sleep 0.25] [--retries 3]

Notes:
- Prefers WattTime `region.abbrev` (e.g., PJM_DC, CAISO_SOMETHING). Falls back to `name` or `id`.
- Uses your provided `rows` list as input; updates its last element with the resolved abbrev/name.
"""

import os
import time
import json
import argparse
import requests

rows = [
    # --- North America ---
    ("us-west1", "Oregon", "The Dalles", "United States", "US", 45.5946, -121.1787, ""),
    ("us-west2", "Los Angeles", "Los Angeles", "United States", "US", 34.0522, -118.2437, ""),
    ("us-west3", "Salt Lake City", "Salt Lake City", "United States", "US", 40.7608, -111.8910, ""),
    ("us-west4", "Las Vegas", "Las Vegas", "United States", "US", 36.1699, -115.1398, ""),
    ("us-central1", "Iowa", "Council Bluffs", "United States", "US", 41.2619, -95.8608, ""),
    ("us-east1", "South Carolina", "Moncks Corner", "United States", "US", 33.1954, -80.0131, ""),
    ("us-east4", "Northern Virginia", "Ashburn", "United States", "US", 39.0438, -77.4874, ""),
    ("us-east5", "Columbus", "Columbus", "United States", "US", 39.9612, -82.9988, ""),
    ("us-south1", "Dallas", "Dallas", "United States", "US", 32.7767, -96.7970, ""),
    ("northamerica-northeast1", "Montréal", "Montréal", "Canada", "CA", 45.5017, -73.5673, ""),
    ("northamerica-northeast2", "Toronto", "Toronto", "Canada", "CA", 43.6532, -79.3832, ""),
    ("northamerica-south1", "Querétaro", "Querétaro", "Mexico", "MX", 20.5888, -100.3899, ""),
    # --- South America ---
    ("southamerica-east1", "São Paulo (Osasco)", "São Paulo", "Brazil", "BR", -23.5505, -46.6333, ""),
    ("southamerica-west1", "Santiago", "Santiago", "Chile", "CL", -33.4489, -70.6693, ""),
    # --- Europe ---
    ("europe-west1", "St. Ghislain", "St. Ghislain", "Belgium", "BE", 50.4530, 3.8060, ""),
    ("europe-west2", "London", "London", "United Kingdom", "GB", 51.5074, -0.1278, ""),
    ("europe-west3", "Frankfurt", "Frankfurt", "Germany", "DE", 50.1109, 8.6821, ""),
    ("europe-west4", "Eemshaven", "Eemshaven", "Netherlands", "NL", 53.4490, 6.8310, ""),
    ("europe-west6", "Zürich", "Zürich", "Switzerland", "CH", 47.3769, 8.5417, ""),
    ("europe-west8", "Milan", "Milan", "Italy", "IT", 45.4642, 9.1900, ""),
    ("europe-west9", "Paris", "Paris", "France", "FR", 48.8566, 2.3522, ""),
    ("europe-west10", "Berlin", "Berlin", "Germany", "DE", 52.5200, 13.4050, ""),
    ("europe-west12", "Turin", "Turin", "Italy", "IT", 45.0703, 7.6869, ""),
    ("europe-central2", "Warsaw", "Warsaw", "Poland", "PL", 52.2297, 21.0122, ""),
    ("europe-north1", "Hamina", "Hamina", "Finland", "FI", 60.5697, 27.1977, ""),
    ("europe-north2", "Stockholm", "Stockholm", "Sweden", "SE", 59.3293, 18.0686, ""),
    ("europe-southwest1", "Madrid", "Madrid", "Spain", "ES", 40.4168, -3.7038, ""),
    # --- Middle East ---
    ("me-west1", "Tel Aviv", "Tel Aviv", "Israel", "IL", 32.0853, 34.7818, ""),
    ("me-central1", "Doha", "Doha", "Qatar", "QA", 25.2854, 51.5310, ""),
    ("me-central2", "Dammam", "Dammam", "Saudi Arabia", "SA", 26.4207, 50.0888, ""),
    # --- Africa ---
    ("africa-south1", "Johannesburg", "Johannesburg", "South Africa", "ZA", -26.2041, 28.0473, ""),
    # --- Asia ---
    ("asia-south1", "Mumbai", "Mumbai", "India", "IN", 19.0760, 72.8777, ""),
    ("asia-south2", "Delhi", "Delhi", "India", "IN", 28.6139, 77.2090, ""),
    ("asia-southeast1", "Singapore", "Singapore", "Singapore", "SG", 1.3521, 103.8198, ""),
    ("asia-southeast2", "Jakarta", "Jakarta", "Indonesia", "ID", -6.2088, 106.8456, ""),
    ("asia-east1", "Changhua County", "Changhua County", "Taiwan", "TW", 24.0518, 120.5160, ""),
    ("asia-east2", "Hong Kong", "Hong Kong", "Hong Kong", "HK", 22.3193, 114.1694, ""),
    ("asia-northeast1", "Tokyo", "Tokyo", "Japan", "JP", 35.6762, 139.6503, ""),
    ("asia-northeast2", "Osaka", "Osaka", "Japan", "JP", 34.6937, 135.5023, ""),
    ("asia-northeast3", "Seoul", "Seoul", "South Korea", "KR", 37.5665, 126.9780, ""),
    # --- Australia ---
    ("australia-southeast1", "Sydney", "Sydney", "Australia", "AU", -33.8688, 151.2093, ""),
    ("australia-southeast2", "Melbourne", "Melbourne", "Australia", "AU", -37.8136, 144.9631, ""),
]

LOGIN_LEGACY = "https://api.watttime.org/login"
REGION_FROM_LOC_URL = "https://api.watttime.org/v3/region-from-loc"

from requests.auth import HTTPBasicAuth
def login():
    login_url = LOGIN_LEGACY
    rsp = requests.get(login_url, auth=HTTPBasicAuth('sabivarga', 'password'))
    TOKEN = rsp.json()['token']
    return TOKEN

def region_from_loc(token, lat, lon, signal="co2_moer", timeout=20, retries=3, backoff=0.6):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"latitude": lat, "longitude": lon, "signal_type": signal}
    last = None
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(REGION_FROM_LOC_URL, headers=headers, params=params, timeout=timeout)
            if resp.status_code == 401:
                raise RuntimeError("Unauthorized (401). Check credentials.")
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            last = e
            time.sleep(backoff * attempt)
    raise last

def normalize_region_abbrev(data) -> str:
    """
    Accepts any of:
      - "PJM_DC"
      - {"region": "PJM_DC"}
      - {"region": {"abbrev": "PJM_DC", "name": "...", "id": "..."}}
      - {"abbrev": "...", "name": "...", "id": "..."}
    Returns a single canonical abbrev string (falls back to name/id), else "UNKNOWN".
    """
    # Bare string
    if isinstance(data, str):
        return data.strip() or "UNKNOWN"

    # Dict forms
    if isinstance(data, dict):
        # Common case: {"region": ...}
        inner = data.get("region", data)

        # If inner is a bare string
        if isinstance(inner, str):
            return inner.strip() or "UNKNOWN"

        # If inner is a dict with fields
        if isinstance(inner, dict):
            return inner.get("abbrev") or inner.get("name") or inner.get("id") or "UNKNOWN"

    # Any other type (list/None/etc.)
    return "UNKNOWN"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--signal", default="co2_moer", help="WattTime signal_type (default: co2_moer)")
    ap.add_argument("--sleep", type=float, default=0.25, help="Delay between calls (seconds)")
    ap.add_argument("--retries", type=int, default=3, help="Retries per API call")
    ap.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout seconds")
    args = ap.parse_args()

    token = login()

    updated_rows = []
    mapping = {}  # { gcp_region: resolved_abbrev }
    for tup in rows:
        (gcp_region, display_name, city, country, cc, lat, lon, _seed) = tup
        try:
            data = region_from_loc(token, lat, lon, signal=args.signal,
                                   timeout=args.timeout, retries=args.retries)
            # prefer abbrev (e.g., PJM_DC), else name, else id
            abbrev = normalize_region_abbrev(data)
            updated_rows.append((gcp_region, display_name, city, country, cc, lat, lon, abbrev))
            mapping[gcp_region] = abbrev
            print(f"[OK] {gcp_region:>22} @ ({lat:.4f}, {lon:.4f}) -> {abbrev}")
        except Exception as e:
            # Preserve seed if lookup fails
            updated_rows.append((gcp_region, display_name, city, country, cc, lat, lon, _seed))
            mapping[gcp_region] = _seed
            print(f"[WARN] {gcp_region:>22} failed: {e}")

        time.sleep(args.sleep)

    # Pretty print results to the prompt
    print("\n=== Updated rows (tuple list) ===")
    print(json.dumps(updated_rows, indent=2, ensure_ascii=False))

    print("\n=== Simple mapping { GCP_region: watttime_abbrev } ===")
    print(json.dumps(mapping, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
