"""Sun, shadow and line-of-sight analysis for the Takur Ghar box on 4 March 2002.

Terrain: NASADEM (SRTM-derived). Sun: astral, at the DEM summit, local time = Afghanistan time (UTC+4:30).
Validated against the Landsat 7 scene of 5 Mar 2002 05:49:50 UTC (metadata sun az 141.5 / el 43.0 deg;
astral gives 142.8 / 43.4).

What this does and does NOT model: terrain only. No trees, snow depth, rocks or buildings, no atmosphere or
cloud, no night (the Razor 03 insertion was in the dark; this says nothing about night vision or the AC-130's
infrared sweep). The DEM is ~31 m north-south by ~26 m east-west and has SRTM error on steep slopes, so
anything smaller than a few cells (including the whole ~100 m summit complex) is below its resolution.

Usage: python3 sun_viewshed.py NASADEM_HGT_n33e069.tif   (needs overlay.json from build_overlay.py)
Writes sun.json, analysis.json, sun_shadow.png, viewshed.png
"""
import datetime as dt
import json
import sys
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from astral import Observer
from astral.sun import azimuth, elevation
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

BOX = (69.15, 33.30, 69.28, 33.40)
BIG = (69.05, 33.20, 69.38, 33.50)  # terrain context for shadows/sightlines that start inside the box
TZ = dt.timezone(dt.timedelta(hours=4, minutes=30))
DAY = dt.date(2002, 3, 4)

ov = json.load(open("overlay.json"))
SUM = ov["summit"]

with rasterio.open(sys.argv[1]) as src:
    wb = from_bounds(*BIG, transform=src.transform)
    zb = src.read(1, window=wb).astype("float32")
    tfb = src.window_transform(wb)
    cb = int(round((BOX[0] - tfb.c) / tfb.a)); rb = int(round((BOX[3] - tfb.f) / tfb.e))
H, W = zb.shape
m_lon = 111320 * np.cos(np.radians(33.35)); m_lat = 110574
dxm, dym = abs(tfb.a) * m_lon, abs(tfb.e) * m_lat
with rasterio.open(sys.argv[1]) as src:
    wbox = from_bounds(*BOX, transform=src.transform)
    z = src.read(1, window=wbox).astype("float32")
h, w = z.shape
R0, C0 = rb, cb   # box origin inside the big grid
rows, cols = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
BR, BC = rows + R0, cols + C0
# summit cell in the big grid
sr = int(round((SUM["model"][2] / (abs(tfb.e) * m_lat)))) + R0
sc = int(round(SUM["model"][0] / (abs(tfb.a) * m_lon))) + C0
print("summit cell elev:", zb[sr, sc], "box", h, w, "big", H, W)

# slope normals for self-shadowing
g_e = np.gradient(zb, dxm, axis=1)
g_n = -np.gradient(zb, dym, axis=0)
nrm = np.dstack([-g_e, -g_n, np.ones_like(zb)])
nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
slope = np.degrees(np.arctan(np.hypot(g_e, g_n)))
aspect = (np.degrees(np.arctan2(-g_e, -g_n)) + 360) % 360


def sunlit(az, el, max_km=12.0, step=30.0):
    """True where a box cell gets direct sun: faces the sun and no terrain blocks the ray."""
    a, e = np.radians(az), np.radians(el)
    sdir = np.array([np.sin(a) * np.cos(e), np.cos(a) * np.cos(e), np.sin(e)])
    facing = (nrm[BR, BC] @ sdir) > 0
    out = np.zeros(h * w, bool)
    r_f, c_f, h0 = BR.ravel(), BC.ravel(), zb[BR, BC].ravel()
    ds = np.arange(step, max_km * 1000, step)
    dr = -(ds * np.cos(a)) / dym   # north is -row
    dc = (ds * np.sin(a)) / dxm
    rise = ds * np.tan(e)
    CH = 12000
    for i in range(0, h * w, CH):
        sl = slice(i, i + CH)
        rr = np.rint(r_f[sl, None] + dr[None, :]).astype(int)
        cc = np.rint(c_f[sl, None] + dc[None, :]).astype(int)
        ok = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < W)
        t = zb[np.clip(rr, 0, H - 1), np.clip(cc, 0, W - 1)]
        blocked = ((t > h0[sl, None] + rise[None, :] + 3.0) & ok).any(axis=1)  # 3 m tolerance for DEM noise
        out[sl] = ~blocked
    return out.reshape(h, w) & facing.reshape(h, w)


