# Takur Ghar 3D terrain (open-data build)

`takur_ghar_2002.glb` is a textured 3D model of the box 69.15-69.28 E, 33.30-33.40 N (about 12 x 11 km).
Open it in Blender, the three.js editor (https://threejs.org/editor/) or any glTF viewer. Units are metres, Y up,
north-up when viewed from above. Vertical exaggeration is x1.5.

| Layer | Source | Date | Resolution |
|---|---|---|---|
| Terrain | NASADEM (NASA reprocessing of SRTM), Planetary Computer `nasadem` | 20 Feb 2000 | ~31 m, no voids in this box |
| Texture | Landsat 7 ETM+ Collection 2 surface reflectance, LE07_L2SP_153037_20020913 | 13 Sep 2002 (0% cloud, snow-free) | 30 m |
| Texture fill (east edge) | LE07_L2SP_152037_20020922 | 22 Sep 2002 (0% cloud) | 30 m |
| **March texture** | LE07_L2SP_153037_20020305 (day after the battle, 5% scene cloud) | 5 Mar 2002 | 30 m |
| March fill (east edge) | LE07_L2SP_152037_20020314 (2% scene cloud) | 14 Mar 2002 | 30 m |

The March texture shows snow on the high ground and bare, dark valley floor. The east strip comes from the 14 Mar
pass, so seams and slightly different snow cover are possible there. (The 6 Mar Landsat 5 scene was tried for the fill
but has dark banding in the box's east, so it isn't used.)

Neither texture shows the battle itself. There is no wreckage, no people and no
winter conditions in this model. The texture is a snow-free late-summer view of bare ground. Heights are approximate
(SRTM error grows on steep slopes); the local high point in the DEM is 3,172 m versus the published 3,186 m.

## Viewer (switch between the two textures)

`viewer.html` loads the GLB with a button to swap the September and March textures, top/oblique camera buttons, a
vertical-exaggeration slider and the event overlay below. It needs a local web server and internet (three.js from a CDN):

    cd gods-eye-view/research/takur-ghar && python3 -m http.server 8000   # then open http://localhost:8000/viewer.html

Screenshots: `overlay_obl.png` (September, oblique), `overlay_top_mar.png` (March, top-down).

## Event overlay (`build_overlay.py` -> `overlay.json`, `overlay_chalk2.png`)

Three layers, each with its derivation shown in the viewer. None is a surveyed position.

| Layer | What it is | Basis |
|---|---|---|
| Summit complex | Highest DEM cell within 600 m of the usual coordinate (3,172 m at 33.3429 N 69.2135 E, about 456 m from that coordinate) | Copeland et al. 2021: bunkers, DShK, LZ (~60 m from the bunkers) and Ranger fighting position all on the summit; too close together for a 31 m DEM, so one marker |
| Chalk 2 landing elevation | The ~2,576 m contour band (+/-10 m) within 6 km of the summit | "Over 600 m / 2,000 ft below" the summit (Copeland et al., citing Macpherson 2005). The elevation is all the sources fix |
| Razor 03 crash ring | 6 km circle around the summit | Army SOF history puts tail 476 about 6 km from Takur Ghar; Razor 03 "crashed away from the peak". No direction given; treating 476 as Razor 03 is an inference |

Known problems:

* Everything at the Chalk 2 elevation in this model lies on the western valley side, but the paper's Figure 3 draws the
  Chalk 2 approach from the east. I could not reconcile them (the published summit height/coordinate, or "over 600 m",
  may be loose). A search for steep northeast-facing slopes leading up to the summit found 2 cells in the whole box, so
  no landing patch is claimed. An earlier version without the "leads up to the summit" test was misleading and was dropped.
* Not placed: the Razor 03 crash site, the "mosque" landmark in Figure 3, the Predator's orbit, and any clock times
  (the sources give a sequence, not times, apart from "night of 3-4 March", the 17-hour duration and sunset exfiltration).
* The summit marker is the DEM high point. Published coordinates differ in the 4th decimal and the DEM is 14 m below the
  published 3,186 m, so treat positions as good to a few hundred metres at best.

Rebuild: `./fetch_inputs.sh` then
`python3 build_scene.py NASADEM_HGT_n33e069.tif red.tif green.tif blue.tif --fill fill_red.tif fill_green.tif fill_blue.tif`
then `python3 render_preview.py takur_ghar_2002.glb preview`. For March run `./fetch_inputs.sh mar` and build with the
`mar_*` files and `--out takur_ghar_2002_mar.glb` (the viewer reuses the September mesh and only swaps the texture PNG). Needs rasterio, numpy, trimesh, pillow, matplotlib.

Also here: `dem_check.py` (void/slope check), `REQUESTS.md` (imagery requests and leads).
