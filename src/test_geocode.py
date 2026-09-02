"""Sanity tests for the released geocoding path.

    python -m pytest src/test_geocode.py

Needs the boundary file (scripts/download_boundaries.sh).
"""
from pathlib import Path

import pytest

from geocode import DistrictGeocoder
from region_tokens import build_model_input

BOUNDARY = (Path(__file__).resolve().parents[1]
            / "data" / "HangJeongDong_ver20260401.geojson")

pytestmark = pytest.mark.skipif(
    not BOUNDARY.exists(),
    reason="boundary file missing; run scripts/download_boundaries.sh")


@pytest.fixture(scope="module")
def geocoder():
    return DistrictGeocoder(BOUNDARY)


def test_same_district_name_different_province(geocoder):
    """Six cities have a '중구'; the (province, district) pair disambiguates."""
    seoul = geocoder.lookup(37.5640, 126.9970)   # Seoul City Hall area
    daegu = geocoder.lookup(35.8690, 128.6060)   # central Daegu
    assert seoul == ("서울특별시", "중구")
    assert daegu == ("대구광역시", "중구")


def test_subcity_ward_coarsened_to_city(geocoder):
    """수원시장안구 must surface as 수원시 (the 255 -> 229 coarsening)."""
    _, sigungu = geocoder.lookup(37.3040, 127.0110)
    assert sigungu == "수원시"


def test_coastal_point_snaps_to_nearest(geocoder):
    """A point just offshore still resolves instead of failing."""
    sido, sigungu = geocoder.lookup(35.0700, 129.0900)  # off Busan harbor
    assert sido and sigungu


def test_out_of_range_rejected(geocoder):
    with pytest.raises(ValueError):
        geocoder.lookup(35.6762, 139.6503)  # Tokyo


def test_model_input_format():
    s = build_model_input("가로등이 기울어져 있습니다", "경기도", "수원시")
    assert s == "[경기도 수원시] 가로등이 기울어져 있습니다"
