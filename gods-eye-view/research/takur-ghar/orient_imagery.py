"""Annotated orientation images of the Takur Ghar summit from Esri World Imagery (free to view).

Imagery: Esri World Imagery, source Vantor (formerly Maxar) "Vivid", captured 2021-06-09, 0.5 m resolution at the summit
(from Esri's own metadata service). Summer 2021, not March 2002, and an orthophoto (straight down, flat colours).
The tiles are fetched on the fly and NOT stored in this repository; Esri's terms apply (attribution: Esri, Vantor,
Earthstar Geographics, GIS user community). Use it for looking, not for redistribution.

Annotations (all schematic, see README): both candidate summit points, north arrow, scale bar, the directions from
Naylor 2005 / Copeland et al. 2021 and a search zone for the boulder bunker.
Usage: python3 orient_imagery.py OUTDIR
"""
import io, json, math, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

OSM = (33.3421431, 69.2137717)       # OpenStreetMap peak node (NGA names), 3,191 m
ov = json.load(open("overlay.json"))
DEM = (ov["summit"]["lat"], ov["summit"]["lon"])   # highest terrain cell, 3,172 m
HEAD = ov["headings"]
out = sys.argv[1]


def to_tile(z, lat, lon):
    n = 2 ** z
    return (lon + 180) / 360 * n, (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n


def mosaic(z, half, center):
    x, y = to_tile(z, *center); cx, cy = int(x), int(y)
    img = Image.new("RGB", ((2 * half + 1) * 256,) * 2)
    for dy in range(-half, half + 1):
        for dx in range(-half, half + 1):
            u = f"https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{cy + dy}/{cx + dx}"
            img.paste(Image.open(io.BytesIO(urllib.request.urlopen(u, timeout=40).read())).convert("RGB"),
                      ((dx + half) * 256, (dy + half) * 256))
    return img, (x - (cx - half)) * 256, (y - (cy - half)) * 256


def enhance(im):
    im = ImageOps.autocontrast(im, cutoff=1)
    return im.filter(ImageFilter.UnsharpMask(radius=3, percent=140, threshold=2))


def render(z, half, crop_r, name, rings, wedge_m):
    mpp = 156543.03392 * math.cos(math.radians(OSM[0])) / 2 ** z
    im, px, py = mosaic(z, half, OSM)
    im = enhance(im)
    x0, y0 = int(px - crop_r), int(py - crop_r)
    im = im.crop((x0, y0, x0 + 2 * crop_r, y0 + 2 * crop_r)).convert("RGBA")
    ox, oy = px - x0, py - y0                                  # OSM node in the crop
    # DEM summit offset in pixels
    dpx = (DEM[1] - OSM[1]) * 111320 * math.cos(math.radians(OSM[0])) / mpp
    dpy = -(DEM[0] - OSM[0]) * 110574 / mpp
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    font = ImageFont.load_default(size=19)
    T = lambda xy, t, fill: d.text(xy, t, fill=fill, font=font, stroke_width=3, stroke_fill=(0, 0, 0, 255))
    cx, cy = ox + dpx / 2, oy + dpy / 2                        # midpoint between the two candidates

    def at(b, dist, c=(cx, cy)):
        return c[0] + dist * math.sin(math.radians(b)) / mpp, c[1] - dist * math.cos(math.radians(b)) / mpp

    # search zone for the boulder bunker: NW of the LZ, close to the crest (my inference, see README)
    r_m = wedge_m
    d.ellipse([cx - r_m / mpp, cy - r_m / mpp, cx + r_m / mpp, cy + r_m / mpp], outline=(255, 235, 80, 255), width=2)
    T((cx - r_m / mpp + 4, cy - r_m / mpp - 20), f"search zone, {int(r_m)} m (summit complex)", (255, 235, 80, 255))
    for hd in HEAD:
        L = r_m * 1.0 if hd["id"] != "chalk2" else r_m * 1.0
        tip = at(hd["bearing"], L)
        col = tuple(int(hd["color"][i:i + 2], 16) for i in (1, 3, 5)) + (255,)
        a, b = ((tip, (cx, cy)) if hd.get("inbound") else ((cx, cy), tip))
        d.line([a, b], fill=col, width=3)
        T((tip[0] + 5, tip[1] - 8), f"{hd['label']} {hd['bearing']}°", col)
    for rr in rings:   # distance rings from the midpoint
        d.ellipse([cx - rr / mpp, cy - rr / mpp, cx + rr / mpp, cy + rr / mpp], outline=(255, 154, 48, 200), width=2)
        T((cx + rr / mpp * 0.71, cy + rr / mpp * 0.71), f"{rr} m", (255, 154, 48, 255))
    # candidates
    for (x, y), lab, col in (((ox, oy), "OSM peak 3,191 m", (255, 70, 70, 255)), ((ox + dpx, oy + dpy), "terrain high point 3,172 m", (70, 200, 255, 255))):
        d.ellipse([x - 6, y - 6, x + 6, y + 6], outline=col, width=3)
        T((x + 9, y + (6 if lab.startswith("OSM") else -22)), lab, col)
    # north arrow + scale bar + attribution
    W = im.size[0]
    d.line([(W - 40, 70), (W - 40, 30)], fill=(255, 255, 255, 255), width=4); d.polygon([(W - 40, 20), (W - 48, 36), (W - 32, 36)], fill=(255, 255, 255, 255))
    T((W - 46, 74), "N", (255, 255, 255, 255))
    bar_m = 50 if mpp < 0.7 else 200
    d.rectangle([20, im.size[1] - 40, 20 + bar_m / mpp, im.size[1] - 34], fill=(255, 255, 255, 255))
    T((20, im.size[1] - 60), f"{bar_m} m", (255, 255, 255, 255))
    d.rectangle([0, im.size[1] - 22, im.size[0], im.size[1]], fill=(0, 0, 0, 150))
    T((6, im.size[1] - 20), "Esri World Imagery, Vantor, 9 Jun 2021 (not 2002). Schematic.", (255, 255, 255, 255))
    Image.alpha_composite(im, lay).convert("RGB").save(f"{out}/{name}")
    print(name, f"{mpp:.2f} m/px, {im.size}")


render(18, 3, 380, "orient_close.png", rings=[50, 100], wedge_m=100)
render(17, 3, 700, "orient_context.png", rings=[300, 600], wedge_m=100)
