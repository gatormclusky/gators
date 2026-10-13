# Takur Ghar 3D terrain (open-data build)

`takur_ghar_2002.glb` is a textured 3D model of the box 69.15-69.28 E, 33.30-33.40 N (about 12 x 11 km).
Open it in Blender, the three.js editor (https://threejs.org/editor/) or any glTF viewer. Units are metres, Y up,
north-up when viewed from above. Vertical exaggeration is x1.5.

| Layer | Source | Date | Resolution |
|---|---|---|---|
| Terrain | NASADEM (NASA reprocessing of SRTM), Planetary Computer `nasadem` | 20 Feb 2000 | ~31 m N-S x ~26 m E-W, no voids in this box |
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
| Summit complex | Highest terrain cell near the usual coordinate: 3,172 m at 33.3429 N 69.2135 E | Copeland et al. 2021: bunkers, DShK, LZ (~60 m from the bunkers) and Ranger fighting position all on the summit; too close together for a 31 m DEM, so one marker. **Location check:** OpenStreetMap's peak node for Takur Ghar (from the NGA names database, 33.3421 N 69.2138 E, 3,191 m) is 90 m from this cell. The rounded 33.34 N 69.21 E that I used first is 456 m away and would have been wrong. |
| Headings | Six direction arrows from the summit marker (bunkers NW ~315 deg, cliff NE ~30, rocky hill ENE ~66, Chalk 2 inbound from ~110 deg, Razor 01 wreck SSW ~206, MAKO 30 second site WSW ~256) | Read from Naylor 2005, "Razor 01 assault on Al Qaida bunker atop Takur Ghar" (as reproduced on thebattlecast.com) and Copeland et al. Fig. 3. Direction only (about +/-25 deg), lengths mean nothing. **My reading of the Naylor sketch: its compass arrow is labelled "W" and points up, so west is up.** Copeland's figure independently agrees on the bunkers (NW) and Chalk 2 (from the east). Please check against the book. |
| Chalk 2 landing arc | A line 600 m from the summit marker across bearings 70-150 deg (ground there is 65-250 m lower than the summit) | **Distance:** the Army history (Folse 2022, p. 62): a second MH-47 landed 13 Rangers under S. Sgt. Canon "600 meters down the slope". **Direction:** both schematics put Chalk 2's approach to the east/south-east. An arc of possibilities, not a location. |
| Razor 03 crash ring | 6 km circle around the summit | Army SOF history puts tail 476 about 6 km from Takur Ghar; Razor 03 "crashed away from the peak". No direction given; treating 476 as Razor 03 is an inference |

Known problems:

* **Correction (Chalk 2).** I first read Copeland et al.'s "over 600 meters below the summit / 2,000 feet below" as a
  610 m drop in height and drew the 2,576 m contour band. No ground within 8 km east or south-east of the summit is
  that low (it is 2,800-3,300 m there), so that reading could not match the schematics. The Army history says "600
  meters down the slope", a distance along the slope, which fits, so the band was removed and replaced by the arc.
  The Rangers' climb took 2.5+ hours against a 45-minute estimate, so the landing is probably not simply 600 m in a
  straight line; treat the arc as the least the sources support.
* Not placed: the Razor 03 crash site, the "mosque" landmark in Figure 3, the Predator's orbit, and any clock times
  (the sources give a sequence, not times, apart from "night of 3-4 March", the 17-hour duration and sunset exfiltration).
* The summit marker is the terrain high point, 14-19 m below the published 3,186 m / OSM 3,191 m (SRTM error). The Naylor
  sketch is a schematic from a book as reproduced on a blog, and its orientation is my reading.

Rebuild: `./fetch_inputs.sh` then
`python3 build_scene.py NASADEM_HGT_n33e069.tif red.tif green.tif blue.tif --fill fill_red.tif fill_green.tif fill_blue.tif`
then `python3 render_preview.py takur_ghar_2002.glb preview`. For March run `./fetch_inputs.sh mar` and build with the
`mar_*` files and `--out takur_ghar_2002_mar.glb` (the viewer reuses the September mesh and only swaps the texture PNG). Needs rasterio, numpy, trimesh, pillow, matplotlib.

Also here: `dem_check.py` (void/slope check), `REQUESTS.md` (imagery requests and leads).

## Sun and shadow, 4 March 2002 (`sun_viewshed.py` -> `analysis.json`, `sun_shadow.png`, `sun.json`)

Terrain only. The sun model (astral, at the summit, Afghanistan time UTC+4:30) matches the Landsat 7 pass of 5 Mar
2002 05:49:50 UTC (metadata az 141.5 / el 43.0 deg; computed 142.8 / 43.4). The sun is at the geometric horizon
at about 06:20 and 17:51 (civil twilight 05:54 to 18:18). (astral's own "sunrise 06:11 / sunset 17:58" includes the
horizon dip for an observer on open ground at 3,172 m, which does not apply among mountains; I quoted it earlier and
it was wrong for this purpose.)

| | |
|---|---|
| Direct sun at the summit | 11.0 h of the day (terrain shadows and slope only) |
| Share of the box in terrain shadow | 24% at 08:00, 1% at 10:20, 1% at 14:00, 20% at 16:30 |
| Median direct-sun hours, steep slopes above 2,400 m within 6 km | NE-facing 8.0, E 8.7, N 8.7, W 9.0, SW 9.7, S 10.0 |

So in early March a north-east-facing slope loses only about two hours of sun against a south-facing one: the sun is
high enough that most of the difference is in the first and last hours.

Not modelled: snow, rock, trees, cloud, atmosphere, and night. The Razor 03 insertion happened in the dark, so none of
this speaks to that or to the AC-130's infrared sweep. The viewer's "Show sun and cast shadows" slider casts real-time
shadows from the same sun table; use "Grey terrain" because the Landsat textures carry their own baked shading
(`sun_0800_grey_terrain.png` shows 08:00).

**Viewshed: not reliable, not shown.** The script also computes what a person at the summit could see. The result
swings with an assumed observer height: ground within 2 km counted as visible is 3% at 2 m, 15% at 6 m and 34% at 12
m, because the blocking terrain near the summit is only a few metres high, inside SRTM's error. A bilinear
re-check agreed with the code, so this is a data limit, not a bug. I did not commit `viewshed.png` for that reason.

### The Army's clock times against the sun (`chalk2_sun.py` -> `chalk2_sun.json`)

Times from the Army history (Folse 2022, pp. 60-62), which prints no time zone; I assumed local (UTC+4:30):

| Time | Event | Sun elevation at the summit |
|---|---|---|
| 02:45 | First MH-47 (Razor 03, MAKO 30) at the summit; RPG; Roberts falls | -44 deg (full darkness) |
| 04:57 | MAKO 30 lands again; Chapman charges the bunker | -18 deg |
| ~05:20 | Drone shows Chapman fighting on, about 45 min | -13 deg |
| 06:05 | Ranger MH-47 (Razor 01) lands and crash-lands; Chalk 2 lands 600 m down the slope | -3.5 deg (civil twilight) |
| 11:30 | Peak cleared | +49 deg |

Terrain-only direct sun: the summit is lit from about 07:00; points on the 600 m arc between bearings 90 and 150 deg from
about 07:00, and at 70 deg only from about 08:30. So the Rangers began their climb before sunrise and were in
terrain shade or low sun for roughly the first hour.

## Orientation imagery (`orient_imagery.py`)

Best free imagery: **Esri World Imagery** (free to view in a browser or Google Earth-style apps). Esri's metadata service
reports Vantor (ex-Maxar) "Vivid" imagery over the summit captured 9 June 2021 at 0.5 m resolution. It is summer,
nearly 20 years after the battle, an orthophoto (looking straight down), and low in contrast. `orient_imagery.py` fetches
it on the fly and draws north, a scale bar, the OSM and terrain summit points, the headings and a 100 m "summit complex"
search zone. The imagery is not stored in this repository (Esri's terms apply).

The boulder bunker is not identifiable in it by me. The sourced clues for finding it: the bunkers and DShK sit at the
top, north-west of the Rangers' bowl-shaped landing zone (about 60 m away), with a vertical cliff on the north-east edge
and a lone "bonsai" tree beside the boulder (Naylor sketch). Look within about 100 m of the two summit points.
