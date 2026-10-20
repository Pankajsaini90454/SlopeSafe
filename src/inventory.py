"""Part 3: clean the landslide inventory and draw it on a map.
 
Input : data/raw/landslides.csv   (columns: lat, lon  +  optional date, source,
                                    confidence, notes)
Output: data/processed/landslides_clean.csv
        landslides_map.html
 
Run from the project root:
    python src/inventory.py
"""
import numpy as np
import pandas as pd
 
from config import BOUNDS, CENTER, STUDY_AREA
 
RAW = "data/raw/landslides.csv"
CLEAN = "data/processed/landslides_clean.csv"
DEDUPE_METRES = 50
 
 
def clean(df):
    """Return (clean_df, log) where log lists how many rows each step removed."""
    log = [("rows read", len(df))]
 
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    missing = {"lat", "lon"} - set(df.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {sorted(missing)}")
 
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"])
    log.append(("valid coordinates", len(df)))
 
    inside = (
        df["lat"].between(STUDY_AREA["south"], STUDY_AREA["north"])
        & df["lon"].between(STUDY_AREA["west"], STUDY_AREA["east"])
    )
    df = df[inside]
    log.append(("inside study area", len(df)))
 
    for col, default in (("source", "unknown"), ("confidence", "medium"),
                         ("date", ""), ("notes", "")):
        if col not in df.columns:
            df[col] = default
        df[col] = df[col].fillna(default)
    df["confidence"] = df["confidence"].astype(str).str.lower().str.strip()
 
    # keep the higher-confidence record when two points are within 50 m
    rank = {"high": 0, "medium": 1, "low": 2}
    df = df.assign(_r=df["confidence"].map(rank).fillna(1)).sort_values("_r")
    lat = df["lat"].to_numpy()
    lon = df["lon"].to_numpy()
    keep = np.ones(len(df), dtype=bool)
    m_per_deg = 111_000
    for i in range(len(df)):
        if not keep[i]:
            continue
        dy = (lat - lat[i]) * m_per_deg
        dx = (lon - lon[i]) * m_per_deg * np.cos(np.radians(lat[i]))
        close = (dx**2 + dy**2) < DEDUPE_METRES**2
        close[: i + 1] = False
        keep[close] = False
    df = df[keep].drop(columns="_r").reset_index(drop=True)
    df.insert(0, "id", range(1, len(df) + 1))
    log.append((f"after removing duplicates (<{DEDUPE_METRES} m)", len(df)))
    return df, log
 
 
def draw_map(df, path="landslides_map.html"):
    import folium
 
    m = folium.Map(location=CENTER, zoom_start=11, tiles=None)
    folium.TileLayer("OpenStreetMap", name="Street").add_to(m)
    folium.TileLayer(
        tiles=("https://server.arcgisonline.com/ArcGIS/rest/services/"
               "World_Imagery/MapServer/tile/{z}/{y}/{x}"),
        attr="Esri World Imagery", name="Satellite",
    ).add_to(m)
    folium.TileLayer("OpenTopoMap", name="Terrain").add_to(m)
    folium.Rectangle(BOUNDS, color="red", weight=2, fill=False).add_to(m)
 
    colors = {"high": "red", "medium": "orange", "low": "gray"}
    group = folium.FeatureGroup(name="Past landslides")
    for r in df.itertuples():
        folium.CircleMarker(
            [r.lat, r.lon], radius=5, color=colors.get(r.confidence, "orange"),
            fill=True, fill_opacity=0.8,
            popup=f"#{r.id} | {r.source} | {r.date} | confidence: {r.confidence}",
        ).add_to(group)
    group.add_to(m)
    folium.LayerControl().add_to(m)
    m.save(path)
    print(f"Saved {path}")
 
 
def main():
    df, log = clean(pd.read_csv(RAW))
    for step, n in log:
        print(f"{step:<42}{n:>6}")
    print("\nBy source:")
    print(df["source"].value_counts().to_string())
    print("\nBy confidence:")
    print(df["confidence"].value_counts().to_string())
 
    df.to_csv(CLEAN, index=False)
    print(f"\nSaved {CLEAN}")
    draw_map(df)
    if len(df) < 50:
        print("\nWARNING: fewer than 50 landslide points. A model trained on this "
              "will be weak. See the plan for small inventories.")
 
 
if __name__ == "__main__":
    main()