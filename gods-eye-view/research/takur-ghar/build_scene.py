"""Build a textured 3D terrain (GLB) of the Takur Ghar box.

Terrain: NASADEM (SRTM-derived, Feb 2000), ~30 m.
Texture: Landsat 7 ETM+ Collection 2 surface reflectance, 13 Sep 2002 (snow-free), 30 m.

Usage:
  python3 build_scene.py NASADEM_HGT_n33e069.tif red.tif green.tif blue.tif \\
      [--fill fill_red.tif fill_green.tif fill_blue.tif] [--exag 1.5] [--out takur_ghar_2002.glb]
Inputs are Planetary Computer assets (`nasadem`, and `landsat-c2-l2` items
LE07_L2SP_153037_20020913_02_T1 plus LE07_L2SP_152037_20020922_02_T1 as --fill for the
east edge the first scene doesn't cover); see fetch_inputs.sh.
Outputs: GLB (Y up, metres), texture PNG, and preview renders.
"""
import argparse
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.windows import from_bounds
from PIL import Image
import trimesh

BOX = (69.15, 33.30, 69.28, 33.40)  # W, S, E, N
PEAK = (69.21, 33.34)

ap = argparse.ArgumentParser()
ap.add_argument("dem"); ap.add_argument("red"); ap.add_argument("green"); ap.add_argument("blue")
ap.add_argument("--fill", nargs=3, metavar=("R", "G", "B"), help="second scene used where the first has no data")
ap.add_argument("--exag", type=float, default=1.5, help="vertical exaggeration")
ap.add_argument("--out", default="takur_ghar_2002.glb")
a = ap.parse_args()

with rasterio.open(a.dem) as src:
    win = from_bounds(*BOX, transform=src.transform)
    z = src.read(1, window=win).astype("float32")
    tf = src.window_transform(win)
    crs = src.crs
    z[z == src.nodata] = np.nan
h, w = z.shape

# Resample each Landsat band onto the DEM grid (surface reflectance = DN*0.0000275 - 0.2).
VALID_MIN = 7273  # Landsat C2 L2 surface-reflectance valid DN range starts here; below it is edge/fill noise

def resample(path):
    with rasterio.open(path) as s:
        dst = np.zeros((h, w), "float32")
        reproject(rasterio.band(s, 1), dst, dst_transform=tf, dst_crs=crs,
                  resampling=Resampling.bilinear, src_nodata=0, dst_nodata=0)
    return dst

bands = [resample(p) for p in (a.red, a.green, a.blue)]
if a.fill:
    for b, p in zip(bands, a.fill):
        gap = b < VALID_MIN
        b[gap] = resample(p)[gap]
print(f"texture coverage: {100 * (bands[0] >= VALID_MIN).mean():.1f}%")
rgb = np.dstack([np.clip(b * 0.0000275 - 0.2, 0, 1) * (b >= VALID_MIN) for b in bands])
lo, hi = np.percentile(rgb[rgb > 0], (2, 98))  # stretch over valid pixels only
tex = np.clip((rgb - lo) / (hi - lo), 0, 1) ** (1 / 1.2)
Image.fromarray((tex * 255).astype("uint8")).save(a.out.replace(".glb", "_texture.png"))

# Mesh in metres: x east, y up, z south (so it reads as north-up from above).
lat0 = np.radians((BOX[1] + BOX[3]) / 2)
m_lon, m_lat = 111320 * np.cos(lat0), 110574
cols, rows = np.meshgrid(np.arange(w), np.arange(h))
lon = tf.c + (cols + 0.5) * tf.a
lat = tf.f + (rows + 0.5) * tf.e
x = (lon - BOX[0]) * m_lon
zs = (lat - BOX[3]) * m_lat * -1.0
y = np.nan_to_num(z, nan=np.nanmin(z)) * a.exag
verts = np.column_stack([x.ravel(), y.ravel(), zs.ravel()])
uv = np.column_stack([(cols.ravel() + 0.5) / w, 1 - (rows.ravel() + 0.5) / h])
idx = np.arange(h * w).reshape(h, w)
tl, tr, bl, br = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, :-1].ravel(), idx[1:, 1:].ravel()
faces = np.vstack([np.column_stack([tl, bl, tr]), np.column_stack([tr, bl, br])])

img = Image.open(a.out.replace(".glb", "_texture.png"))
mat = trimesh.visual.material.PBRMaterial(baseColorTexture=img, metallicFactor=0.0, roughnessFactor=1.0)
mesh = trimesh.Trimesh(verts, faces, visual=trimesh.visual.TextureVisuals(uv=uv, material=mat), process=False)
# Normals straight from the height grid (fast, and the GLB then carries NORMAL so viewers can light it).
dy_dx = np.gradient(y, abs(tf.a) * m_lon, axis=1)
dy_dz = np.gradient(y, abs(tf.e) * m_lat, axis=0)  # rows run south, same as +z
nrm = np.dstack([-dy_dx, np.ones_like(y), -dy_dz])
nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
mesh.vertex_normals = nrm.reshape(-1, 3)
mesh.export(a.out)
print(f"{a.out}: {len(verts)} vertices, {len(faces)} faces, exaggeration x{a.exag}")
