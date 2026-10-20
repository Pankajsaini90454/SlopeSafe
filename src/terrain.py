"""Part 2: build slope, aspect and curvature rasters from the DEM.
 
Input : data/raw/dem.tif          (SRTM 30 m GeoTIFF for the study area)
Output: data/processed/dem_utm.tif, slope.tif, aspect.tif, curvature.tif,
        slope_preview.png
 
Run from the project root:
    python src/terrain.py
"""
import numpy as np
import rasterio
from rasterio.warp import Resampling, calculate_default_transform, reproject
 
from config import CRS_METRIC
from terrain_math import NODATA, terrain_derivatives
 
RAW_DEM = "data/raw/dem.tif"
OUT_DIR = "data/processed"
RES = 30  # metres
 
 
def load_dem_metric(path, res=RES):
    """Read the DEM and reproject it to metres (UTM) so slope is correct."""
    with rasterio.open(path) as src:
        transform, width, height = calculate_default_transform(
            src.crs, CRS_METRIC, src.width, src.height, *src.bounds, resolution=res
        )
        dem = np.full((height, width), NODATA, dtype="float32")
        reproject(
            source=rasterio.band(src, 1),
            destination=dem,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=src.nodata,
            dst_transform=transform,
            dst_crs=CRS_METRIC,
            dst_nodata=NODATA,
            resampling=Resampling.bilinear,
        )
    meta = {
        "driver": "GTiff", "height": height, "width": width, "count": 1,
        "dtype": "float32", "crs": CRS_METRIC, "transform": transform,
        "nodata": NODATA, "compress": "lzw",
    }
    return dem, meta
 
 
def save(array, name, meta):
    with rasterio.open(f"{OUT_DIR}/{name}.tif", "w", **meta) as dst:
        dst.write(array, 1)
    print(f"Saved {OUT_DIR}/{name}.tif")
 
 
def preview(slope):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
 
    shown = np.ma.masked_equal(slope, NODATA)
    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(shown, cmap="YlOrBr", vmin=0, vmax=45)
    fig.colorbar(im, label="Slope (degrees)")
    ax.set_title("Slope, Guwahati study area")
    ax.axis("off")
    fig.savefig(f"{OUT_DIR}/slope_preview.png", dpi=150, bbox_inches="tight")
    print(f"Saved {OUT_DIR}/slope_preview.png")
 
 
def main():
    dem, meta = load_dem_metric(RAW_DEM)
    valid = dem[dem != NODATA]
    print(f"DEM size: {dem.shape[1]} x {dem.shape[0]} cells at {RES} m")
    print(f"Elevation: {valid.min():.0f} m to {valid.max():.0f} m")
 
    slope, aspect, curvature = terrain_derivatives(dem, RES)
    save(dem, "dem_utm", meta)
    save(slope, "slope", meta)
    save(aspect, "aspect", meta)
    save(curvature, "curvature", meta)
 
    s = slope[slope != NODATA]
    print(f"Slope: mean {s.mean():.1f} deg, max {s.max():.1f} deg, "
          f"{(s > 30).mean() * 100:.1f}% of cells steeper than 30 deg")
    preview(slope)
 
 
main()