#!/usr/bin/env bash
# Download the DEM tile and Landsat bands used by build_scene.py (free, Microsoft Planetary Computer).
# Primary texture: LE07 path 153 (13 Sep 2002). Fill for its uncovered east edge: path 152 (22 Sep 2002).
set -euo pipefail
PC=https://planetarycomputer.microsoft.com/api
sign() { curl -sS -m 60 "$PC/sas/v1/sign?href=$1" | python3 -c "import sys,json;print(json.load(sys.stdin)['href'])"; }
get() { curl -sS -m 600 -o "$2" "$(sign "$1")"; }
get https://nasademeuwest.blob.core.windows.net/nasadem-cog/v001/NASADEM_HGT_n33e069.tif NASADEM_HGT_n33e069.tif
fetch_scene() {  # item id, output prefix
  curl -sS -m 60 "$PC/stac/v1/collections/landsat-c2-l2/items/$1" -o "$2item.json"
  for b in red green blue; do
    get "$(python3 -c "import json;print(json.load(open('$2item.json'))['assets']['$b']['href'])")" "$2$b.tif"
  done
}
fetch_scene LE07_L2SP_153037_20020913_02_T1 ""
fetch_scene LE07_L2SP_152037_20020922_02_T1 "fill_"
