"""Coordinates -> administrative district (the location half of the method).

This is the exact geocoding logic used to build the paper's datasets, extracted
from the production pipeline. Every report carries a GPS point; the classifier
never sees it. Instead the point is mapped once, at dataset-build time, to one
of 229 coarse districts (si/gun/gu), and only the district name reaches the
model. Coarsening to 229 categories is also the privacy boundary: precise
coordinates never leave the build step.

Steps, in order:
  1. Load the administrative-dong boundary polygons (3,558 features).
  2. Coarsen sub-city wards to their city: "수원시장안구" -> "수원시".
     District *names* are ambiguous on their own ("중구" exists in six
     cities), so the unit of conditioning is always the (province, district)
     pair -- 229 combinations.
  3. Point-in-polygon lookup with an STRtree spatial index.
  4. Points that fall in no polygon (coastline, reclaimed land; 0.105% of
     the corpus) snap to the nearest polygon instead of being dropped.

Requires shapely >= 2.0. Boundary data: see scripts/download_boundaries.sh.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Tuple

import numpy as np
import shapely
from shapely import STRtree
from shapely.geometry import shape

# Sub-city administrative wards ("일반구") merge into their city:
# 수원시장안구 -> 수원시. This is what takes the raw 255 units down to 229.
_GU_RE = re.compile(r"^(.+?시).+구$")

# Coordinates outside this box (all of South Korea) are rejected as invalid.
LAT_RANGE = (33.0, 38.7)
LON_RANGE = (124.5, 132.0)


class DistrictGeocoder:
    def __init__(self, boundary_file: str | Path) -> None:
        with open(boundary_file, encoding="utf-8") as f:
            feats = json.load(f)["features"]
        self._geoms = np.array([shape(f["geometry"]) for f in feats],
                               dtype=object)
        self._sido = np.array([f["properties"]["sidonm"] for f in feats])
        self._sigungu = np.array(
            [m.group(1) if (m := _GU_RE.match(s)) else s
             for s in (f["properties"]["sggnm"] for f in feats)])
        shapely.prepare(self._geoms)
        self._tree = STRtree(self._geoms)

    def lookup(self, lat: float, lon: float) -> Tuple[str, str]:
        """Map one point to its (province, district) pair.

        Raises ValueError for coordinates outside South Korea.
        """
        sido, sigungu = self.lookup_batch([lat], [lon])
        return sido[0], sigungu[0]

    def lookup_batch(self, lat, lon) -> Tuple[List[str], List[str]]:
        lat = np.asarray(lat, dtype=float)
        lon = np.asarray(lon, dtype=float)
        bad = ~(np.isfinite(lat) & np.isfinite(lon)
                & (lat >= LAT_RANGE[0]) & (lat <= LAT_RANGE[1])
                & (lon >= LON_RANGE[0]) & (lon <= LON_RANGE[1]))
        if bad.any():
            raise ValueError(
                f"{int(bad.sum())} coordinate(s) outside South Korea "
                f"(lat {LAT_RANGE}, lon {LON_RANGE})")

        idx = np.full(len(lat), -1, dtype=np.int64)
        inp, tr = self._tree.query(shapely.points(lon, lat),
                                   predicate="intersects")
        idx[inp] = tr

        # Coastal / reclaimed-land points: snap to the nearest polygon.
        miss = np.flatnonzero(idx < 0)
        if len(miss):
            inp, tr = self._tree.query_nearest(
                shapely.points(lon[miss], lat[miss]))
            idx[miss[inp]] = tr

        return list(self._sido[idx]), list(self._sigungu[idx])
