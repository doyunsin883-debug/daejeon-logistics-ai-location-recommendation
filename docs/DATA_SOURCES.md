# 데이터 출처 및 공개 원칙

이 프로젝트는 공공데이터를 활용한 공모전/포트폴리오 목적의 분석입니다.  
public GitHub 저장소에는 원본 대용량 데이터(`data/raw/`)를 포함하지 않고, 앱 실행과 결과 확인에 필요한 정제 데이터(`data/processed/`)만 포함하는 것을 기본 원칙으로 합니다.

## 공개 저장소 운영 원칙

- 원본 데이터는 각 제공기관의 공식 페이지에서 직접 다운로드합니다.
- 원본 파일, 대용량 zip, shp, hwpx, 가상환경은 GitHub에 업로드하지 않습니다.
- README와 본 문서에 제공기관, 데이터명, 기준일, 원본 링크를 표시합니다.
- 각 데이터의 이용허락범위와 기타 유의사항은 다운로드 시점의 원문 페이지 고지를 우선합니다.
- 본 프로젝트는 제공기관이 후원하거나 검증한 결과가 아니며, 분석 책임은 프로젝트 작성자에게 있습니다.

## 주요 데이터 출처

| 구분 | 데이터명 | 제공기관 | 기준일/파일명 | 원본 링크 | 저장소 공개 방식 |
| --- | --- | --- | --- | --- | --- |
| 우체국 공급 | 과학기술정보통신부 우정사업본부_우체국 정보 파일 | 과학기술정보통신부 우정사업본부 | 2025-03-01 | [공공데이터포털](https://www.data.go.kr/data/15142424/fileData.do) | 원본 제외, 대전 필터링 결과만 사용 |
| 택배 물량 참고 | 과학기술정보통신부 우정사업본부_전국 우편번호(배달지 기준)별 택배물량 | 과학기술정보통신부 우정사업본부 | 2023-12-31 | [공공데이터포털](https://www.data.go.kr/data/15138728/fileData.do) | 원본 제외 |
| 행정동 경계 | 국가데이터처_SGIS 행정구역 통계 및 경계 | 국가데이터처 | 2025-06-30 | [공공데이터포털](https://www.data.go.kr/data/15129688/fileData.do) | 원본 shp/zip 제외, 정제 GeoJSON만 사용 |
| 주민등록 인구 | 2025년 12월말 주민등록 인구현황 | 대전광역시 | 2025-12 | [대전의 통계](https://www.daejeon.go.kr/sta/StaStatisticsFldView.do?boardId=normal_0009&colmn1Cont=C0201&colmn2Cont=&menuSeq=180&ntatcSeq=1504798173&pageIndex=1) | 원본 제외, 행정동 집계 결과 사용 |
| 공동주택 | 대전광역시 동구_공동주택현황 | 대전광역시 동구 | 2025-04-10 | [공공데이터포털](https://www.data.go.kr/data/15013553/fileData.do) | 원본 제외, 통합 정제 결과 사용 |
| 공동주택 | 대전광역시 서구_공동주택 현황 | 대전광역시 서구 | 2025-08-19 | [공공데이터포털](https://www.data.go.kr/data/15104512/fileData.do) | 원본 제외, 통합 정제 결과 사용 |
| 공동주택 | 대전광역시 유성구_공동주택 현황 | 대전광역시 유성구 | 2026-06-09 | [공공데이터포털](https://www.data.go.kr/data/15013653/fileData.do) | 원본 제외, 통합 정제 결과 사용 |
| 공동주택 | 대전광역시 대덕구_공동주택현황 | 대전광역시 대덕구 | 2025-08-31 | [공공데이터포털](https://www.data.go.kr/data/15013602/fileData.do) | 원본 제외, 통합 정제 결과 사용 |
| 공동주택 | 대전광역시 중구_건축물(공동주택)유지관리대상 | 대전광역시 중구 | 2025-01-01 | [공공데이터포털](https://www.data.go.kr/data/15120314/fileData.do) | 원본 제외, 통합 정제 결과 사용 |
| 인구 보조 | 대전광역시 서구_동별 성별 인구수 추이 | 대전광역시 서구 | 2023-04-30 | [공공데이터포털](https://www.data.go.kr/data/15135562/fileData.do) | 원본 제외 |
| 인구 보조 | 대전광역시 유성구_인구통계 현황 | 대전광역시 유성구 | 2025-06-30 | [공공데이터포털](https://www.data.go.kr/data/3069789/fileData.do) | 원본 제외 |
| 물류 환경 참고 | 지역별 물류창고업 등록현황 | 국가물류통합정보센터 | 조회 시점 기준 | [국가물류통합정보센터](https://nlic.go.kr/nlic/WhsStatsWarehouseLocation.action) | 원본 제외, 참고 지표로만 활용 |
| 물류 환경 참고 | 면적별 물류창고업 등록현황 | 국가물류통합정보센터 | 조회 시점 기준 | [국가물류통합정보센터](https://www.nlic.go.kr/nlic/WhsStatsWarehouseArea.action) | 원본 제외, 참고 지표로만 활용 |
| 물류 환경 참고 | 연도별 물류창고업 등록현황 | 국가물류통합정보센터 | 조회 시점 기준 | [국가물류통합정보센터](https://www.nlic.go.kr/nlic/WhsStatsWarehouseYear.action) | 원본 제외, 참고 지표로만 활용 |

## 저장소에 포함하는 정제 데이터

| 파일 | 설명 |
| --- | --- |
| `data/processed/population_dong.csv` | 행정동별 인구 집계 |
| `data/processed/apt_all.csv` | 구별 공동주택 데이터를 표준 컬럼으로 통합한 결과 |
| `data/processed/postoffice_daejeon.csv` | 대전 소재 우체국 필터링 결과 |
| `data/processed/postoffice_by_gu.csv` | 자치구별 우체국 수 집계 |
| `data/processed/location_ranking.csv` | 행정동별 인구, 공동주택, 우체국 지표 및 기본 입지점수 |
| `data/processed/location_ranking_clustered.csv` | K-Means 군집명이 포함된 후보지 결과 |
| `data/processed/cluster_summary.csv` | 군집별 평균 지표 요약 |
| `data/processed/location_map.geojson` | 대시보드 지도 표시용 정제 행정동 경계 |
| `data/processed/daejeon_boundary.geojson` | 대전 경계 정제 GeoJSON |

## 저작권 및 라이선스 주의

공공데이터라도 데이터별 이용조건이 다를 수 있습니다.  
저장소를 public으로 운영할 때는 다음 원칙을 따릅니다.

- 원본 데이터 전체 재배포를 피합니다.
- 데이터 출처와 기준일을 명시합니다.
- 제공기관이 프로젝트를 후원하거나 보증하는 것처럼 표현하지 않습니다.
- 분석으로 생성한 그래프와 표는 원본 데이터의 변형 결과임을 밝힙니다.
- 공모전 제출 전, 공모전 규정의 공개 가능 범위를 한 번 더 확인합니다.
