#!/usr/bin/env bash
# Fetch the pinned administrative boundary polygons (not committed: 33 MB).
#
# Source: admdongkor (https://github.com/vuski/admdongkor), CC BY 4.0.
# The version is pinned to the one used to build the paper's datasets.
set -euo pipefail

DEST="$(dirname "$0")/../data"
FILE="HangJeongDong_ver20260401.geojson"
URL="https://raw.githubusercontent.com/vuski/admdongkor/master/ver20260401/${FILE}"

mkdir -p "$DEST"
if [ -f "$DEST/$FILE" ]; then
    echo "already present: $DEST/$FILE"
    exit 0
fi
echo "downloading $FILE (~33 MB) ..."
curl -L --fail -o "$DEST/$FILE" "$URL"
echo "done: $DEST/$FILE"
