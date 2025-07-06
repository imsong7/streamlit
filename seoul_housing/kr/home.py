# -*- coding:utf-8 -*-

import pandas as pd
import streamlit as st
from utils import load_data
from millify import prettify
from map import showMap

def run_home(total_df):
    st.markdown("## 대시보드 개요 \n"
                "본 프로젝트는 2025년 서울시 부동산 실거래가를 알려주는 대시보드입니다.")

    col = st.columns((2, 2), gap='medium')

    total_df["CTRT_DAY"] = pd.to_datetime(total_df["CTRT_DAY"].astype(str), format="%Y-%m-%d")
    total_df["month"] = total_df["CTRT_DAY"].dt.month

    selected_type = st.sidebar.selectbox("주거형태별", sorted(total_df["BLDG_USG"].unique()))
    selected_month = st.sidebar.radio("확인하고 싶은 월을 선택하세요", ["1월", "2월", "3월"])
    month_dict = {'1월': 1, '2월': 2, '3월': 3}
    
    filtered_df = total_df[total_df['BLDG_USG'] == selected_type]
    filtered_month = filtered_df[filtered_df['month'] == month_dict[selected_month]]

    # Define columns for display
    columns = ["CGG_NM", "STDG_NM", "BLDG_NM", "ARCH_AREA", "THING_AMT"]
    sorted_df = filtered_month[columns]

    with col[0]:
        st.subheader(f"2025년 {month_dict[selected_month]}월 서울시 {selected_type} 평균가격")
        showMap(filtered_month, month_dict[selected_month])

        # Rename columns for display
        sorted_df_renamed = sorted_df.rename(columns={
            'CGG_NM': '자치구',
            'STDG_NM': '동',
            'BLDG_NM': '건물명',
            'ARCH_AREA': '면적 (㎡)',
            'THING_AMT': '가격 (만원)'
        })

        # Show top 3 and bottom 3 prices
        st.markdown(f"#### 🏠 {selected_month} {selected_type} 가격 상위 3개")
        st.dataframe(sorted_df_renamed.sort_values(by='가격 (만원)', ascending=False).head(3).reset_index(drop=True))

        st.markdown(f"#### 🏠 {selected_month} {selected_type} 가격 하위 3개")
        st.dataframe(sorted_df_renamed.sort_values(by='가격 (만원)', ascending=True).head(3).reset_index(drop=True))

    with col[1]:
        st.subheader('')
        cgg_nm = st.selectbox("자치구", sorted(filtered_month["CGG_NM"].unique()))
        st.markdown(f'#### {cgg_nm} {selected_month} {selected_type} 가격 개요')

        col1, col2 = st.columns(2)

        # Calculate the average max and min price per district
        avg_max_price = filtered_month.groupby("CGG_NM")['THING_AMT'].max().mean()
        avg_min_price = filtered_month.groupby("CGG_NM")['THING_AMT'].min().mean()

        # Filter the data by selected district
        filtered_cgg_nm = filtered_month[filtered_month['CGG_NM'] == cgg_nm]

        # Drop NaN values and calculate min and max price
        filtered_cgg_nm = filtered_cgg_nm.dropna(subset=['THING_AMT'])  
        min_price = filtered_cgg_nm['THING_AMT'].min()
        max_price = filtered_cgg_nm['THING_AMT'].max()

        # Calculate the difference between the max/min price and the average
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
        
        filtered_cgg_nm = filtered_cgg_nm[columns]
        filtered_cgg_nm_renamed = filtered_cgg_nm.rename(columns={
            'CGG_NM': '자치구',
            'STDG_NM': '동',
            'BLDG_NM': '건물명',
            'ARCH_AREA': '면적 (㎡)',
            'THING_AMT': '가격 (만원)'
        })

        # Show top 5 and bottom 5 prices for selected district
        st.markdown(f"#### 🏠 {cgg_nm} {selected_type} 가격 상위 5개")
        st.dataframe(filtered_cgg_nm_renamed.sort_values(by='가격 (만원)', ascending=False).head(5).reset_index(drop=True))

        st.markdown(f"#### 🏠 {cgg_nm} {selected_type} 가격 하위 5개")
        st.dataframe(filtered_cgg_nm_renamed.sort_values(by='가격 (만원)', ascending=True).head(5).reset_index(drop=True))

    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption("출처 : [서울시 부동산 실거래가 정보](https://data.seoul.go.kr/dataList/OA-21275/S/1/datasetView.do)")