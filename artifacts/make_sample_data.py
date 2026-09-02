"""Synthetic raw-report generator — try the pipeline without the real corpus.

The real corpus cannot be released (reports never leave the operator's
environment), so this generator mimics its shape instead: the raw column
layout, the extreme class imbalance, reports forwarded to more than one
agency under the same report id, duplicated texts, empty texts, unmappable
agency names, and GPS coordinates jittered around each province.

    python make_sample_data.py --rows 3000 --out sample_reports.csv

The generated coordinates work with src/geocode.py, so the full
coords -> district -> region-token path can be exercised end to end.
Standalone: needs only numpy + pandas.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# Province -> a representative interior point (derived from the boundary
# polygons); synthetic reports scatter around it.
SIDO_CENTER = {
    "서울특별시": (37.5659, 126.9385), "부산광역시": (35.1937, 129.0504),
    "대구광역시": (35.9659, 128.6497), "인천광역시": (37.7045, 126.4413),
    "광주광역시": (35.1598, 126.8322), "대전광역시": (36.3436, 127.3909),
    "울산광역시": (35.5259, 129.2148), "세종특별자치시": (36.5733, 127.2665),
    "경기도": (37.5927, 127.4081), "강원특별자치도": (37.8185, 128.2122),
    "충청북도": (36.6351, 127.5777), "충청남도": (36.5319, 126.8237),
    "전북특별자치도": (35.7305, 127.1363), "전라남도": (34.8886, 126.9989),
    "경상북도": (36.3509, 128.6368), "경상남도": (35.3418, 128.3735),
    "제주특별자치도": (33.3600, 126.5271),
}
SIDO = sorted(SIDO_CENTER)

# agency name -> report-text templates (Korean, synthetic)
ORG_TEMPLATES = {
    "서울특별시": ["{loc} 인도 위 불법 주정차 차량 단속 부탁드립니다.",
                   "{loc} 공원에 쓰레기 무단투기가 심각합니다. 조치 바랍니다.",
                   "{loc} 가로등이 고장나서 밤에 너무 어둡습니다."],
    "경기도": ["{loc} 도로에 포트홀이 생겨 위험합니다.",
               "{loc} 산책로 옆 배수로가 막혀 악취가 납니다.",
               "{loc} 어린이보호구역 과속 차량 단속 요청합니다."],
    "부산광역시": ["{loc} 해안가 방파제 난간이 파손되어 있습니다.",
                   "{loc} 버스정류장 안내판이 떨어질 것 같아요."],
    "경찰청": ["{loc} 사거리에서 신호위반 차량이 너무 많습니다. 단속 바랍니다.",
               "{loc} 골목에서 상습적인 음주 소란이 있습니다.",
               "{loc} 무인 오토바이 폭주족 신고합니다."],
    "한국전력공사": ["{loc} 전신주 전선이 늘어져 보행자 머리에 닿을 것 같습니다.",
                     "{loc} 변압기에서 스파크가 튀는 것을 목격했습니다."],
    "고용노동부": ["{loc} 공사현장 근로자들이 안전모 없이 작업 중입니다.",
                   "{loc} 사업장에서 임금체불이 계속되고 있습니다."],
    "한국도로공사": ["{loc} 고속도로 갓길에 낙하물이 방치되어 있습니다.",
                     "{loc} 고속도로 방음벽이 파손되었습니다."],
    "한국철도공사": ["{loc} 기차역 승강장 안전문이 오작동합니다.",
                     "{loc} 철도 건널목 차단기가 내려오지 않습니다."],
    "서울특별시교육청": ["{loc} 초등학교 통학로에 불법 주차가 많아 위험합니다.",
                         "{loc} 학교 담장이 기울어져 있어 붕괴가 우려됩니다."],
    "경기도교육청": ["{loc} 중학교 앞 신호등 점멸이 고장났습니다."],
    "한국토지주택공사": ["{loc} 임대아파트 승강기가 자주 멈춥니다.",
                         "{loc} LH 단지 놀이터 시설물이 파손되었습니다."],
    "한국농어촌공사": ["{loc} 농수로 둑이 무너져 침수가 우려됩니다.",
                       "{loc} 저수지 수문 주변 접근 방지 펜스가 없습니다."],
    "국토교통부": ["{loc} 국도 교량 이음새가 벌어져 있습니다.",
                   "{loc} 신축 건물 외벽 자재가 떨어질 것 같습니다."],
    "과학기술정보통신부": ["{loc} 통신 공사 후 맨홀 뚜껑이 열려 있습니다.",
                           "{loc} 기지국 공사 자재가 인도를 막고 있습니다."],
    "정부산하기관및위원회": ["{loc} 스팸 문자가 하루 수십 통씩 옵니다. 차단 요청합니다.",
                             "{loc} 불법 스팸 전화 신고합니다."],
    # unmappable agencies -- exercise the pipeline's unknown-label handling
    "해양경찰청": ["{loc} 항구 근처 어선이 기름을 유출하는 것 같습니다."],
    "국민권익위원회": ["{loc} 관련 행정 처분에 대한 민원입니다."],
}

# imbalanced draw weights: local-government orgs dominate
ORG_WEIGHTS = {
    "서울특별시": 30, "경기도": 25, "부산광역시": 10,
    "경찰청": 12, "한국전력공사": 4, "고용노동부": 3,
    "한국도로공사": 3, "한국철도공사": 2,
    "서울특별시교육청": 3, "경기도교육청": 1,
    "한국토지주택공사": 1.5, "한국농어촌공사": 1,
    "국토교통부": 1.5, "과학기술정보통신부": 1,
    "정부산하기관및위원회": 1, "해양경찰청": 0.7, "국민권익위원회": 0.3,
}

PLACES = ["중앙로 12", "역전길 45", "시장통 3", "공단대로 88", "학교앞 사거리",
          "강변북로 진입로", "터미널 앞", "아파트 후문", "산업단지 2문", "구청 앞"]
CHANNELS = ["앱", "웹", "전화", "방문"]


def generate(rows: int, seed: int = 7) -> pd.DataFrame:
    rng = np.random.RandomState(seed)
    orgs = list(ORG_WEIGHTS)
    probs = np.array([ORG_WEIGHTS[o] for o in orgs], dtype=float)
    probs /= probs.sum()

    records = []
    for i in range(rows):
        org = orgs[rng.choice(len(orgs), p=probs)]
        sido = SIDO[rng.randint(len(SIDO))]
        clat, clon = SIDO_CENTER[sido]
        loc = f"{sido} {PLACES[rng.randint(len(PLACES))]}"
        template = ORG_TEMPLATES[org][rng.randint(len(ORG_TEMPLATES[org]))]
        text = template.format(loc=loc)
        if rng.rand() < 0.5:  # vary the surface form
            text += f" 접수 요청드립니다. (민원 {rng.randint(1, 9999)}호)"
        records.append({
            "c_no": f"SPP-2026-{i:07d}",
            "c_a_contents": text,
            "c_manage_top_org_name": org,
            "c_sido": sido,
            "c_a_w": round(clat + rng.uniform(-0.08, 0.08), 6),  # latitude
            "c_a_e": round(clon + rng.uniform(-0.08, 0.08), 6),  # longitude
            "c_recv_channel": CHANNELS[rng.randint(len(CHANNELS))],
            # unused noise columns, mimicking the dozens in the real export
            "c_reg_dt": f"2026-{rng.randint(1, 13):02d}-{rng.randint(1, 29):02d}",
            "c_status": ["접수", "처리중", "완료"][rng.randint(3)],
            "c_file_cnt": rng.randint(0, 4),
        })

    df = pd.DataFrame(records)

    # same report id forwarded to a second agency (multi-forwarding): 2%
    n_amb = max(1, rows // 50)
    amb = df.sample(n=n_amb, random_state=seed).copy()
    amb["c_manage_top_org_name"] = "경찰청"
    # duplicated report texts under fresh ids: 3%
    n_dup = max(1, rows * 3 // 100)
    dup = df.sample(n=n_dup, random_state=seed + 1).copy()
    dup["c_no"] = [f"SPP-2026-D{i:06d}" for i in range(len(dup))]
    # empty texts: 1%
    n_empty = max(1, rows // 100)
    empty = df.sample(n=n_empty, random_state=seed + 2).copy()
    empty["c_a_contents"] = "  "
    empty["c_no"] = [f"SPP-2026-E{i:06d}" for i in range(len(empty))]

    out = pd.concat([df, amb, dup, empty], ignore_index=True)
    return out.sample(frac=1, random_state=seed + 3).reset_index(drop=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate synthetic raw reports")
    parser.add_argument("--rows", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--out", type=str, default="sample_reports.csv")
    args = parser.parse_args()

    df = generate(args.rows, args.seed)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.suffix.lower() in (".xlsx", ".xls"):
        df.to_excel(out, index=False)
    else:
        df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"{len(df)} rows -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
