"""대전 생활물류 거점 K-Means 군집분석.

실행:
    python kmeans_analysis.py

입력 파일은 스크립트와 같은 폴더 또는 data/processed 폴더에서 자동 탐색한다.
출력:
    location_ranking_clustered.csv
    location_map_clustered.geojson
    cluster_summary.csv
"""
from __future__ import annotations

from pathlib import Path
import json
import pandas as pd
import geopandas as gpd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

BASE_DIR = Path(__file__).resolve().parent


def find_file(filename: str) -> Path:
    candidates = [
        BASE_DIR / filename,
        BASE_DIR / "data" / "processed" / filename,
        Path.cwd() / filename,
        Path.cwd() / "data" / "processed" / filename,
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f"{filename}을 찾을 수 없습니다. 검색 경로: {candidates}")


def load_data() -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    ranking = pd.read_csv(find_file("location_ranking.csv"), encoding="utf-8-sig")
    map_gdf = gpd.read_file(find_file("location_map.geojson"))
    return ranking, map_gdf


def prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    feature_cols = ["인구_norm", "세대수_norm", "우체국_norm"]
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise ValueError(f"군집분석 필수 컬럼이 없습니다: {missing}")

    result = df.copy()
    result[feature_cols] = result[feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    return result, feature_cols


def choose_k(x_scaled, k_min: int = 3, k_max: int = 6) -> tuple[int, dict[int, float]]:
    max_allowed = min(k_max, len(x_scaled) - 1)
    scores: dict[int, float] = {}
    for k in range(k_min, max_allowed + 1):
        model = KMeans(n_clusters=k, random_state=42, n_init=20)
        labels = model.fit_predict(x_scaled)
        scores[k] = float(silhouette_score(x_scaled, labels))
    best_k = max(scores, key=scores.get)
    return best_k, scores


def assign_priority_labels(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """군집별 평균 입지점수 순서에 따라 해석 가능한 우선순위명을 붙인다."""
    result = df.copy()
    cluster_summary = (
        result.groupby("cluster", as_index=False)
        .agg(
            행정동수=("행정동", "count"),
            평균인구=("총 인구수", "mean"),
            평균공동주택세대수=("공동주택세대수", "mean"),
            평균우체국수=("우체국수", "mean"),
            평균입지점수=("입지점수", "mean"),
        )
        .sort_values("평균입지점수", ascending=False)
        .reset_index(drop=True)
    )

    names = ["최우선 후보군", "유망 후보군", "관찰 후보군", "낮은 우선순위", "보완 검토군", "기타 군집"]
    label_map = {
        int(row["cluster"]): names[i] if i < len(names) else f"우선순위 {i + 1}군"
        for i, (_, row) in enumerate(cluster_summary.iterrows())
    }
    result["군집명"] = result["cluster"].map(label_map)
    cluster_summary["군집명"] = cluster_summary["cluster"].map(label_map)
    return result, cluster_summary


def run_kmeans(n_clusters: int | None = None) -> tuple[pd.DataFrame, gpd.GeoDataFrame, pd.DataFrame, dict[int, float]]:
    ranking, map_gdf = load_data()
    ranking, feature_cols = prepare_features(ranking)

    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(ranking[feature_cols])

    selected_k, silhouette_scores = choose_k(x_scaled)
    if n_clusters is not None:
        if not 2 <= n_clusters < len(ranking):
            raise ValueError("n_clusters는 2 이상, 데이터 개수 미만이어야 합니다.")
        selected_k = n_clusters

    model = KMeans(n_clusters=selected_k, random_state=42, n_init=20)
    ranking["cluster"] = model.fit_predict(x_scaled)
    ranking, cluster_summary = assign_priority_labels(ranking)

    # 지도는 동일 행정동 경계가 여러 조각인 경우가 있어 행정동 기준으로 군집 결과만 붙인다.
    cluster_cols = ["구", "행정동", "cluster", "군집명"]
    cluster_lookup = ranking[cluster_cols].drop_duplicates(["구", "행정동"])

    map_clean = map_gdf.drop(columns=[c for c in ["cluster", "군집명"] if c in map_gdf.columns])
    clustered_map = map_clean.merge(cluster_lookup, on=["구", "행정동"], how="left")
    if clustered_map.crs is None:
        clustered_map = clustered_map.set_crs("EPSG:4326")
    else:
        clustered_map = clustered_map.to_crs("EPSG:4326")

    return ranking, clustered_map, cluster_summary, silhouette_scores


def main() -> None:
    ranking, clustered_map, summary, silhouette_scores = run_kmeans()

    ranking_path = BASE_DIR / "location_ranking_clustered.csv"
    map_path = BASE_DIR / "location_map_clustered.geojson"
    summary_path = BASE_DIR / "cluster_summary.csv"

    ranking.to_csv(ranking_path, index=False, encoding="utf-8-sig")
    clustered_map.to_file(map_path, driver="GeoJSON")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    print("K-Means 분석 완료")
    print("Silhouette scores:", json.dumps(silhouette_scores, ensure_ascii=False, indent=2))
    print(summary.to_string(index=False))
    print(f"저장: {ranking_path}")
    print(f"저장: {map_path}")
    print(f"저장: {summary_path}")


if __name__ == "__main__":
    main()
