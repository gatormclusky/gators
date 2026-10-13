"""Derive overlay layers for the Takur Ghar model from the DEM and the published account.

Everything here is a *derived or schematic* position, not a surveyed one. Inputs and reasoning:

* Summit complex: the DEM's highest cell within 600 m of the published coordinate (the peak itself, 3,186 m
  in published accounts). Bunkers, landing zone (LZ) and Ranger fighting position all sit within ~60-100 m of
  it (Copeland et al. 2021, Fig. 3 and text) which is below this DEM's ~31 m cell size to resolve, so they are
  one marker.
* Chalk 2 landing elevation: the account says Chalk 2 landed "over 600 m below the summit" / "2,000 feet below
  the primary LZ" and then climbed "a northeast facing slope" for over two and a half hours (Copeland et al.
  2021, citing Macpherson 2005). That is a vertical drop (~610 m), i.e. an elevation of about 2,576 m. The only
  thing the sources fix is that elevation, so this layer is the ~2,576 m contour band (+/-10 m) within 6 km of
  the summit. The landing is somewhere along it; the sources do not say where.
  An attempt to also pick out a "candidate area" by requiring a steep northeast-facing slope that leads up to
  the summit left only 2 cells in the whole box (about 5.9 km out), and a version without the "leads up to the
  summit" test put most cells on the far side of the valley. Neither was defensible, so no area is claimed.
* Headings: bearings read from Naylor's sketch (via Battlecast) and Copeland et al. Fig. 3, see HEADINGS below.
* Razor 03 crash ring: the Army SOF history puts tail 476 about 6 km from Takur Ghar; the geographic analysis
  says Razor 03 made a controlled crash "away from the peak". Direction is not given in either source, so this
  is a 6 km ring around the summit (clipped to the box). Mapping Razor 03 to tail 476 is an inference.

Usage: python3 build_overlay.py NASADEM_HGT_n33e069.tif
Writes overlay.json and overlay_chalk2.png
"""
import json
import sys
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from PIL import Image

BOX = (69.15, 33.30, 69.28, 33.40)
PUB = (69.21, 33.34)
EXAG = 1.5

with rasterio.open(sys.argv[1]) as src:
    win = from_bounds(*BOX, transform=src.transform)
    z = src.read(1, window=win).astype("float32")
    tf = src.window_transform(win)
h, w = z.shape
m_lon = 111320 * np.cos(np.radians((BOX[1] + BOX[3]) / 2))
m_lat = 110574
cols, rows = np.meshgrid(np.arange(w), np.arange(h))
lon = tf.c + (cols + 0.5) * tf.a
lat = tf.f + (rows + 0.5) * tf.e
X = (lon - BOX[0]) * m_lon
Z = (BOX[3] - lat) * m_lat


def to_model(r, c):
    return [float(X[r, c]), float(z[r, c] * EXAG), float(Z[r, c])]


# Summit: highest cell within 600 m of the published coordinate.
px, pz = (PUB[0] - BOX[0]) * m_lon, (BOX[3] - PUB[1]) * m_lat
near = np.hypot(X - px, Z - pz) <= 600
r0, c0 = np.unravel_index(np.argmax(np.where(near, z, -np.inf)), z.shape)
summit = {"lat": float(lat[r0, c0]), "lon": float(lon[r0, c0]), "elev_m": float(z[r0, c0]), "model": to_model(r0, c0),
          "offset_from_published_coord_m": float(np.hypot(X[r0, c0] - px, Z[r0, c0] - pz))}
# Independent check: OpenStreetMap's peak node (imported from the NGA GNS database), Nominatim "Takur Ghar".
OSM = {"lat": 33.3421431, "lon": 69.2137717, "ele_m": 3191}
OSM["distance_from_dem_summit_m"] = float(np.hypot((OSM["lon"] - lon[r0, c0]) * m_lon, (OSM["lat"] - lat[r0, c0]) * m_lat))
summit["osm_peak"] = OSM
dist = np.hypot(X - X[r0, c0], Z - Z[r0, c0])
dx, dz = X[0, 1] - X[0, 0], Z[1, 0] - Z[0, 0]

