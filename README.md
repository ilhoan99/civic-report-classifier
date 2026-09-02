# Same Complaint, Different Agency

**Location-conditioned routing of civic safety reports under extreme class
imbalance** — companion code and interactive demo for the paper.

**Interactive demo:** https://ilhoan99.github.io/civic-report-classifier/

South Korea's nationwide civic reporting platform receives more than ten
million citizen reports a year, routed to 12 agencies whose sizes differ by
1,292:1. The correct agency is not a function of the report text alone:
identical complaints are legitimately routed to different agencies depending
on *where* they were filed. The deployed remedy is small and it is all here —
geocode each report to 1 of 229 coarse districts and prepend the district to
the text as two plain tokens:

```
[경기도 수원시] 도로에 포트홀이 생겨 차량 파손이 우려됩니다
```

Combined with a class-balanced loss, this lifts the rarest agency's F1 from
4.6 to 29.8 and beats the incumbent rule-based router 76.8% to 28.5% on a
balanced rare-agency sample of live intake.

## What is in this repository

| Path | Contents |
|---|---|
| `src/` | The released method: coordinates → district (`geocode.py`, the exact production logic) and district → model input (`region_tokens.py`), with a CLI walkthrough (`example.py`) and tests |
| `docs/` | The interactive demo (GitHub Pages): one report filed in different districts, real precomputed model outputs, deferral behavior, per-province results |
| `artifacts/` | Aggregate result tables from the paper's ledger (per-province accuracy, per-class F1, deferral curve, per-class auto-routing coverage), the LLM-prompt agency descriptions and tie-break rules, and a synthetic raw-data generator |
| `scripts/` | `download_boundaries.sh` — fetches the pinned boundary polygons (33 MB, not committed) |

## Quickstart

```bash
pip install -r src/requirements.txt      # shapely + numpy
bash scripts/download_boundaries.sh      # boundary polygons (admdongkor, CC BY 4.0)

python src/example.py --lat 37.2636 --lon 127.0286 \
    --text "도로에 포트홀이 생겨 차량 파손이 우려됩니다"
# coordinates : (37.2636, 127.0286)
# district    : 경기도 수원시  (1 of 229; coordinates are discarded from here on)
# model input : [경기도 수원시] 도로에 포트홀이 생겨 차량 파손이 우려됩니다

python -m pytest src/test_geocode.py     # district disambiguation, coastal fallback
```

To try the pipeline shape without any real data:

```bash
python artifacts/make_sample_data.py --rows 3000 --out sample_reports.csv
```

The generated rows carry synthetic GPS coordinates that work with
`src/geocode.py`, so the full coordinates → district → region-token path runs
end to end.

To run the demo locally:

```bash
cd docs && python -m http.server 8000    # then open http://localhost:8000
```

## What is deliberately not here

- **The report corpus.** Citizen reports never leave the operator's
  environment and cannot be released. Demo texts are illustrative paraphrases
  written by the authors.
- **Model weights.** The classifier (klue/roberta-base fine-tune) serves
  inside the operator's environment. The demo's predictions are precomputed
  real outputs of the trained models; the generating checkpoints are recorded
  in `docs/data/examples.json`.
- **Precise locations.** The method conditions on 229 coarse districts only —
  that is the privacy boundary, and the demo respects it (district polygons,
  no street-level pins).

## Data and licenses

- Code: MIT (see `LICENSE`).
- Administrative boundary polygons:
  [admdongkor](https://github.com/vuski/admdongkor) (CC BY 4.0), version
  pinned to `ver20260401`. The lightweight district/province outlines under
  `docs/data/` are simplified derivatives of the same data.
- Demo basemap tiles: © OpenStreetMap contributors, © CARTO.

## Citation

```bibtex
@misc{kim2026samecomplaint,
  title  = {Same Complaint, Different Agency: Location-Conditioned Routing
            of Civic Reports under Extreme Class Imbalance},
  author = {Kim, Ilhwan and Oh, Seungtaek and Kim, Changhwan and Moon, Jaewon},
  year   = {2026},
  url    = {https://github.com/ilhoan99/civic-report-classifier}
}
```

This is a research artifact by the authors (KETI); it is not an
official service of the reporting platform.
