"""Try to register the user's top-down summit schematic (a slide with B1/B2, R1/R2, DSHK, trench, rocky outcropping,
Razor 01 symbol and a north arrow) onto Esri World Imagery, and test whether the match is better than chance.

The slide is the user's own and is NOT in this repository; pass its path. Everything it yields is a visual aid:
the schematic is not to scale and its scale is unknown (assumed from Copeland et al. 2021: the Rangers were ~60 m from the
bunkers). Esri tiles are fetched on the fly and not stored. The tree-by-tree null test below is the only check on the fit.

What it does
  1. Measures the north arrow on the slide (principal axis of the cyan arrow pixels): page-up is then a compass bearing.
  2. Builds a conifer-canopy mask from the June 2021 Esri/Vantor imagery (dark, green, locally darker than surroundings).
  3. For three assumed anchors, drops the slide's green "tree" blobs onto the imagery and reports the share of tree area
     that lands on canopy, against 2,000 random placements (same orientation and scale).
       A  Razor 01 symbol  = Predator HUD fix
       B  Rocky Outcropping = terrain high point
       C  Rocky Outcropping = the rock-band candidate 215 m north of the HUD fix
       D  Razor 01 symbol  = the "LZ - Razor 01" point in the user's own Takur_Ghar_Battlefield.kml
Usage: python3 schematic_register.py SLIDE.png
"""
import io
import math
import sys
import urllib.request
import numpy as np
from PIL import Image, ImageFilter

Z = 18
CENTER = (33.3436, 69.2125)
HUD = (33 + 20 / 60 + 34 / 3600, 69 + 12 / 60 + 43 / 3600)
DEM = (33.3429, 69.2135)
CAND = (33.34472, 69.21191)
KML_LZ = (33.342145, 69.214099)   # "LZ - Razor 01" in the user's Takur_Ghar_Battlefield.kml (placed from the same slide on SRTM, "tens of metres")
M_LAT = 110574.0
M_LON = 111320 * math.cos(math.radians(33.343))
# page pixels read by eye from the slide (+/-10 px): Razor 01 symbol and the Rocky Outcropping centre
RAZOR01, OUTCROP = (400, 228), (532, 402)
ANCHORS = {"A  Razor 01 symbol = HUD fix": (RAZOR01, HUD),
           "B  outcrop = terrain high point": (OUTCROP, DEM),
           "C  outcrop = candidate rock band": (OUTCROP, CAND),
           "D  Razor 01 symbol = user's KML LZ": (RAZOR01, KML_LZ)}


def tile_xy(lat, lon):
    n = 2 ** Z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def slide_masks(path):
    s = np.asarray(Image.open(path).convert("RGB")).astype(int)
    r, g, b = s[..., 0], s[..., 1], s[..., 2]
    green = (g > 130) & (r < 130) & (b < 110) & (g - r > 40)
    cyan = (b > 190) & (g > 150) & (r < 170) & (b - r > 60)
    ys, xs = np.nonzero(cyan[:120, 700:])           # the north arrow sits at the top right of the slide
    pts = np.column_stack([xs, ys]).astype(float)
    axis = np.linalg.svd(pts - pts.mean(0), full_matrices=False)[2][0]
    axis = axis if axis[0] > 0 else -axis             # arrow points right and up
    north_from_up = math.degrees(math.atan2(axis[0], -axis[1]))
    return green, north_from_up


def canopy_mask():
    half = 3
    tx, ty = tile_xy(*CENTER)
    cx, cy = int(tx), int(ty)
    mos = Image.new("RGB", ((2 * half + 1) * 256,) * 2)
    for dy in range(-half, half + 1):
        for dx in range(-half, half + 1):
            url = f"https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{Z}/{cy + dy}/{cx + dx}"
            mos.paste(Image.open(io.BytesIO(urllib.request.urlopen(url, timeout=40).read())).convert("RGB"), ((dx + half) * 256, (dy + half) * 256))
    a = np.asarray(mos).astype(float)
    bright = a.mean(2)
    exg = 2 * a[..., 1] - a[..., 0] - a[..., 2]
    local = np.asarray(mos.convert("L").filter(ImageFilter.BoxBlur(18))).astype(float)
    m = (bright < 75) & (exg > 22) & ((local - bright) > 15)
    eroded, opened = m.copy(), np.zeros_like(m)       # 3x3 opening removes single-pixel speckle
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            eroded &= np.roll(np.roll(m, dy, 0), dx, 1)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            opened |= np.roll(np.roll(eroded, dy, 0), dx, 1)
    return opened, (cx - half, cy - half)


def main(slide):
    green, north_from_up = slide_masks(slide)
    beta = (360 - north_from_up) % 360                   # compass bearing of page-up
    print(f"north arrow is {north_from_up:.1f} deg clockwise from page-up -> page-up = bearing {beta:.1f}, page-right = {(beta + 90) % 360:.1f}")
    canopy, (tx0, ty0) = canopy_mask()
    h, w = canopy.shape
    mpp = 156543.03392 * math.cos(math.radians(CENTER[0])) / 2 ** Z
    ys, xs = np.nonzero(green)
    ys, xs = ys[::2], xs[::2]
    print(f"tree pixels {len(xs)}, canopy base rate {canopy.mean():.3f}")

    def score(anchor_page, anchor_mos, s):
        b = math.radians(beta)
        up, right = -(ys - anchor_page[1]) * s, (xs - anchor_page[0]) * s
        e = up * math.sin(b) + right * math.cos(b)
        n = up * math.cos(b) - right * math.sin(b)
        col = np.rint(anchor_mos[0] + e / mpp).astype(int)
        row = np.rint(anchor_mos[1] - n / mpp).astype(int)
        ok = (row >= 0) & (row < h) & (col >= 0) & (col < w)
        return float(canopy[row[ok], col[ok]].mean()) if ok.mean() >= 0.98 else None

    rng = np.random.default_rng(1)
    for s in (0.285, 0.2):
        print(f"\nscale {s} m per page pixel")
        for name, (page, ll) in ANCHORS.items():
            tx, ty = tile_xy(*ll)
            obs = score(page, ((tx - tx0) * 256, (ty - ty0) * 256), s)
            null = []
            while len(null) < 2000:
                sc = score(page, (rng.uniform(250, w - 250), rng.uniform(250, h - 250)), s)
                if sc is not None:
                    null.append(sc)
            null = np.array(null)
            print(f"  {name:34s} on canopy {obs:.3f} | random median {np.median(null):.3f}, 95th {np.percentile(null, 95):.3f} | "
                  f"share of random placements >= observed {(null >= obs).mean():.3f}")


if __name__ == "__main__":
    main(sys.argv[1])
