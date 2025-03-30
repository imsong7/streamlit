# -*- coding:utf-8 -*-

import pandas as pd
from utils import load_data
import streamlit as st
from millify import prettify # 숫자 더 읽기 쉽게 간결한 형식으로 변환
from eda.map import showMap


st.set_page_config(
    page_title="서울시 부동산 대시보드",  
    layout="wide", 
    initial_sidebar_state="expanded" 
)

def run_home():
    total_df = load_data()
    st.markdown("## 대시보드 개요 \n"
    "본 프로젝트는 2025년 서울시 부동산 실거래가를 알려주는 대시보드입니다.")

    col = st.columns((2, 2), gap='medium')

    total_df["CTRT_DAY"] = pd.to_datetime(total_df["CTRT_DAY"].astype(str), format="%Y-%m-%d")
    total_df["month"] = total_df["CTRT_DAY"].dt.month
    selected_type = st.sidebar.selectbox("주거형태별", sorted(total_df["BLDG_USG"].unique()), index=1)

    if selected_type == "단독다가구":
        cols = ["CGG_NM", "STDG_NM", "ARCH_AREA", "THING_AMT"]
    else:
        cols = ["CGG_NM", "STDG_NM", "BLDG_NM", "ARCH_AREA", "THING_AMT"]

    
    total_df = total_df.loc[total_df["BLDG_USG"]==selected_type, :]

    selected_month = st.sidebar.radio("확인하고 싶은 월을 선택하세요", ["1월", "2월", "3월"])
    month_dict = {'1월': 1, '2월': 2, '3월': 3}

    filtered_month = total_df[total_df['month'] == month_dict[selected_month]]

    with col[0]:
        st.subheader(f"2025년 {month_dict[selected_month]}월 서울시 {selected_type} 평균가격")
        showMap(total_df, month_dict[selected_month])
        sorted_df = filtered_month[cols]
        st.markdown(f"#### 🏠 {selected_month} {selected_type} 가격 상위 3개")
        st.dataframe(sorted_df.sort_values(by='THING_AMT', ascending=False).head(3).reset_index(drop=True))
        st.markdown(f"#### 🏠 {selected_month} {selected_type} 가격 하위 3개")
        st.dataframe(sorted_df.sort_values(by='THING_AMT', ascending=True).head(3).reset_index(drop=True))

    with col[1]:
        st.subheader('')
        cgg_nm = st.selectbox("자치구", sorted(total_df["CGG_NM"].unique()))
        st.markdown(f'#### {cgg_nm} {selected_month} {selected_type} 가격 개요')

        col1, col2 = st.columns(2)

        avg_max_price = filtered_month.groupby("CGG_NM")['THING_AMT'].max().mean()
        avg_min_price = filtered_month.groupby("CGG_NM")['THING_AMT'].min().mean()

        filtered_month = filtered_month[filtered_month['CGG_NM'] == cgg_nm]
        sorted_df = filtered_month[cols]

        # NaN 값 제외하고 최소가격과 최대가격 계산
        filtered_month = filtered_month.dropna(subset=['THING_AMT'])  
        min_price = filtered_month['THING_AMT'].min()
        max_price = filtered_month['THING_AMT'].max()

        # 최대/최소 가격과 평균 최대/최소 가격 차이 계산
        max_delta = max_price - avg_max_price
        min_delta = min_price - avg_min_price

        with col1:
            st.metric(
                label=f"{cgg_nm} 최소가격 (만원)", 
                value=f"{min_price:,.0f}", 
                delta=f"{min_delta:,.0f} 만원"
            )

        with col2:
            st.metric(
                label=f"{cgg_nm} 최대가격 (만원)", 
                value=f"{max_price:,.0f}", 
                delta=f"{max_delta:,.0f} 만원"
            )


        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"#### 🏠 {cgg_nm} {selected_type} 가격 상위 5개")
        st.dataframe(sorted_df.sort_values(by='THING_AMT', ascending=False).head(5).reset_index(drop=True))
        st.markdown(f"#### 🏠 {cgg_nm} {selected_type} 가격 하위 5개")
        st.dataframe(sorted_df.sort_values(by='THING_AMT', ascending=True).head(5).reset_index(drop=True))
        
    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption("출처 : [서울시 부동산 실거래가 정보](https://data.seoul.go.kr/dataList/OA-21275/S/1/datasetView.do)")


    
       