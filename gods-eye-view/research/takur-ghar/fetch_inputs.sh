#!/usr/bin/env bash
# Download the DEM tile and Landsat bands used by build_scene.py (free, Microsoft Planetary Computer).
# Usage: ./fetch_inputs.sh [sep|mar]   (default sep)
#   sep: primary LE07 path 153 (13 Sep 2002); fill for its uncovered east edge: path 152 (22 Sep 2002).
#   mar: primary LE07 path 153 (5 Mar 2002, day after the battle); fill: LE07 path 152 (14 Mar 2002). Files get a mar_ prefix.
#        (LT05 6 Mar was tried for the fill but has dark banding in the box's east, so it is not used.)
set -euo pipefail
SEASON=${1:-sep}
PC=https://planetarycomputer.microsoft.com/api
sign() { curl -sS -m 60 "$PC/sas/v1/sign?href=$1" | python3 -c "import sys,json;print(json.load(sys.stdin)['href'])"; }
get() { curl -sS -m 600 -o "$2" "$(sign "$1")"; }
[ -f NASADEM_HGT_n33e069.tif ] || get https://nasademeuwest.blob.core.windows.net/nasadem-cog/v001/NASADEM_HGT_n33e069.tif NASADEM_HGT_n33e069.tif
fetch_scene() {  # item id, output prefix
  curl -sS -m 60 "$PC/stac/v1/collections/landsat-c2-l2/items/$1" -o "$2item.json"
  for b in red green blue; do
    get "$(python3 -c "import json;print(json.load(open('$2item.json'))['assets']['$b']['href'])")" "$2$b.tif"
  done
}
if [ "$SEASON" = mar ]; then
  fetch_scene LE07_L2SP_153037_20020305_02_T1 "mar_"
  fetch_scene LE07_L2SP_152037_20020314_02_T1 "mar_fill_"
else
  fetch_scene LE07_L2SP_153037_20020913_02_T1 ""
  fetch_scene LE07_L2SP_152037_20020922_02_T1 "fill_"
fi