# Chalk 2 landing elevation: ~610 m (2,000 ft) below the 3,186 m summit.
target = 3186 - 609.6
cand = (np.abs(z - target) <= 10) & (dist <= 6000) & (dist > 0)
print(f"summit {summit['elev_m']:.0f} m at {summit['lat']:.4f}N {summit['lon']:.4f}E; "
      f"{summit['offset_from_published_coord_m']:.0f} m from the rounded 33.34N 69.21E, "
      f"{summit['osm_peak']['distance_from_dem_summit_m']:.0f} m from the OSM peak node")
print(f"{target:.0f} m contour band cells: {cand.sum()}; dist to summit min/median/max "
      f"{dist[cand].min():.0f}/{np.median(dist[cand]):.0f}/{dist[cand].max():.0f} m")

img = np.zeros((h, w, 4), "uint8")
img[cand] = (255, 150, 40, 215)
Image.fromarray(img).save("overlay_chalk2.png")

# Razor 03 crash ring: 6 km around the summit, sampled on the terrain, clipped to the box.
ring = []
for ang in np.linspace(0, 2 * np.pi, 361):
    x = X[r0, c0] + 6000 * np.sin(ang)
    zz = Z[r0, c0] - 6000 * np.cos(ang)
    c = int(round((x - X[0, 0]) / dx))
    r = int(round((zz - Z[0, 0]) / dz))
    if 0 <= r < h and 0 <= c < w:
        ring.append([float(x), float(z[r, c] * EXAG + 20), float(zz)])
    else:
        ring.append(None)

# Label anchor: the band cell nearest the band's median position.
rr, cc = np.nonzero(cand)
k = np.argmin((rr - np.median(rr)) ** 2 + (cc - np.median(cc)) ** 2)
label_model = to_model(rr[k], cc[k])

# Directions from the Rangers' position / LZ (all within ~100 m of the summit marker). Bearings are true compass
# bearings read from two schematic figures, so +/- 25 deg at best, and distances are NOT to scale:
#  * Naylor 2005, "Razor 01 assault on Al Qaida bunker atop Takur Ghar", as reproduced on thebattlecast.com
#    (Battlecast, 2024). Its compass arrow is labelled "W" and points up, i.e. WEST IS UP on that sketch, which I
#    read as: map-right = north, map-down = east, map-left = south.
#  * Copeland et al. 2021, Fig. 3 (oblique view; its compass puts north toward the upper right, i.e. looking NW).
# The two agree on the bunkers (NW of the LZ) and on Chalk 2 arriving from the east.
HEADINGS = [
    {"id": "bunkers", "label": "Bunkers + DShK", "bearing": 315, "color": "#ff5555",
     "note": "Enemy bunker system (boulder, 'bonsai' tree, DShK) lies north-west of the Rangers' position. Both figures agree."},
    {"id": "cliff", "label": "Cliff", "bearing": 30, "color": "#9ad0ff",
     "note": "Vertical cliff on the Rangers' right, to the north-east (Self 2008 via Copeland; the Naylor sketch draws it along the north edge)."},
    {"id": "rocky_hill", "label": "Rocky hill", "bearing": 66, "color": "#c8a0ff",
     "note": "On the Naylor sketch Chalk 2's path ends at a rocky hill east-north-east of the Rangers' position; Roberts' helmet is marked there."},
    {"id": "chalk2", "label": "Chalk 2 inbound", "bearing": 110, "color": "#ffb060", "inbound": True,
     "note": "Chalk 2 (Canon) came up from the east/south-east and swung round to the rocky hill. Direction only; the sketch is not to scale."},
    {"id": "razor01", "label": "Razor 01 wreck", "bearing": 206, "color": "#cccccc",
     "note": "The crashed Chinook lies south-south-west of the Rangers' position (about 15 m on the sketch)."},
    {"id": "mako30", "label": "MAKO 30 site 2", "bearing": 256, "color": "#c8e08a",
     "note": "Marked on the sketch west-south-west of the Rangers' position."},
]

out = {
    "summit": summit,
    "headings": HEADINGS,
    "chalk2": {"texture": "overlay_chalk2.png", "cells": int(cand.sum()), "elev_m": float(target), "label_model": label_model,
               "criteria": "elevation 2576 +/- 10 m (610 m below the 3,186 m summit), within 6 km of the summit"},
    "ring6km": ring,
}
json.dump(out, open("overlay.json", "w"))
