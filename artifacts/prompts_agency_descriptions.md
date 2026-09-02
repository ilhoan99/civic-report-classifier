# Agency jurisdiction descriptions and tie-break rules

These are the description and tie-break blocks used in the paper's LLM-baseline
prompts, released verbatim (Korean originals, with the English renderings used
during development). They were **written by the authors from public sources**;
they are not operator documentation.

Label ids are the canonical training ids. Note that the id order differs from
the share order used in the paper's tables: the rarest class is label 8
(한국농어촌공사 / KRC), while label 11 (한국통신사업자연합회 / KCTA) is the
third-largest class.

| id | abbr | agency |
|---:|---|---|
| 0 | LocalGov | 지자체 |
| 1 | Police | 경찰청 |
| 2 | KEPCO | 한국전력공사 |
| 3 | MOEL | 고용노동부 |
| 4 | KEC | 한국도로공사 |
| 5 | KORAIL | 한국철도공사 |
| 6 | EduOff | 교육청 |
| 7 | LH | 한국토지주택공사 |
| 8 | KRC | 한국농어촌공사 |
| 9 | MOLIT | 국토교통부 |
| 10 | MSIT | 과학기술정보통신부 |
| 11 | KCTA | 한국통신사업자연합회 |

## Descriptions (Korean — the prompt originals)

**0 지자체.** 도로 포트홀·보도 파손, 가로등·보안등 고장, 맨홀·배수구 이상,
불법주정차 과태료, 쓰레기 무단투기, 불법광고물 등 생활권 시설물과 생활불편
신고 대부분을 처리하는 기본 소관 기관. 나머지 11개 기관은 이 기본값에서
시설·구간별로 떼어낸 예외에 해당한다.

**1 경찰청.** 과속·신호위반·중앙선 침범·난폭운전 등 운행 중 교통법규 위반
신고를 접수한다. 신호기·교통안전표지 같은 교통규제 시설과 관련한 신고도
경찰 소관이다.

**2 한국전력공사.** 전주(전신주) 기울어짐·파손, 늘어지거나 끊어진 전선,
변압기·배전설비 이상, 정전·감전 위험 등 전력설비 신고를 맡는다. 24시간 123
신고 창구를 운영한다.

**3 고용노동부.** 건설·해체 공사장이나 사업장의 산업안전 위반 신고를
처리한다. 안전난간·낙하물방지망 미설치, 안전모·안전화·안전대 미착용 등
근로자 안전조치 미비가 주 대상이다.

**4 한국도로공사.** 고속도로 본선과 나들목·휴게소·졸음쉼터 등 고속도로 시설
관련 신고를 담당한다. 포장 파손(포트홀), 차로 낙하물, 방호울타리·표지판
손상, 휴게소 시설 불편 등이 해당한다.

**5 한국철도공사.** 철도 건널목, 승강장·역사 시설, 선로 주변 위험 요소 등
철도 이용·운행과 관련한 신고를 접수한다. 열차나 역 구내에서 발견한
생명·신체 위험 요인이 주 대상이다.

**6 교육청.** 학교 부지 안의 건물·담장·놀이시설·통학버스 등 학교 시설과
학생 안전 관련 신고를 시·도 교육청이 처리한다. 국공립·사립 초·중·고가 모두
지도·감독 대상이다.

**7 한국토지주택공사.** LH가 공급·관리하는 공공임대·공공분양 단지와 조성
중인 택지·공사 현장의 시설 안전 신고를 처리한다. 단지 내 균열·누수 등
하자와 미조성 부지의 위험 요소가 주 대상이다.

**8 한국농어촌공사.** 농업용 저수지·수문과 용수로·배수로 등 농업생산기반시설
관련 신고를 처리한다. 수로 덮개 파손과 추락 위험, 제방·저수지 누수 등
농어촌 지역 신고가 많다.

**9 국토교통부.** 국토관리청이 관리하는 일반국도 구간의 포장 파손·도로
시설물 이상 신고를 담당한다. 철도·항공·자동차 안전과 건설공사 현장의
건설사고 관련 신고도 이 부처 소관이다.

**10 과학기술정보통신부.** 방송통신 설비·통신망, 우정사업(우체국·우편) 등
소관 분야의 신고를 담당한다. 공중케이블 정비와 불법스팸 대응 정책을
총괄하는 부처이기도 하다.

**11 한국통신사업자연합회.** 전주에 얽히거나 늘어진 방송·통신 케이블 등
공중케이블 관련 신고를 받아 통신사업자에 연계해 정비한다. 문자·전화
불법스팸에 대한 통신사 공동 대응 창구 역할도 한다.

