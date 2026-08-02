"""대전 생활물류 거점 입지 추천 Streamlit 대시보드.

실행:
    streamlit run streamlit_app.py
"""
from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.express as px
import pydeck as pdk
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.set_page_config(
    page_title="대전 생활물류 거점 추천",
    page_icon="📦",
    layout="wide",
)

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
    raise FileNotFoundError(f"{filename}을 찾을 수 없습니다.")


@st.cache_data

def load_data() -> tuple[pd.DataFrame, gpd.GeoDataFrame]:
    ranking = pd.read_csv(find_file("location_ranking.csv"), encoding="utf-8-sig")
    map_gdf = gpd.read_file(find_file("location_map.geojson"))
    if map_gdf.crs is None:
        map_gdf = map_gdf.set_crs("EPSG:4326")
    else:
        map_gdf = map_gdf.to_crs("EPSG:4326")
    return ranking, map_gdf


def calculate_score(df: pd.DataFrame, w_pop: float, w_house: float, w_supply: float) -> pd.DataFrame:
    result = df.copy()
    total = w_pop + w_house + w_supply
    if total <= 0:
        w_pop = w_house = w_supply = 1 / 3
    else:
        w_pop, w_house, w_supply = w_pop / total, w_house / total, w_supply / total

    for col in ["인구_norm", "세대수_norm", "우체국_norm"]:
        result[col] = pd.to_numeric(result[col], errors="coerce").fillna(0).clip(0, 1)

    result["공급부족_norm"] = 1 - result["우체국_norm"]
    result["동적입지점수"] = 100 * (
        w_pop * result["인구_norm"]
        + w_house * result["세대수_norm"]
        + w_supply * result["공급부족_norm"]
    )
    result["순위"] = result["동적입지점수"].rank(method="min", ascending=False).astype(int)
    return result.sort_values("동적입지점수", ascending=False).reset_index(drop=True)


def add_clusters(df: pd.DataFrame, n_clusters: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    result = df.copy()
    features = result[["인구_norm", "세대수_norm", "우체국_norm"]].fillna(0)
    scaled = StandardScaler().fit_transform(features)
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=20)
    result["cluster"] = model.fit_predict(scaled)

    summary = (
        result.groupby("cluster", as_index=False)
        .agg(
            행정동수=("행정동", "count"),
            평균인구=("총 인구수", "mean"),
            평균공동주택세대수=("공동주택세대수", "mean"),
            평균우체국수=("우체국수", "mean"),
            평균점수=("동적입지점수", "mean"),
        )
        .sort_values("평균점수", ascending=False)
        .reset_index(drop=True)
    )
    names = ["최우선 후보군", "유망 후보군", "관찰 후보군", "낮은 우선순위", "보완 검토군", "기타 군집"]
    mapping = {int(row.cluster): names[i] if i < len(names) else f"군집 {i+1}" for i, row in summary.iterrows()}
    result["군집명"] = result["cluster"].map(mapping)
    summary["군집명"] = summary["cluster"].map(mapping)
    return result, summary


def score_to_color(score: float) -> list[int]:
    value = float(np.clip(score, 0, 100)) / 100
    return [int(255 * value), int(80 + 120 * (1 - value)), int(60 + 100 * (1 - value)), 180]


def build_map(map_gdf: gpd.GeoDataFrame, scored: pd.DataFrame) -> pdk.Deck:
    merge_cols = ["구", "행정동", "동적입지점수", "순위", "군집명", "총 인구수", "공동주택세대수", "우체국수"]
    lookup = scored[merge_cols].drop_duplicates(["구", "행정동"])
    gdf = map_gdf.drop(columns=[c for c in merge_cols[2:] if c in map_gdf.columns], errors="ignore")
    gdf = gdf.merge(lookup, on=["구", "행정동"], how="left")
    gdf["동적입지점수"] = gdf["동적입지점수"].fillna(0)
    gdf["fill_color"] = gdf["동적입지점수"].apply(score_to_color)

    geojson = json.loads(gdf.to_json())
    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson,
        pickable=True,
        stroked=True,
        filled=True,
        get_fill_color="properties.fill_color",
        get_line_color=[60, 60, 60, 180],
        line_width_min_pixels=1,
        auto_highlight=True,
    )
    tooltip = {
        "html": "<b>{구} {행정동}</b><br/>점수: {동적입지점수}<br/>순위: {순위}<br/>군집: {군집명}<br/>인구: {총 인구수}<br/>공동주택 세대수: {공동주택세대수}<br/>우체국 수: {우체국수}",
        "style": {"backgroundColor": "steelblue", "color": "white"},
    }
    return pdk.Deck(
        layers=[layer],
        initial_view_state=pdk.ViewState(latitude=36.3504, longitude=127.3845, zoom=10.2, pitch=0),
        map_style="light",
        tooltip=tooltip,
    )


try:
    ranking_raw, map_gdf = load_data()
