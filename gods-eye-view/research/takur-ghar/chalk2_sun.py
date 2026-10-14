"""Terrain sun/shadow at the Chalk 2 landing arc and the summit during the morning of 4 March 2002.

Times of the events come from the Army history (Folse 2022, pp. 60-62), printed as local clock times:
02:45 first MH-47 at the summit, 04:57 MAKO-30 lands again, ~05:20 Chapman fighting on alone, 06:05 Ranger MH-47
lands (Razor 01), Canon's 13 Rangers land "600 meters down the slope", peak cleared by 11:30, extraction after dark.
Sunrise at the summit 06:11, sunset 17:58 (UTC+4:30). Copeland et al. (2021) give the Chalk 2 climb as 2.5+ hours.

Terrain only (no snow, trees, cloud). Usage: python3 chalk2_sun.py NASADEM_HGT_n33e069.tif  (needs overlay.json, sun.json)
"""
import json
import sys
import numpy as np
import rasterio
from rasterio.windows import from_bounds

BIG = (69.05, 33.20, 69.38, 33.50)
BOX = (69.15, 33.30, 69.28, 33.40)
ov, sun = json.load(open("overlay.json")), json.load(open("sun.json"))
with rasterio.open(sys.argv[1]) as src:
    wb = from_bounds(*BIG, transform=src.transform)
    zb = src.read(1, window=wb).astype("float32")
    tf = src.window_transform(wb)
H, W = zb.shape
m_lon, m_lat = 111320 * np.cos(np.radians(33.35)), 110574
dxm, dym = abs(tf.a) * m_lon, abs(tf.e) * m_lat
rb, cb = int(round((BOX[3] - tf.f) / tf.e)), int(round((BOX[0] - tf.c) / tf.a))
sx, _, sz = ov["summit"]["model"]


def cell(x, zz):  # model x east, z south (metres from the box's NW corner) -> big-grid row/col
    return int(round(zz / dym)) + rb, int(round(x / dxm)) + cb


g_e = np.gradient(zb, dxm, axis=1); g_n = -np.gradient(zb, dym, axis=0)
nrm = np.dstack([-g_e, -g_n, np.ones_like(zb)]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)


def lit(r, c, az, el):
    a, e = np.radians(az), np.radians(el)
    s3 = np.array([np.sin(a) * np.cos(e), np.cos(a) * np.cos(e), np.sin(e)])
    if nrm[r, c] @ s3 <= 0:
        return False
    ds = np.arange(30.0, 12000.0, 30.0)
    rr = np.rint(r - ds * np.cos(a) / dym).astype(int); cc = np.rint(c + ds * np.sin(a) / dxm).astype(int)
    ok = (rr >= 0) & (rr < H) & (cc >= 0) & (cc < W)
    t = zb[np.clip(rr, 0, H - 1), np.clip(cc, 0, W - 1)]
    return not ((t > zb[r, c] + ds * np.tan(e) + 3.0) & ok).any()


pts = {"summit": cell(sx, sz)}
for b in (70, 90, 110, 130, 150):
    x = sx + 600 * np.sin(np.radians(b)); zz = sz - 600 * np.cos(np.radians(b))
    pts[f"arc {b} deg"] = cell(x, zz)
times = [t for t in sun if "06:00" <= t["t"] <= "09:30" and t["t"][-1] == "0" and int(t["t"][3:]) % 30 == 0] or []
times = [t for t in sun if t["t"] in ("06:00", "06:10", "06:20", "06:30", "07:00", "07:30", "08:00", "08:30", "09:00", "09:30")]
res = {}
print("terrain-only direct sun (1 = lit). Sunrise 06:11 at the summit.")
print(f"{'':12s}" + "".join(f"{t['t']:>7s}" for t in times))
print(f"{'sun el':12s}" + "".join(f"{t['el']:7.1f}" for t in times))
for name, (r, c) in pts.items():
    row = [int(lit(r, c, t["az"], t["el"])) if t["el"] > 0 else 0 for t in times]
    res[name] = dict(zip([t["t"] for t in times], row))
    print(f"{name:12s}" + "".join(f"{v:7d}" for v in row), f"  elev {zb[r, c]:.0f} m")
json.dump(res, open("chalk2_sun.json", "w"), indent=1)