obs = Observer(latitude=33.3429, longitude=69.2135, elevation=3172)
sun_tbl, times = [], []
t = dt.datetime.combine(DAY, dt.time(5, 30), tzinfo=TZ)
while t <= dt.datetime.combine(DAY, dt.time(18, 40), tzinfo=TZ):
    sun_tbl.append({"t": t.strftime("%H:%M"), "az": round(float(azimuth(obs, t)), 2), "el": round(float(elevation(obs, t)), 2)})
    t += dt.timedelta(minutes=10)
json.dump(sun_tbl, open("sun.json", "w"))

# Direct-sun duration (20 min samples while sun >= 3 deg above the horizon)
samples = [s for s in sun_tbl[::2] if s["el"] >= 3]
hours = np.zeros((h, w))
for s in samples:
    hours += sunlit(s["az"], s["el"]) * (20 / 60)

res = {"date": "2002-03-04", "tz": "UTC+4:30", "samples_20min": len(samples)}
cell = lambda r, c: (r, c)
rs, cs = sr - R0, sc - C0
res["summit_direct_sun_h"] = float(hours[rs, cs])
res["box_median_direct_sun_h"] = float(np.median(hours))
Xg = (cols + 0.5) * dxm; Zg = (rows + 0.5) * dym
dsum = np.hypot(Xg - Xg[rs, cs], Zg - Zg[rs, cs])
asp_box = aspect[BR, BC]; slope_box = slope[BR, BC]
steep = slope_box >= 20
near = (dsum <= 6000) & (z > 2400)
for name, lo, hi in (("NE", 22.5, 67.5), ("E", 67.5, 112.5), ("S", 157.5, 202.5), ("SW", 202.5, 247.5), ("W", 247.5, 292.5), ("N", 337.5, 22.5)):
    m = (asp_box >= lo) & (asp_box < hi) if lo < hi else ((asp_box >= lo) | (asp_box < hi))
    sel = m & steep & near
    res[f"steep_{name}_facing_median_sun_h"] = float(np.median(hours[sel])) if sel.any() else None
    res[f"steep_{name}_facing_cells"] = int(sel.sum())
band = np.abs(z - (3186 - 609.6)) <= 10
band &= dsum <= 6000
res["chalk2_elev_band_median_sun_h"] = float(np.median(hours[band]))
res["chalk2_elev_band_cells"] = int(band.sum())

# Snapshots for the figure
snap = {}
for label_t in ("08:00", "10:20", "14:00", "16:30"):
    s = next(x for x in sun_tbl if x["t"] == label_t)
    snap[label_t] = (s, sunlit(s["az"], s["el"]))
res["sunlit_fraction_at"] = {k: float(v[1].mean()) for k, v in snap.items()}
res["summit_sunlit_at"] = {k: bool(v[1][rs, cs]) for k, v in snap.items()}

# Viewshed: cells with a clear line of sight to/from a person at the summit (observer 2 m, target 1.7 m).
def viewshed(r0, c0, h_obs=2.0, h_tgt=1.7, n=240):
    vis = np.zeros(h * w, bool)
    zo = zb[r0, c0] + h_obs
    r_t, c_t = BR.ravel(), BC.ravel()
    t = np.linspace(0, 1, n + 1)[1:-1]
    CH = 8000
    for i in range(0, h * w, CH):
        sl = slice(i, i + CH)
        rr = np.rint(r0 + (r_t[sl, None] - r0) * t[None, :]).astype(int)
        cc = np.rint(c0 + (c_t[sl, None] - c0) * t[None, :]).astype(int)
        zt = zb[r_t[sl], c_t[sl]] + h_tgt
        line = zo + (zt[:, None] - zo) * t[None, :]
        vis[sl] = ~(zb[rr, cc] > line + 1.0).any(axis=1)
    return vis.reshape(h, w)

