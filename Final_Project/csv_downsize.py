import pandas as pd
from pathlib import Path

# ---- edit these paths ----
AIRPORTS_IN  = r"C:\Users\irish\Computer_Electronic_Engineering_Year5\Knowledge_Data_Engineering\Final_Project\Data\openflights\airports.csv"
ROUTES_IN    = r"C:\Users\irish\Computer_Electronic_Engineering_Year5\Knowledge_Data_Engineering\Final_Project\Data\flight_route_database\routes.csv"

OUT_DIR      = Path(".")
AIRPORTS_OUT = OUT_DIR / "airports_region.csv"
ROUTES_OUT   = OUT_DIR / "routes_region_nonstop.csv"

KEEP = {"Ireland","United Kingdom","Germany","France","Netherlands","Spain","Portugal"}

# ---- load ----
air = pd.read_csv(AIRPORTS_IN)  # airports headers are Title Case (OK)
rt  = pd.read_csv(ROUTES_IN, low_memory=False)

# Normalize routes headers to lowercase for reliable access
rt.columns = [c.strip().lower() for c in rt.columns]
# routes expected columns after normalization:
# 'airline','airline id','source airport','source airport id',
# 'destination airport','destination airport id','codeshare','stops','equipment'

# ---- keep airports by country ----
air_keep = air[air["Country"].isin(KEEP)].copy()

# kept airport ids as ints
keep_ids = set(pd.to_numeric(air_keep["Airport ID"], errors="coerce").dropna().astype(int))

# ---- clean routes ----
# drop missing ids and keep non-stop only
rt = rt[(rt["source airport id"] != r"\N") & (rt["destination airport id"] != r"\N")].copy()
rt["source airport id"]      = pd.to_numeric(rt["source airport id"], errors="coerce").astype("Int64")
rt["destination airport id"] = pd.to_numeric(rt["destination airport id"], errors="coerce").astype("Int64")
rt["stops"] = pd.to_numeric(rt["stops"], errors="coerce").fillna(0).astype(int)

# keep routes where BOTH endpoints are in our region and stops == 0
rt_keep = rt[
    (rt["stops"] == 0) &
    (rt["source airport id"].isin(keep_ids)) &
    (rt["destination airport id"].isin(keep_ids))
].copy()

# optional: cap fan-out per origin to keep size bounded (e.g., 40)
CAP = 40
rt_keep = (rt_keep
           .sort_values(["destination airport id","airline"], na_position="last")
           .groupby("source airport id", group_keys=False)
           .head(CAP))

# deduplicate origin→destination (keep one per pair)
rt_keep = rt_keep.drop_duplicates(subset=["source airport id","destination airport id"])

# ---- write ----
AIRPORTS_OUT.parent.mkdir(parents=True, exist_ok=True)
air_keep.to_csv(AIRPORTS_OUT, index=False)
rt_keep.to_csv(ROUTES_OUT, index=False)

print("Airports kept:", len(air_keep))
print("Routes kept:", len(rt_keep))
