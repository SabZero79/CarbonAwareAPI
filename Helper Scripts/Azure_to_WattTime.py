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
    # --- United States (North America) ---
    ("eastus",           "East US",             "Boydton (Virginia)",        "United States", "US", 36.6670, -78.3875, ""),
    ("eastus2",          "East US 2",           "Boydton (Virginia)",        "United States", "US", 36.6670, -78.3875, ""),
    ("centralus",        "Central US",          "Des Moines (Iowa)",         "United States", "US", 41.5868, -93.6250, ""),
    ("northcentralus",   "North Central US",    "Chicago (Illinois)",        "United States", "US", 41.8781, -87.6298, ""),
    ("southcentralus",   "South Central US",    "San Antonio (Texas)",       "United States", "US", 29.4241, -98.4936, ""),
    ("westus",           "West US",             "San Jose (California)",     "United States", "US", 37.3382, -121.8863, ""),
    ("westus2",          "West US 2",           "Quincy (Washington)",       "United States", "US", 47.2343, -119.8524, ""),
    ("westus3",          "West US 3",           "Phoenix (Arizona)",         "United States", "US", 33.4484, -112.0740, ""),
    ("westcentralus",    "West Central US",     "Cheyenne (Wyoming)",        "United States", "US", 41.1400, -104.8202, ""),
    ("eastus3",          "East US 3",           "Atlanta (Georgia)",         "United States", "US", 33.7490, -84.3880, ""),
    ("westcentralus2",   "West Central US 2",   "Denver Metro (Colorado)",   "United States", "US", 39.7392, -104.9903, ""),

    # --- Canada (North America) ---
    ("canadacentral",    "Canada Central",      "Toronto (Ontario)",         "Canada",        "CA", 43.6532, -79.3832, ""),
    ("canadaeast",       "Canada East",         "Québec City (Québec)",      "Canada",        "CA", 46.8139, -71.2080, ""),

    # --- Mexico (North America) ---
    ("mexicocentral",    "Mexico Central",      "Querétaro",                 "Mexico",        "MX", 20.5888, -100.3899, ""),

    # --- South America ---
    ("brazilsouth",      "Brazil South",        "São Paulo State",           "Brazil",        "BR", -23.5505, -46.6333, ""),
    ("brazilsoutheast",  "Brazil Southeast",    "Rio de Janeiro",            "Brazil",        "BR", -22.9068, -43.1729, ""),
    ("chilecentral",     "Chile Central",       "Santiago",                  "Chile",         "CL", -33.4489, -70.6693, ""),

    # --- Europe ---
    ("northeurope",      "North Europe",        "Dublin",                    "Ireland",       "IE", 53.3498,  -6.2603, ""),
    ("westeurope",       "West Europe",         "Amsterdam / NL",            "Netherlands",   "NL", 52.3676,   4.9041, ""),
    ("ukSouth",          "UK South",            "London",                    "United Kingdom","GB", 51.5074,  -0.1278, ""),
    ("ukwest",           "UK West",             "Cardiff",                   "United Kingdom","GB", 51.4816,  -3.1791, ""),
    ("francecentral",    "France Central",      "Paris",                     "France",        "FR", 48.8566,   2.3522, ""),
    ("francesouth",      "France South",        "Marseille",                 "France",        "FR", 43.2965,   5.3698, ""),
    ("switzerlandnorth", "Switzerland North",   "Zürich",                    "Switzerland",   "CH", 47.3769,   8.5417, ""),
    ("switzerlandwest",  "Switzerland West",    "Geneva",                    "Switzerland",   "CH", 46.2044,   6.1432, ""),
    ("germanywestcentral","Germany West Central","Frankfurt am Main",        "Germany",       "DE", 50.1109,   8.6821, ""),
    ("germanynorth",     "Germany North",       "Berlin",                    "Germany",       "DE", 52.5200,  13.4050, ""),
    ("norwayeast",       "Norway East",         "Oslo",                      "Norway",        "NO", 59.9139,  10.7522, ""),
    ("norwaywest",       "Norway West",         "Stavanger",                 "Norway",        "NO", 58.9690,   5.7331, ""),
    ("swedencentral",    "Sweden Central",      "Gävle/Sandviken",           "Sweden",        "SE", 60.6749,  17.1413, ""),
    ("swedensouth",      "Sweden South",        "Malmö region",              "Sweden",        "SE", 55.6049,  13.0038, ""),
    ("polandcentral",    "Poland Central",      "Warsaw",                    "Poland",        "PL", 52.2297,  21.0122, ""),
    ("italynorth",       "Italy North",         "Milan",                     "Italy",         "IT", 45.4642,   9.1900, ""),
    ("spaincentral",     "Spain Central",       "Madrid",                    "Spain",         "ES", 40.4168,  -3.7038, ""),
    ("austriacenter",    "Austria East",        "Vienna (metro)",            "Austria",       "AT", 48.2082,  16.3738, ""),

    # --- Middle East ---
    ("uaenorth",         "UAE North",           "Dubai",                     "United Arab Emirates","AE", 25.2048, 55.2708, ""),
    ("uaecentral",       "UAE Central",         "Abu Dhabi",                 "United Arab Emirates","AE", 24.4539, 54.3773, ""),
    ("qatarcentral",     "Qatar Central",       "Doha",                      "Qatar",         "QA", 25.2854,  51.5310, ""),
    ("israelcentral",    "Israel Central",      "Tel Aviv (metro)",          "Israel",        "IL", 32.0853,  34.7818, ""),
    ("saudiarabiaeast",  "Saudi Arabia East",   "Dammam (metro)",            "Saudi Arabia",  "SA", 26.4207,  50.0888, ""),
    ("saudiarabiacentral","Saudi Arabia Central","Jeddah (metro)",           "Saudi Arabia",  "SA", 21.4858,  39.1925, ""),

    # --- Africa ---
    ("southafricanorth", "South Africa North",  "Johannesburg",              "South Africa",  "ZA", -26.2041,  28.0473, ""),
    ("southafricawest",  "South Africa West",   "Cape Town",                 "South Africa",  "ZA", -33.9249,  18.4241, ""),

    # --- Asia ---
    ("eastasia",         "East Asia",           "Hong Kong",                 "Hong Kong",     "HK", 22.3193, 114.1694, ""),
    ("southeastasia",    "Southeast Asia",      "Singapore",                 "Singapore",     "SG",  1.3521, 103.8198, ""),
    ("japaneast",        "Japan East",          "Tokyo/Saitama",             "Japan",         "JP", 35.6762, 139.6503, ""),
    ("japanwest",        "Japan West",          "Osaka",                     "Japan",         "JP", 34.6937, 135.5023, ""),
    ("koreacentral",     "Korea Central",       "Seoul",                     "South Korea",   "KR", 37.5665, 126.9780, ""),
    ("koreasouth",       "Korea South",         "Busan",                     "South Korea",   "KR", 35.1796, 129.0756, ""),
    ("centralindia",     "Central India",       "Pune",                      "India",         "IN", 18.5204,  73.8567, ""),
    ("southindia",       "South India",         "Chennai",                   "India",         "IN", 13.0827,  80.2707, ""),
    ("westindia",        "West India",          "Mumbai",                    "India",         "IN", 19.0760,  72.8777, ""),
    ("indonesiacentral", "Indonesia Central",   "Jakarta",                   "Indonesia",     "ID", -6.2088, 106.8456, ""),
    ("malaysiawest",    "Malaysia West",      "Kuala Lumpur (metro)",        "Malaysia",      "MY",  3.1390, 101.6869, ""),
    ("taiwannorth",      "Taiwan North",        "Taipei (metro)",            "Taiwan",        "TW", 25.0330, 121.5654, ""),

    # --- Oceania ---
    ("australiaeast",    "Australia East",      "Sydney",                    "Australia",     "AU", -33.8688, 151.2093, ""),
    ("australiasoutheast","Australia Southeast","Melbourne",                 "Australia",     "AU", -37.8136, 144.9631, ""),
    ("australiacentral", "Australia Central",   "Canberra (restricted)",     "Australia",     "AU", -35.2809, 149.1300, ""),
    ("newzealandnorth",  "New Zealand North",   "Auckland",                  "New Zealand",   "NZ", -36.8509, 174.7645, ""),
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

    print("\n=== Simple mapping { Azure_region: watttime_abbrev } ===")
    print(json.dumps(mapping, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
