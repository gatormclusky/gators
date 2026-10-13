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
| LZ fix + headings | A white ring (100 m) at the Predator HUD point, with six direction arrows from it (bunkers NW ~315 deg, cliff NE ~30, rocky hill ENE ~66, Chalk 2 inbound from ~110 deg, Razor 01 wreck SSW ~206, MAKO 30 second site WSW ~256) | Read from Naylor 2005 "Razor 01 assault" sketch (as reproduced on thebattlecast.com) and Copeland et al. Fig. 3, drawn from the LZ fix below. Direction only (about +/-25 deg), lengths mean nothing. **My reading of the Naylor sketch: its compass arrow is labelled "W" and points up, so west is up.** Copeland's figure independently agrees on the bunkers (NW) and Chalk 2 (from the east). Please check against the book. |
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

## Predator HUD fix (from a frame supplied by the user)

An infrared frame from the Predator feed shows an MH-47 with rotors turning on a snowy slope with a lone pine at the left
and footpaths in the snow, with a HUD reading **33°20'34"N 69°12'43"E**, **232.79°**, **1.93 nm**, **252 m** and a clock
of **01:47:41** (no time zone). I read the coordinate as the sensor's aim point (frame centre, where the helicopter is);
the other numbers I do not know the meaning of (232.79 could be the camera's look direction, 1.93 nm the slant range).

* 33.34278 N 69.21194 E, rounded to 1 arc-second (about 31 m north-south, 26 m east-west), and 2002 Predator
  geolocation error is unknown, so I treat it as **+/-100 m**.
* It is **143 m west** of the terrain high point (bearing 264 deg), **184 m west-north-west** of OpenStreetMap's peak
  (bearing 292 deg), and the terrain there is **3,111 m, about 60 m below** the high point. The sources put the LZ "on the
  summit", so either the fix is off by more than 100 m, or the fight was on a bench below and west of the high point.
* If the clock is Zulu, 01:47:41 is 06:17 local, which is close to the Army's 06:05 landing of the Ranger helicopters
  (Razor 01; Chalk 2 landed elsewhere). That is a guess; the frame shows an intact aircraft unloading, and small dark
  (hot) figures under the tail.
* Using it as the anchor, the boulder bunker (north-west of the Rangers' position, 50-100 m on the Naylor sketch) falls
  near 33.3431-33.3434 N 69.2112-69.2116 E. The wedge in `orient_imagery.py`'s output covers 50-100 m at bearings
  290-340 from the fix. In the Esri imagery that wedge holds a cluster of conifers, consistent with bunkers "under the
  cover of foliage" (Copeland et al.), but I cannot see a bunker or boulder in 0.5 m summer imagery.

Other images supplied (no sources given, so provenance is unverified): burned helicopter wreckage beside a lone conifer on
a bare crest; wreckage in a hollow beside a stone-lined pit with snow peaks behind; and a DShK on a tripod in a rock and
sandbag emplacement above a snowy slope of conifers. They are ground-level references for what to look for, not
geolocated.

## Ridge photo, DoD Predator reel and a candidate for "the boulder"

Added after the user supplied a long-range ridge photograph (a Chinook wreck on a crest among conifers, a snow strip along
the crest, and a prominent rock outcrop where the crest descends to the right) and pointed to their Drive notes. Source
and date of that photo are unverified; the user's Drive ledger says *Weapon of Choice* fig. 16 (p. 310) is a colour ridge
photograph with a prominent outcrop, which may be the same picture. I could not download the book here to check.

### What the DoD reel is (DVIDS video 618151)

"Air Force Tech. Sgt. John Chapman - ISR Feed Highlights, Takur Ghar, Afghanistan, March 4, 2002" is a public-domain, 90 second
annotated edit of the Predator infrared feed (https://www.dvidshub.net/video/618151). The coordinate overlay was cropped out,
so it gives no new fixes. It does give DoD's own captions, "Local Time" stamps, and bunker labels **B1** and **B2** over a
dark tree clump (frames at 04:28). Frames at 04:27 (Razor 04 inserting the team) and 05:44 (Razor 01) show a Chinook, seen
from above with rotors turning and small dark (hot) figures leaving its tail, like the frame the user supplied.

| Reel "Local Time" | Reel caption | Army history (Folse 2022) |
|---|---|---|
| 04:27 | Razor 04 inserts the team to recover Roberts | MAKO-30 lands 04:57 |
| 04:28-04:31 | Chapman runs up the slope, charges a bunker, moves on a second machine gun | (same phase) |
| 05:41 | Chapman "regains his faculties and continues to fight" | recovered ~05:20, fought ~45 min |
| 05:43-05:44 | Razor 01 incoming, RPGs; Chapman killed | Razor 01 lands 06:05 |

**Correction.** I first wrote that there was no constant offset between the reel and the other sources. That was wrong once
the user's own slide is used as a reference: its panel "QRF INFIL/SHOOTDOWN IN RZR 01 - 6:14am" is exactly 30 minutes after the
reel's 05:44 for Razor 01, and the Army's MAKO-30 landing (04:57) is exactly 30 minutes after the reel's 04:27. So the reel's
"Local Time" is UTC+4 and the slide and Army history are UTC+4:30. Two sources still disagree with each other: the Army's
history puts Razor 01's landing at 06:05 against the slide's 06:14.

### The user's HUD frame, timed

Its clock, 01:47:41, is almost certainly Zulu. That is 06:17:41 on the slide's UTC+4:30 clock (3.7 minutes after the slide's
Razor 01 shootdown at 06:14) and 05:47:41 on the reel's UTC+4 clock (3.7 minutes after the reel's Razor 01 frames at 05:44). The
frame shows a Chinook on the ground with rotors still turning and figures at its tail, like the reel's Razor 01 frames. So the
frame is very probably Razor 01 at the LZ, a few minutes after it went down. Still an inference, not a proof.

### DoD's own words on the summit

American Forces Press Service (reproduced at https://www.dvidshub.net/news/printable/527277), on the 24 May 2002 briefing:
"There are sheer drops on the west and east sides of the crown of the ridge and only one place to off-load a helicopter";
"three feet of snow and tree foliage covered two well-fortified enemy bunkers"; "A green command and control tent was hidden
in a crevice between the rocks." The briefing transcript itself (globalsecurity.org mil-020524-dod01) could not be fetched
from here (HTTP 402). The user's Drive ledger quotes it as putting "two bunker positions northeast and southeast of a
prominent rock, at the nearby trees", which I have not verified.

### What the terrain model says

NASADEM (about 26 x 31 m cells): the high point is the north end of a spine that continues south at 3,070-3,145 m and falls
steeply north (about 175 m in 370 m). East-west slopes either side of the summit are 20-23 degrees (cliffs are below this
resolution). West of the high point, at the Predator fix, there is a flat bench at 3,100-3,111 m about 180 m long north-south,
which fits "only one place to off-load a helicopter" and a bowl-shaped LZ.

### Candidate outcrop (LOW confidence; see "Competing placements" below, where it is weakened)

If the ridge photo was taken from the east looking west (the Shah-i-Kot plain is the hazy flat behind the crest), the crest
descends to the right, so right is north and the outcrop lies down-crest north of the Chinook, about 90-150 m by the
fuselage scale (very rough). The Naylor sketch (west up, my reading) also puts the boulder north-west of the Rangers'
position. In the June 2021 Esri imagery, a jagged light rock band about 50 m wide with dark fractures and conifers on its east
side is centred about **215 m north of the Predator fix: 33.34472 N 69.21191 E** (terrain 3,045 m; 250 m north-west of the
terrain high point, about 125 m below it). `orient_imagery.py` draws it as `orient_north_of_fix.png`. Against it: that is
farther and lower than a bunker complex "atop the peak" should be, the fix is only good to about 100 m, and I cannot tell a
single prominent rock from a natural rock band at 0.5 m. Treat it as the first place to look in Google Earth.

### Not reachable from this sandbox

apnews.com returns 403 and AP Images is a licensed archive, so I could not look at AP's archived photos; arsof-history.org
(the *Weapon of Choice* PDF) and globalsecurity.org are blocked or paywalled for downloads here, and history.army.mil,
af.mil and nationalmuseum.af.mil return 403. DVIDS and Esri tiles are reachable. The Drive connector returns no text for
image files, so I could not read the user's screenshots (including any with Blaber's orientation); attaching them in chat works.

## The user's Google Drive (accessed via the Drive connector)

**Access.** The connector lists and searches files and reads text files (md, txt, html). For images, `read_file_content`
returns nothing, but `download_file_content` returns the bytes (base64, saved to a tool-result file), which decode into real
images. In this session I pulled 45 images from the "aar roberts ridge" and "blaber aar photos" folders, and the KML
(`Takur_Ghar_Battlefield.kml`). Not read: the MP4s (84 MB), the PDFs, the GPKG/QGZ/KMZ/OBJ files. `decode_drive.py` is not in
this repository; the images and the KML are the user's files and are not copied here.

**What the images are.** Time-stamped annotated Predator infrared frames with labels (Enemy 1/2, Red Beard, B1, B2, R1, R2,
trench, DSHK, donkey, Roberts, Chapman; "Pic taken 2 days after (note steepness of terrain)", "FP1 FP2 are good fighting
positions with defilade, Mako went here initially, then Rangers fought from the positions for 13-15 hours", "Ammo supply point
behind R2"); a top-down schematic series (CSAR infil 04:57, actions 04:57-05:11, movement off the X 05:13, QRF infil/shootdown in
Razor 01 06:14) with a north arrow; ground photographs after the battle (wreckage, positions, remains, a helmet marked CROSE; some
are graphic); a 3D overview of the Anaconda area; *Milani* figures 8 and 9 (enemy bunker, command tent); a grey ridge photo; and
four unrelated phone screenshots of soldiers, which I did not use.

**Orientation measured from the schematic.** Its north arrow points 66.9 deg clockwise from page-up (principal axis of the arrow
pixels), so page-up is bearing 293 (WNW), page-right 23 (NNE). That agrees with the Naylor sketch ("W" arrow pointing up, my earlier
reading) to within the 25 deg tolerance I gave it, and with Copeland et al.'s "vertical cliff to the right (north-east)". On the
schematic, the Rocky Outcropping lies SE of B1 (bearing about 127, about 50-75 m) and R1 lies WSW of B1; B2 is NNW of R1.

**The user's KML already holds a working placement.** Folder "Summit schematic features (approx., from AAR deck)": Bunker 1
33.342744 N 69.213987 E, Bunker 2 33.342811 69.213791, Rock 1 "the boulder (low rock outcrop)" 33.342750 69.213932, Rock 2
33.342680 69.213639, DShK 33.342653 69.213488, LZ Razor 01 33.342145 69.214099, FP1, FP2, "Huge rock outcrop (anchors the saddle)"
33.342055 69.215377, each "placed from Blaber slide schematic on SRTM terrain; approximate (tens of metres)". The anchor is
the working summit point 33.3421 69.2138, which is the OpenStreetMap/NGA peak node. Distances from the KML boulder: B1 5 m,
terrain high point 43 m, KML LZ 69 m, OSM peak 69 m, Predator HUD fix 185 m (bearing 271), my candidate band 288 m (bearing 319).

### Competing placements, and a test (`schematic_register.py`)

Two placements for the bunker complex now compete: the KML's, at the summit on the highest ground, and my candidate rock band
215 m north of the Predator fix (3,045 m, about 125 m below the high point). `schematic_register.py SLIDE.png` drops the slide's
green tree blobs onto the June 2021 imagery under four anchor assumptions and compares the share of tree area landing on detected
conifer canopy with 2,000 random placements (same orientation and scale; 0.285 m per page pixel, from "Rangers about 60 m from the
bunkers", which is also what the KML implies; 0.2 as a sensitivity check):

| Anchor | On canopy (0.285 m/px) | Random median / 95th | Share of random placements as good |
|---|---|---|---|
| A  Razor 01 symbol = Predator HUD fix | 0.5% | 2.4% / 15.5% | 70% |
| B  outcrop = terrain high point | 4.2% | 2.6% / 17.4% | 40% |
| C  outcrop = candidate rock band | 24.9% | 2.7% / 16.8% | **1.1%** |
| D  Razor 01 symbol = KML LZ | **0.0%** | 2.5% / 15.2% | 100% |

At 0.2 m/px, C drops to 5.4% (33% of random placements do as well); A, B and D stay at or below chance. In the 2021 image the
nearest detected conifer to the KML's B1, B2, Rock 1, Rock 2, DShK and LZ is 28 to 43 m away, with none within 15 m, and the
wide view shows open ground around them with the conifers to the north and north-west.

How to read this, honestly:

* The KML placement is **not corroborated by trees** in 2021. The sources describe a big pine at B1 and a second tree at B2 (the
  user's own ledger notes a "splintered stump" and Ground Truth's 2024 "first tree"), so the trees may have been destroyed in
  2002 or later, may be small dwarf pines my canopy mask misses, or the KML anchor may be shifted by 30 m or more.
* My candidate fits the trees better at one scale (about 1% of random placements, but 6 combinations were tried, so about 7%
  after correcting for that), and fails at the other scale. It is also 125 m below the high point, against the sources' "atop
  the peak". I would not rely on it. It stays here as the best-fitting alternative, not as an identification.
* The Predator HUD point is 213 m west-north-west of the KML LZ (a 3.4 deg pointing difference at the frame's 1.93 nm slant
  range). That is plausible for a 2002 sensor aim point but I could not verify it, so I cannot say which is wrong.
* Settling it needs something the satellite image can't give: the user's 2024 summit-walk frames (tree pair, cliff rim, boulder)
  matched against the terrain, or a photo whose camera position is known.