except Exception as exc:
    st.error(f"데이터 로딩 실패: {exc}")
    st.stop()

st.title("📦 AI 기반 대전 생활물류 거점 입지 추천 시스템")
st.caption("인구·공동주택 세대수·기존 우체국 공급을 결합해 행정동별 후보지를 비교합니다.")

with st.sidebar:
    st.header("분석 설정")
    selected_gu = st.multiselect("자치구", sorted(ranking_raw["구"].dropna().unique()), default=sorted(ranking_raw["구"].dropna().unique()))
    w_pop = st.slider("인구 수요 가중치", 0, 100, 40, 5)
    w_house = st.slider("공동주택 수요 가중치", 0, 100, 40, 5)
    w_supply = st.slider("기존 공급 부족 가중치", 0, 100, 20, 5)
    n_clusters = st.slider("K-Means 군집 수", 3, 6, 4)
    top_n = st.slider("표시할 상위 후보 수", 5, 30, 10)
    st.info("가중치는 자동으로 합계 100%가 되도록 재조정됩니다.")

filtered = ranking_raw[ranking_raw["구"].isin(selected_gu)].copy()
if filtered.empty:
    st.warning("선택한 조건에 해당하는 행정동이 없습니다.")
    st.stop()

scored = calculate_score(filtered, w_pop, w_house, w_supply)
scored, cluster_summary = add_clusters(scored, min(n_clusters, len(scored) - 1))
top = scored.head(top_n)

m1, m2, m3, m4 = st.columns(4)
m1.metric("분석 행정동", f"{len(scored)}개")
m2.metric("1순위", top.iloc[0]["행정동"])
m3.metric("1순위 점수", f"{top.iloc[0]['동적입지점수']:.1f}")
m4.metric("1순위 자치구", top.iloc[0]["구"])

left, right = st.columns([1.55, 1])
with left:
    st.subheader("행정동별 입지점수 지도")
    st.pydeck_chart(build_map(map_gdf[map_gdf["구"].isin(selected_gu)], scored), use_container_width=True)
with right:
    st.subheader(f"추천 TOP {top_n}")
    display_cols = ["순위", "구", "행정동", "동적입지점수", "군집명", "총 인구수", "공동주택세대수", "우체국수"]
    show = top[display_cols].copy()
    show["동적입지점수"] = show["동적입지점수"].round(1)
    st.dataframe(show, hide_index=True, use_container_width=True, height=520)

st.subheader("상위 후보 비교")
fig = px.bar(
    top.sort_values("동적입지점수"),
    x="동적입지점수",
    y="행정동",
    color="군집명",
    orientation="h",
    hover_data=["구", "총 인구수", "공동주택세대수", "우체국수"],
    labels={"동적입지점수": "입지점수(0~100)", "행정동": "행정동"},
)
st.plotly_chart(fig, use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    st.subheader("K-Means 군집 요약")
    summary_show = cluster_summary.copy()
    for col in ["평균인구", "평균공동주택세대수", "평균우체국수", "평균점수"]:
        summary_show[col] = summary_show[col].round(1)
    st.dataframe(summary_show[["군집명", "행정동수", "평균인구", "평균공동주택세대수", "평균우체국수", "평균점수"]], hide_index=True, use_container_width=True)
with c2:
    st.subheader("수요·공급 군집 분포")
    scatter = px.scatter(
        scored,
        x="인구_norm",
        y="세대수_norm",
        size="동적입지점수",
        color="군집명",
        hover_name="행정동",
        hover_data=["구", "우체국수", "동적입지점수"],
        labels={"인구_norm": "인구 정규화", "세대수_norm": "공동주택 세대수 정규화"},
    )
    st.plotly_chart(scatter, use_container_width=True)

st.subheader("후보지 상세 확인")
selected_dong = st.selectbox("행정동 선택", scored["행정동"].tolist())
row = scored.loc[scored["행정동"] == selected_dong].iloc[0]
d1, d2, d3, d4, d5 = st.columns(5)
d1.metric("입지 순위", f"{int(row['순위'])}위")
d2.metric("입지점수", f"{row['동적입지점수']:.1f}")
d3.metric("총 인구", f"{int(row['총 인구수']):,}명")
d4.metric("공동주택 세대", f"{int(row['공동주택세대수']):,}세대")
d5.metric("우체국", f"{int(row['우체국수'])}개")
st.write(f"**군집 해석:** {row['군집명']}")

csv_bytes = scored.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
st.download_button(
    "현재 분석 결과 CSV 다운로드",
    data=csv_bytes,
    file_name="daejeon_logistics_dynamic_ranking.csv",
    mime="text/csv",
)

st.divider()
st.caption("주의: 공동주택 주소의 행정동 매칭률이 낮아 일부 행정동의 공동주택 지표가 과소 추정될 수 있습니다. 최종 의사결정 전 주소 매핑 보완이 필요합니다.")
