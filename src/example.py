"""End-to-end walkthrough: GPS point + report text -> model input.

    python example.py --lat 37.2636 --lon 127.0286 \
        --text "도로에 포트홀이 생겨 차량 파손이 우려됩니다"

Prints the resolved district, the exact string the classifier is trained on,
and (when `transformers` is installed) its subword segmentation.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from geocode import DistrictGeocoder
from region_tokens import build_model_input, show_tokenization

DEFAULT_BOUNDARY = (Path(__file__).resolve().parents[1]
                    / "data" / "HangJeongDong_ver20260401.geojson")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--text", type=str, required=True)
    parser.add_argument("--boundary-file", type=str, default=str(DEFAULT_BOUNDARY))
    args = parser.parse_args()

    if not Path(args.boundary_file).exists():
        parser.error(f"boundary file not found: {args.boundary_file}\n"
                     "Run scripts/download_boundaries.sh first.")

    geocoder = DistrictGeocoder(args.boundary_file)
    sido, sigungu = geocoder.lookup(args.lat, args.lon)
    model_input = build_model_input(args.text, sido, sigungu)

    print(f"coordinates : ({args.lat}, {args.lon})")
    print(f"district    : {sido} {sigungu}  (1 of 229; coordinates are "
          "discarded from here on)")
    print(f"model input : {model_input}")

    pieces = show_tokenization(model_input)
    if pieces is None:
        print("tokens      : (install `transformers` to see the subword pieces)")
    else:
        print(f"tokens      : {' '.join(pieces)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
