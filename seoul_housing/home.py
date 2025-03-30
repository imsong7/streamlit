# -*- coding:utf-8 -*-

import pandas as pd
from utils import load_data
import streamlit as st
from millify import prettify # 숫자 더 읽기 쉽게 간결한 형식으로 변환

def run_home():
    total_df = load_data()
    st.markdown("## 대시보드 개요 \n"
    "본 프로젝트는 2025년 서울시 부동산 실거래가를 알려주는 대시보드입니다.")

    total_df["CTRT_DAY"] = pd.to_datetime(total_df["CTRT_DAY"].astype(str), format="%Y-%m-%d")
    total_df["month"] = total_df["CTRT_DAY"].dt.month
    total_df = total_df.loc[total_df["BLDG_USG"]=="아파트", :]

    cgg_nm = st.sidebar.selectbox("자치구", sorted(total_df["CGG_NM"].unique()))
    selected_month = st.sidebar.radio("확인하고 싶은 월을 선택하세요", ["1월", "2월", "3월"])
    month_dict = {'1월': 1, '2월': 2, '3월': 3}
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader(f'📍 {cgg_nm} {selected_month} 아파트 가격 개요')

    st.markdown("자치구와 월을 클릭하면 자동으로 각 지역구의 거래된 **최소가격**, **최대가격**을 확인할 수 있습니다.")
    col1, col2 = st.columns(2)
    filtered_month = total_df[total_df['month'] == month_dict[selected_month]]

    avg_max_price = filtered_month.groupby("CGG_NM")['THING_AMT'].max().mean()
    avg_min_price = filtered_month.groupby("CGG_NM")['THING_AMT'].min().mean()

    filtered_month = filtered_month[filtered_month['CGG_NM'] == cgg_nm]

    # NaN 값 제외하고 최소가격과 최대가격 계산
    filtered_month = filtered_month.dropna(subset=['THING_AMT'])  
    min_price = filtered_month['THING_AMT'].min()
    max_price = filtered_month['THING_AMT'].max()

    max_delta = max_price - avg_max_price
    min_delta = min_price - avg_min_price



    with col1:
        st.metric(label=f"{cgg_nm} 최소가격(만원)", value=prettify(int(min_price)), delta=max_delta)

    with col2:
        st.metric(label=f"{cgg_nm} 최대가격(만원)", value=prettify(int(max_price)), delta=min_delta)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🏠 아파트 가격 상위 3 자치구")
    sorted_df = filtered_month[["CGG_NM", "STDG_NM", "BLDG_NM", "ARCH_AREA", "THING_AMT"]]
    st.dataframe(sorted_df.sort_values(by='THING_AMT', ascending=False).head(3).reset_index(drop=True))
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🏠 아파트 가격 하위 3 자치구")
    sorted_df = filtered_month[["CGG_NM", "STDG_NM", "BLDG_NM", "ARCH_AREA", "THING_AMT"]]
    st.dataframe(sorted_df.sort_values(by='THING_AMT', ascending=True).head(3).reset_index(drop=True))
    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption("출처 : [서울시 부동산 실거래가 정보](https://data.seoul.go.kr/dataList/OA-21275/S/1/datasetView.do)")