vis = viewshed(sr, sc)
# Sensitivity: the blockers near the summit are only a few metres high, inside SRTM's error, so check how much
# the answer moves with observer height.
sens = {}
for ho in (2.0, 6.0, 12.0):
    v = vis if ho == 2.0 else viewshed(sr, sc, h_obs=ho)
    sens[str(ho)] = {str(k): float(v[dsum <= k * 1000].mean()) for k in (1, 2, 4, 6)}
res["viewshed_sensitivity_by_observer_height_m"] = sens
res["viewshed_fraction_within_km"] = {str(k): float(vis[dsum <= k * 1000].mean()) for k in (1, 2, 4, 6)}
res["chalk2_elev_band_visible_from_summit"] = float(vis[band].mean())
valley = (z < 2650) & (dsum <= 6000)
res["valley_floor_(<2650m)_visible_from_summit"] = float(vis[valley].mean())
json.dump(res, open("analysis.json", "w"), indent=2)
print(json.dumps(res, indent=2))

# ---- figures
ls = LightSource(315, 40)
hill = ls.hillshade(z, vert_exag=2, dx=dxm, dy=dym)
ext = (BOX[0], BOX[2], BOX[1], BOX[3])
slon, slat = SUM["lon"], SUM["lat"]
fig, axs = plt.subplots(2, 3, figsize=(15, 9.4))
for ax, (k, (s, m)) in zip(axs.ravel(), snap.items()):
    ax.imshow(hill, cmap="gray", extent=ext, alpha=0.5)
    ax.imshow(np.where(m, np.nan, 1.0), cmap="Blues", vmin=0, vmax=2.2, extent=ext, alpha=0.75)
    ax.plot(slon, slat, "r^", ms=9)
    ax.set_title(f"{k} local: sun az {s['az']:.0f} deg, el {s['el']:.0f} deg\nshaded (blue) {100 * (1 - m.mean()):.0f}% of box")
    ax.set_xticks([]); ax.set_yticks([])
ax = axs[1, 1]
im = ax.imshow(hours, cmap="YlOrRd", extent=ext, vmin=0, vmax=hours.max())
ax.plot(slon, slat, "k^", ms=9); fig.colorbar(im, ax=ax, label="hours of direct sun", shrink=0.8)
ax.set_title("Direct sun, 4 Mar 2002 (terrain only)"); ax.set_xticks([]); ax.set_yticks([])
ax = axs[1, 2]; ax.axis("off")
txt = ("Summit direct sun: %.1f h\nBox median: %.1f h\n\nMedian hours, steep slopes >2400 m within 6 km:\n" % (res["summit_direct_sun_h"], res["box_median_direct_sun_h"]))
for name in ("NE", "E", "S", "SW", "W", "N"):
    v = res[f"steep_{name}_facing_median_sun_h"]
    txt += f"  {name}-facing: {v:.1f} h\n" if v is not None else f"  {name}-facing: n/a\n"
txt += "\nChalk 2 elevation band: %.1f h\n\nTerrain only. No snow, rocks, cloud or night." % res["chalk2_elev_band_median_sun_h"]
ax.text(0, 1, txt, va="top", family="monospace", fontsize=10)
fig.tight_layout(); fig.savefig("sun_shadow.png", dpi=110)

fig, ax = plt.subplots(figsize=(8, 7.4))
ax.imshow(hill, cmap="gray", extent=ext)
ax.imshow(np.where(vis, 1.0, np.nan), cmap="Greens", vmin=0, vmax=1.6, extent=ext, alpha=0.55)
ax.plot(slon, slat, "r^", ms=10)
bm = np.where(band, 1.0, np.nan)
ax.imshow(bm, cmap="autumn", vmin=0, vmax=1, extent=ext, alpha=0.9)
ax.set_title("Seen from the summit (green), 2 m observer, 1.7 m target\norange = Chalk 2 elevation band (~2,576 m)")
ax.set_xlabel("lon"); ax.set_ylabel("lat")
fig.savefig("viewshed.png", dpi=120, bbox_inches="tight")
