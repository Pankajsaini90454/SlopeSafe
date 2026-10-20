"""TEMPORARY placeholder DEM so you can test the pipeline before downloading real data.
 
!! This is SYNTHETIC. It is NOT real Guwahati terrain. !!
Never use results from it in your README, metrics, or resume.
Replace data/raw/dem.tif with the official SRTM download when you have it.
 
Run from the project root:
    python src/make_sample_dem.py
"""
import numpy as np
 
from config import STUDY_AREA
 
CELL_DEG = 0.00028  # about 30 m
NODATA = -9999.0
 
 
def smooth_noise(shape, scale, rng):
    """Smooth random field in [0, 1] made by low-pass filtering white noise."""
    noise = rng.standard_normal(shape)
    f = np.fft.fft2(noise)
    fy = np.fft.fftfreq(shape[0])[:, None]
    fx = np.fft.fftfreq(shape[1])[None, :]
    f *= np.exp(-((fx**2 + fy**2) * (scale**2)))
    field = np.real(np.fft.ifft2(f))
    field -= field.min()
    return field / field.max()
 
 
def build_elevation():
    w, e = STUDY_AREA["west"], STUDY_AREA["east"]
    s, n = STUDY_AREA["south"], STUDY_AREA["north"]
    ncols = int(round((e - w) / CELL_DEG))
    nrows = int(round((n - s) / CELL_DEG))
    rng = np.random.default_rng(42)
 
    lat = n - (np.arange(nrows) + 0.5) * CELL_DEG   # row 0 is north
    lon = w + (np.arange(ncols) + 0.5) * CELL_DEG
    LON, LAT = np.meshgrid(lon, lat)
 
    # 0 at the river plain, rising to 1 toward the south and east hills
    south_rise = np.clip((26.17 - LAT) / 0.12, 0, 1)
    east_rise = np.clip((LON - 91.75) / 0.20, 0, 1) * np.clip((26.20 - LAT) / 0.10, 0, 1)
    hill_mask = np.clip(south_rise + 0.8 * east_rise, 0, 1) ** 1.3
 
    ridges = smooth_noise((nrows, ncols), 22, rng)
    detail = smooth_noise((nrows, ncols), 6, rng)
 
    plain = 48 + 3 * smooth_noise((nrows, ncols), 90, rng)
    hills = 60 + 380 * ridges * hill_mask + 30 * detail * hill_mask
    # a few isolated hills inside the city, like Nilachal
    city_hills = 70 * smooth_noise((nrows, ncols), 45, rng) ** 4 * (1 - hill_mask)
 
    dem = plain + hills * hill_mask + city_hills
    return dem.astype("float32")
 
 
def main():
    import rasterio
    from rasterio.transform import from_origin
 
    dem = build_elevation()
    transform = from_origin(STUDY_AREA["west"], STUDY_AREA["north"], CELL_DEG, CELL_DEG)
    with rasterio.open(
        "data/raw/dem.tif", "w", driver="GTiff", height=dem.shape[0],
        width=dem.shape[1], count=1, dtype="float32", crs="EPSG:4326",
        transform=transform, nodata=NODATA, compress="lzw",
    ) as dst:
        dst.write(dem, 1)
    print(f"Saved data/raw/dem.tif ({dem.shape[1]} x {dem.shape[0]} cells)")
    print(f"Elevation: {dem.min():.0f} m to {dem.max():.0f} m  (SYNTHETIC)")
 
 
if __name__ == "__main__":
    main()