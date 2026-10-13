"""Annotated orientation images of the Takur Ghar summit from Esri World Imagery (free to view).

Imagery: Esri World Imagery, source Vantor (formerly Maxar) "Vivid", captured 2021-06-09, 0.5 m resolution at the summit
(from Esri's own metadata service). Summer 2021, not March 2002, and an orthophoto (straight down, flat colours).
The tiles are fetched on the fly and NOT stored in this repository; Esri's terms apply (attribution: Esri, Vantor,
Earthstar Geographics, GIS user community). Use it for looking, not for redistribution.

Anchors drawn:
  * OSM peak node (33.3421431 N 69.2137717 E, 3,191 m) and the terrain high point (3,172 m, from overlay.json);
  * the Predator infrared frame of a Chinook at the LZ, 4 Mar 2002, whose HUD reads 33 20'34"N 69 12'43"E
    (sensor aim point, DMS to 1 arc-second, and 2002 Predator geolocation error is unknown: treat as +/-100 m);
  * from that LZ point: the directions read from Naylor 2005 / Copeland et al. 2021 (west-up sketch, my reading),
    and a wedge 50-100 m away at bearings 290-340 where the sketch puts the boulder bunker (my inference).
Usage: python3 orient_imagery.py OUTDIR
"""
import io, json, math, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

OSM = (33.3421431, 69.2137717)
HUD = (33 + 20 / 60 + 34 / 3600, 69 + 12 / 60 + 43 / 3600)
ov = json.load(open("overlay.json"))
DEM = (ov["summit"]["lat"], ov["summit"]["lon"])
HEAD = ov["headings"]
out = sys.argv[1]
M_LAT = 110574.0


def tile_xy(z, lat, lon):
    n = 2 ** z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def render(z, half, crop_r, name, scale_bar_m, upscale=1):
    cen = (HUD[0], HUD[1] + 60 / (111320 * math.cos(math.radians(HUD[0]))))   # LZ point shifted 60 m east so wedge and summit points both fit
    cx_t, cy_t = tile_xy(z, *cen); cx, cy = int(cx_t), int(cy_t)
    mos = Image.new("RGB", ((2 * half + 1) * 256,) * 2)
    for dy in range(-half, half + 1):
        for dx in range(-half, half + 1):
            u = f"https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{cy + dy}/{cx + dx}"
            mos.paste(Image.open(io.BytesIO(urllib.request.urlopen(u, timeout=40).read())).convert("RGB"), ((dx + half) * 256, (dy + half) * 256))
    mos = ImageOps.autocontrast(mos, cutoff=1).filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=2))
    mpp = 156543.03392 * math.cos(math.radians(cen[0])) / 2 ** z
    ox, oy = (cx_t - (cx - half)) * 256, (cy_t - (cy - half)) * 256          # centre point in the mosaic
    x0, y0 = int(ox - crop_r), int(oy - crop_r)
    im = mos.crop((x0, y0, x0 + 2 * crop_r, y0 + 2 * crop_r)).convert("RGBA")
    if upscale > 1:
        im = im.resize((im.size[0] * upscale, im.size[1] * upscale), Image.LANCZOS)
    k = upscale

    def pix(lat, lon):
        tx, ty = tile_xy(z, lat, lon)
        return ((tx - (cx - half)) * 256 - x0) * k, ((ty - (cy - half)) * 256 - y0) * k

    def step(p, bearing, metres):
        return p[0] + metres * math.sin(math.radians(bearing)) / mpp * k, p[1] - metres * math.cos(math.radians(bearing)) / mpp * k

    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    font = ImageFont.load_default(size=18 * (1 if k == 1 else 1))
    T = lambda xy, t, f: d.text(xy, t, fill=f, font=font, stroke_width=3, stroke_fill=(0, 0, 0, 255))
    lz = pix(*HUD)
    # boulder-bunker search wedge: 50-100 m from the LZ, bearings 290-340 (Naylor sketch: ~315, bunker ~50-100 m)
    arc_out = [step(lz, b, 100) for b in range(290, 341, 5)]; arc_in = [step(lz, b, 50) for b in range(340, 289, -5)]
    d.polygon(arc_out + arc_in, fill=(255, 235, 80, 70), outline=(255, 235, 80, 255))
    T((arc_out[0][0] - 150, arc_out[0][1] - 26), "boulder-bunker search zone", (255, 235, 80, 255))
    for hd in HEAD:
        tip = step(lz, hd["bearing"], 100 if hd["id"] != "chalk2" else 100)
        col = tuple(int(hd["color"][i:i + 2], 16) for i in (1, 3, 5)) + (255,)
        d.line([tip, lz] if hd.get("inbound") else [lz, tip], fill=col, width=3)
        T((tip[0] + 5, tip[1] - 9), f"{hd['label']} {hd['bearing']}°", col)
    for p, lab, col, dy in ((pix(*OSM), "OSM peak 3,191 m", (255, 90, 90, 255), 8), (pix(*DEM), "terrain high point 3,172 m", (80, 205, 255, 255), -26)):
        d.ellipse([p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7], outline=col, width=3); T((p[0] + 10, p[1] + dy), lab, col)
    d.ellipse([lz[0] - 8, lz[1] - 8, lz[0] + 8, lz[1] + 8], outline=(255, 255, 255, 255), width=3)
    d.line([lz[0] - 14, lz[1], lz[0] + 14, lz[1]], fill=(255, 255, 255, 255), width=2); d.line([lz[0], lz[1] - 14, lz[0], lz[1] + 14], fill=(255, 255, 255, 255), width=2)
    T((lz[0] + 12, lz[1] + 10), "Predator HUD point (LZ, 4 Mar 2002)", (255, 255, 255, 255))
    W, Hh = im.size
    d.line([(W - 40, 80), (W - 40, 40)], fill=(255, 255, 255, 255), width=4); d.polygon([(W - 40, 28), (W - 48, 44), (W - 32, 44)], fill=(255, 255, 255, 255)); T((W - 47, 84), "N", (255, 255, 255, 255))
    d.rectangle([20, Hh - 44, 20 + scale_bar_m / mpp * k, Hh - 38], fill=(255, 255, 255, 255)); T((20, Hh - 68), f"{scale_bar_m} m", (255, 255, 255, 255))
    d.rectangle([0, Hh - 26, W, Hh], fill=(0, 0, 0, 160)); T((6, Hh - 24), "Esri World Imagery, Vantor, 9 Jun 2021 (not 2002). Schematic.", (255, 255, 255, 255))
    Image.alpha_composite(im, lay).convert("RGB").save(f"{out}/{name}")
    print(name, f"{mpp / k:.2f} m/px", im.size)


render(18, 3, 400, "orient_close.png", 50, upscale=2)
