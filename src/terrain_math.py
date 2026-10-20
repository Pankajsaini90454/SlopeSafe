"""Pure-numpy terrain maths. No file reading here, so it is easy to test."""
import numpy as np
 
NODATA = -9999.0
 
 
def terrain_derivatives(dem, res):
    """Return slope (deg), aspect (deg from north, -1 if flat), curvature.
 
    dem : 2D array, elevation in metres, NODATA where missing
    res : cell size in metres (square cells)
    Curvature is the Laplacian: positive = concave (hollows, valleys),
    negative = convex (ridges).
    """
    z = np.where(dem == NODATA, np.nan, dem).astype("float64")
 
    # rows increase going south, columns increase going east
    dzdy, dzdx = np.gradient(z, res)
 
    slope = np.degrees(np.arctan(np.hypot(dzdx, dzdy)))
 
    # downslope direction, clockwise from north
    aspect = np.degrees(np.arctan2(-dzdx, dzdy)) % 360
    aspect = np.where(slope < 0.5, -1.0, aspect)
 
    d2x = np.gradient(dzdx, res, axis=1)
    d2y = np.gradient(dzdy, res, axis=0)
    curvature = d2x + d2y
 
    out = []
    for arr in (slope, aspect, curvature):
        arr = np.where(np.isfinite(arr), arr, NODATA).astype("float32")
        out.append(arr)
    return tuple(out)