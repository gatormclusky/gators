"""Void check + hillshade of the Takur Ghar box from a NASADEM (SRTM-derived) tile.

Usage: python3 dem_check.py NASADEM_HGT_n33e069.tif
Tile source: Planetary Computer collection `nasadem` (needs a signed URL from
https://planetarycomputer.microsoft.com/api/sas/v1/sign?href=<asset href>).
"""
import sys
import numpy as np
import rasterio
from rasterio.windows import from_bounds
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

BOX = (69.15, 33.30, 69.28, 33.40)  # W, S, E, N
PEAK = (69.21, 33.34)

with rasterio.open(sys.argv[1]) as src:
    win = from_bounds(*BOX, transform=src.transform)
    z = src.read(1, window=win).astype("float32")
    tf = src.window_transform(win)
    nodata = src.nodata
    px = abs(tf.a)

voids = (z == nodata) if nodata is not None else np.zeros_like(z, bool)
z[voids] = np.nan
print(f"cells={z.size} voids={voids.sum()} ({100*voids.mean():.2f}%) pixel={px*111320:.0f} m")
print(f"elev min={np.nanmin(z):.0f} max={np.nanmax(z):.0f} m")
col, row = ~tf * PEAK
r, c = int(row), int(col)
print(f"at peak coord: {z[r, c]:.0f} m; local max within 600 m: {np.nanmax(z[r-20:r+21, c-20:c+21]):.0f} m")
dy, dx = np.gradient(z, px * 111320 * 1.0, px * 111320 * np.cos(np.radians(33.35)))
slope = np.degrees(np.arctan(np.hypot(dx, dy)))
print(f"slope >30 deg: {100*np.nanmean(slope > 30):.1f}% of box; >45 deg: {100*np.nanmean(slope > 45):.1f}%")

ls = LightSource(azdeg=315, altdeg=35)
fig, ax = plt.subplots(figsize=(8, 7.4))
extent = (BOX[0], BOX[2], BOX[1], BOX[3])
ax.imshow(ls.hillshade(np.nan_to_num(z, nan=np.nanmean(z)), vert_exag=2, dx=px*111320, dy=px*111320), cmap="gray", extent=extent)
im = ax.imshow(z, cmap="terrain", alpha=0.45, extent=extent)
ax.plot(*PEAK, "r^", ms=9)
ax.annotate("Takur Ghar (approx.)", PEAK, xytext=(6, 8), textcoords="offset points", color="red")
fig.colorbar(im, label="elevation (m)", shrink=0.8)
ax.set_xlabel("lon"); ax.set_ylabel("lat")
ax.set_title("NASADEM (SRTM-derived, Feb 2000), ~30 m")
fig.savefig("takur_ghar_dem_hillshade.png", dpi=130, bbox_inches="tight")
