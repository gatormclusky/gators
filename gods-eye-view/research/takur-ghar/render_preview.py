"""Render oblique previews of the GLB from the south-west and the north (matplotlib, no GPU needed)."""
import sys
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource

glb, out_prefix = sys.argv[1], sys.argv[2]
mesh = list(trimesh.load(glb).geometry.values())[0]
tex = np.asarray(mesh.visual.material.baseColorTexture.convert("RGB")) / 255.0
h, w = tex.shape[:2]
V = mesh.vertices.reshape(h, w, 3)
x, y, z = V[..., 0], V[..., 1], V[..., 2]
# shade the texture with the geometry so relief reads (Landsat sun is high)
shade = LightSource(315, 40).hillshade(y, vert_exag=1, dx=30, dy=30)[..., None]
col = np.dstack([np.clip(tex * (0.55 + 0.7 * shade), 0, 1), np.ones((h, w))])
for name, elev, azim in (("sw", 30, -60), ("north", 32, 90)):
    fig = plt.figure(figsize=(10, 6.5))
    ax = fig.add_subplot(111, projection="3d")
    s = 2
    ax.plot_surface(x[::s, ::s], z[::s, ::s], y[::s, ::s], facecolors=col[::s, ::s], rstride=1, cstride=1,
                    linewidth=0, antialiased=False, shade=False)
    ax.set_box_aspect((np.ptp(x), np.ptp(z), np.ptp(y)))
    ax.view_init(elev, azim); ax.invert_yaxis(); ax.set_axis_off()
    fig.savefig(f"{out_prefix}_{name}.png", dpi=110, bbox_inches="tight", facecolor="white")
