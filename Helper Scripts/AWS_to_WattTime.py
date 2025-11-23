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

rows= [
    # --- United States (North America) ---
    ("us-east-1",  "US East (N. Virginia)",  "Ashburn",         "United States", "US", 39.0438, -77.4874, ""),
    ("us-east-2",  "US East (Ohio)",        "Columbus",         "United States", "US", 39.9612, -82.9988, ""),
    ("us-west-1",  "US West (N. California)", "San Jose",       "United States", "US", 37.3382, -121.8863, ""),
    ("us-west-2",  "US West (Oregon)",      "Boardman/The Dalles", "United States", "US", 45.8380, -119.7006, ""),
    ("us-gov-east-1", "AWS GovCloud East",  "Ashburn",          "United States", "US", 39.0438, -77.4874, ""),
    ("us-gov-west-1", "AWS GovCloud West",  "Seattle Metro",    "United States", "US", 47.6062, -122.3321, ""),

    # --- Canada (North America) ---
    ("ca-central-1", "Canada Central",      "Montreal",         "Canada", "CA", 45.5017, -73.5673, ""),
    ("ca-west-1",    "Canada West",         "Calgary",          "Canada", "CA", 51.0447, -114.0719, ""),

    # --- Mexico Placeholder (announced) ---
    ("mx-central-1", "Mexico (planned)",    "Querétaro",        "Mexico", "MX", 20.5888, -100.3899, ""),

    # --- South America ---
    ("sa-east-1",    "South America East",  "São Paulo",        "Brazil", "BR", -23.5505, -46.6333, ""),

    # --- Europe ---
    ("eu-west-1",   "EU West (Ireland)",     "Dublin",          "Ireland", "IE", 53.3498,  -6.2603, ""),
    ("eu-west-2",   "EU West (London)",      "London",          "United Kingdom", "GB", 51.5074, -0.1278, ""),
    ("eu-west-3",   "EU West (Paris)",       "Paris",           "France", "FR", 48.8566, 2.3522, ""),
    ("eu-central-1","EU Central (Frankfurt)","Frankfurt",       "Germany","DE", 50.1109, 8.6821, ""),
    ("eu-central-2","EU Central 2 (Zurich)", "Zurich",          "Switzerland","CH",47.3769, 8.5417, ""),
    ("eu-north-1",  "EU North (Stockholm)",  "Stockholm",       "Sweden", "SE", 59.3293, 18.0686, ""),
    ("eu-south-1",  "EU South (Milan)",      "Milan",           "Italy", "IT", 45.4642, 9.1900, ""),
    ("eu-south-2",  "EU South 2 (Madrid)",   "Madrid",          "Spain", "ES", 40.4168, -3.7038, ""),
    ("eu-west-4",   "EU West 4 (Brussels)",  "Brussels",        "Belgium","BE", 50.8503, 4.3517, ""),
    ("eu-east-1",   "EU East (Warsaw)",      "Warsaw",          "Poland", "PL", 52.2297, 21.0122, ""),
    ("eu-east-2",   "EU East 2 (Helsinki)",  "Helsinki",        "Finland", "FI", 60.1699, 24.9384, ""),

    # --- Middle East ---
    ("il-central-1","Middle East Central",  "Tel Aviv",         "Israel", "IL", 32.0853, 34.7818, ""),
    ("me-south-1", "Middle East South",     "Bahrain/Manama",   "Bahrain", "BH", 26.2074, 50.5832, ""),
    ("me-central-1","Middle East Central 2","Dubai",            "UAE", "AE", 25.2048, 55.2708, ""),

    # --- Africa ---
    ("af-south-1",  "Africa South",         "Cape Town",        "South Africa","ZA", -33.9249,18.4241,""),

    # --- Asia ---
    ("ap-east-1",     "Asia Pacific East",  "Hong Kong",        "Hong Kong", "HK", 22.3193,114.1694, ""),
    ("ap-east-2",     "Asia Pacific East",  "Taipei",           "Taiwan", "TW", 25.03364, 121.55811, ""),
    ("ap-southeast-1","AP Southeast 1",     "Singapore",        "Singapore", "SG",  1.3521,103.8198, ""),
    ("ap-southeast-2","AP Southeast 2",     "Sydney",           "Australia","AU", -33.8688,151.2093,""),
    ("ap-southeast-3","AP Southeast 3",     "Jakarta",          "Indonesia","ID", -6.2088,106.8456,""),
    ("ap-southeast-4","AP Southeast 4",     "Melbourne",        "Australia","AU", -37.8136,144.9631,""),
    ("ap-southeast-5","AP Southeast 5",     "Kuala Lumpur",     "Malaysia","NZ", 3.1497,101.7047,""),
    ("ap-southeast-6","AP Southeast 6",     "Auckland",         "New Zealand","NZ", -36.8509,174.7645,""),
    ("ap-southeast-7","AP Southeast 7",     "Bangkok",          "Thailand","THA", 13.7580, 100.5033,""),
    ("ap-south-1",    "AP South 1",         "Mumbai",           "India", "IN", 19.0760,72.8777, ""),
    ("ap-south-2",    "AP South 2",         "Hyderabad",        "India", "IN", 17.3850,78.4867, ""),
    ("ap-northeast-1","AP Northeast 1",     "Tokyo",            "Japan", "JP", 35.6762,139.6503,""),
    ("ap-northeast-2","AP Northeast 2",     "Seoul",            "South Korea","KR", 37.5665,126.9780,""),
    ("ap-northeast-3","AP Northeast 3",     "Osaka",            "Japan", "JP", 34.6937,135.5023,"")
]



LOGIN_LEGACY = "https://api.watttime.org/login"
REGION_FROM_LOC_URL = "https://api.watttime.org/v3/region-from-loc"

from requests.auth import HTTPBasicAuth
def login():
    login_url = LOGIN_LEGACY
    rsp = requests.get(login_url, auth=HTTPBasicAuth('sabivarga', 'Lejozs456!'))
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

    # Pretty print results to the prompt (no files)
    print("\n=== Updated rows (tuple list) ===")
    print(json.dumps(updated_rows, indent=2, ensure_ascii=False))

    print("\n=== Simple mapping { AWS_region: watttime_abbrev } ===")
    print(json.dumps(mapping, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