## Descriptions (English renderings)

**0 LocalGov.** Default handler for the bulk of civic safety reports: potholes
and broken pavement, streetlight and security-light outages, manholes and
drains, illegal-parking penalties, fly-tipping and illegal signage. The other
eleven bodies are exceptions carved out of this default.

**1 Police.** Handles moving traffic violations reported by citizens —
speeding, running signals, crossing the centre line, reckless driving. Traffic
signals and regulatory road signs also fall under police jurisdiction.

**2 KEPCO.** Handles electricity distribution assets: leaning or damaged
utility poles, sagging or downed power lines, faulty transformers and
switchgear, outages and electrocution hazards. It runs the 24-hour 123 hotline
for these reports.

**3 MOEL.** Handles industrial-safety violations at construction, demolition
and other worksites: missing guardrails or debris nets, workers without
helmets, safety shoes or harnesses, and similar failures to provide required
protection.

**4 KEC.** Handles the expressway network — main lines, interchanges, service
areas and rest stops. Typical reports are potholes and pavement damage,
objects fallen in the lanes, damaged guardrails and signs, and problems with
rest-area facilities.

**5 KORAIL.** Handles reports tied to rail operation and use: level crossings,
platforms and station facilities, and hazards beside the track. Typical cases
are risks to life or limb spotted on a train or inside a station.

**6 EduOff.** Provincial and metropolitan offices of education handle reports
on facilities inside school grounds — buildings, walls, playground equipment,
school buses — and on student safety. They supervise both public and private
primary and secondary schools.

**7 LH.** Handles facility-safety reports inside public rental and public-sale
housing estates LH supplies and manages, and on land-development and
construction sites it is still working on. Typical cases are cracks, leaks and
other defects in its blocks, and hazards on undeveloped parcels.

**8 KRC.** Handles agricultural infrastructure it manages: irrigation
reservoirs and sluice gates, and supply and drainage canals. Typical reports
are broken canal covers and fall hazards, or leaking embankments and
reservoirs in rural areas.

**9 MOLIT.** Handles general national highway sections managed by its regional
construction offices — pavement damage, roadside facilities. Rail, aviation
and motor-vehicle safety, plus construction-site accident reporting, also sit
with this ministry.

**10 MSIT.** Handles reports in its own domains — broadcasting and telecom
facilities and networks, and the postal service (post offices, mail). It is
also the ministry that owns overhead-cable tidy-up policy and illegal-spam
countermeasures.

**11 KCTA.** Telecom industry association that takes reports about tangled or
sagging overhead broadcast/telecom cables on utility poles and routes them to
member carriers for tidy-up. It also serves as the carriers' joint channel on
illegal SMS and voice spam.

## Tie-break rules (Korean originals, then English)

1. 전주(전신주)·전선·변압기 등 전력설비 자체에 관한 신고는 지자체가 아니라
   한국전력공사 소관이지만, 같은 전주에 달린 가로등·보안등의 점등 불량은
   지자체 소관이고 전주에 얽힌 방송·통신 케이블은 통신사업자
   측(한국통신사업자연합회) 소관이다.
2. 학교 부지 경계 안쪽의 건물·담장·놀이시설 등 학교 시설 신고는 지자체가
   아니라 시·도 교육청 소관이며, 경계 바깥의 통학로·어린이보호구역 도로
   시설은 지자체(단속은 경찰) 소관이다.
3. 고속도로 본선·나들목·휴게소 구간의 신고는 지자체가 아니라 한국도로공사
   소관이고(민자 구간은 해당 운영사), 일반국도는 국토교통부
   지방국토관리청이, 시(동) 지역 국도와 그 밖의 시·군·구도는 지자체가 맡는다.

---

1. Reports about the electrical plant itself — leaning poles, sagging or
   broken power lines, transformers — go to KEPCO rather than the local
   government, but a streetlight mounted on the same pole is the local
   government's, and the broadcast/telecom cables strung on it belong to the
   carriers' side (KCTA).
2. Reports about facilities inside the school boundary — buildings, walls,
   playground equipment — go to the provincial office of education rather than
   the local government, while roads, school routes and child-protection zones
   just outside the boundary stay with the local government (enforcement with
   the police).
3. Reports on expressway main lines, interchanges and service areas go to
   Korea Expressway Corporation rather than the local government (privately
   financed stretches go to their concessionaire), while general national
   highways sit with MOLIT's regional construction offices and in-city
   (dong-area) national-highway stretches and all municipal roads sit with the
   local government.
