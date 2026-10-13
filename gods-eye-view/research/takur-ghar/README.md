# Takur Ghar 3D terrain (open-data build)

`takur_ghar_2002.glb` is a textured 3D model of the box 69.15-69.28 E, 33.30-33.40 N (about 12 x 11 km).
Open it in Blender, the three.js editor (https://threejs.org/editor/) or any glTF viewer. Units are metres, Y up,
north-up when viewed from above. Vertical exaggeration is x1.5.

| Layer | Source | Date | Resolution |
|---|---|---|---|
| Terrain | NASADEM (NASA reprocessing of SRTM), Planetary Computer `nasadem` | 20 Feb 2000 | ~31 m, no voids in this box |
| Texture | Landsat 7 ETM+ Collection 2 surface reflectance, LE07_L2SP_153037_20020913 | 13 Sep 2002 (0% cloud, snow-free) | 30 m |
| Texture fill (east edge) | LE07_L2SP_152037_20020922 | 22 Sep 2002 (0% cloud) | 30 m |

Both layers predate or sit near the 4 Mar 2002 battle, but neither shows it. There is no wreckage, no people and no
winter conditions in this model. The texture is a snow-free late-summer view of bare ground. Heights are approximate
(SRTM error grows on steep slopes); the local high point in the DEM is 3,172 m versus the published 3,186 m.

Rebuild: `./fetch_inputs.sh` then
`python3 build_scene.py NASADEM_HGT_n33e069.tif red.tif green.tif blue.tif --fill fill_red.tif fill_green.tif fill_blue.tif`
then `python3 render_preview.py takur_ghar_2002.glb preview`. Needs rasterio, numpy, trimesh, pillow, matplotlib.

Also here: `dem_check.py` (void/slope check), `REQUESTS.md` (imagery requests and leads).
