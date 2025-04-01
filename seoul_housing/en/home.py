# -*- coding:utf-8 -*-

import pandas as pd
import streamlit as st
from utils import load_data
from millify import prettify
from en.map import showMap

def run_home(total_df):
    st.markdown("## Dashboard Overview \n"
                "This project provides a dashboard displaying real estate transaction prices in Seoul for the year 2025.")

    col = st.columns((2, 2), gap='medium')

    total_df["CTRT_DAY"] = pd.to_datetime(total_df["CTRT_DAY"].astype(str), format="%Y-%m-%d")
    total_df["month"] = total_df["CTRT_DAY"].dt.month

    selected_type = st.sidebar.selectbox("Select Housing Type", sorted(total_df["BLDG_USG"].unique()))
    selected_month = st.sidebar.radio("Select the month to check", ["January", "February", "March"])
    month_dict = {'January': 1, 'February': 2, 'March': 3}
    
    filtered_df = total_df[total_df['BLDG_USG'] == selected_type]
    filtered_month = filtered_df[filtered_df['month'] == month_dict[selected_month]]

    # Define columns for display
    columns = ["CGG_NM_EN", "STDG_NM", "BLDG_NM", "ARCH_AREA", "THING_AMT"]
    sorted_df = filtered_month[columns]

    with col[0]:
        st.markdown(f"#### 2025 <u>{selected_month}</u> Average Price of <u>{selected_type}</u> in Seoul", unsafe_allow_html=True)
        showMap(filtered_month, month_dict[selected_month])

        # Rename columns for display
        sorted_df_renamed = sorted_df.rename(columns={
            'CGG_NM_EN': 'District',
            'STDG_NM': 'Neighborhood',
            'BLDG_NM': 'Building Name',
            'ARCH_AREA': 'Area (㎡)',
            'THING_AMT': 'Price (10K KRW)'
        })

        # Show top 3 and bottom 3 prices
        st.markdown(f"#### 🏠 Top 3 {selected_type} Prices")
        st.dataframe(sorted_df_renamed.sort_values(by='Price (10K KRW)', ascending=False).head(3).reset_index(drop=True))

        st.markdown(f"#### 🏠 Bottom 3 {selected_type} Prices")
        st.dataframe(sorted_df_renamed.sort_values(by='Price (10K KRW)', ascending=True).head(3).reset_index(drop=True))

    with col[1]:
        st.subheader('')
        cgg_nm_en = st.selectbox("Select District", sorted(filtered_month["CGG_NM_EN"].unique()))
        st.markdown(f'#### <u>{cgg_nm_en}</u> {selected_month} {selected_type} Price Overview', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        # Calculate the average max and min price per district
        avg_max_price = filtered_month.groupby("CGG_NM_EN")['THING_AMT'].max().mean()
        avg_min_price = filtered_month.groupby("CGG_NM_EN")['THING_AMT'].min().mean()

        # Filter the data by selected district
        filtered_cgg_nm = filtered_month[filtered_month['CGG_NM_EN'] == cgg_nm_en]

        # Drop NaN values and calculate min and max price
        filtered_cgg_nm = filtered_cgg_nm.dropna(subset=['THING_AMT'])  
        min_price = filtered_cgg_nm['THING_AMT'].min()
        max_price = filtered_cgg_nm['THING_AMT'].max()

        # Calculate the difference between the max/min price and the average
        max_delta = max_price - avg_max_price
        min_delta = min_price - avg_min_price

        with col1:
            st.metric(
                label=f"Minimum Price (10K KRW)", 
                value=f"{min_price:,.0f}", 
                delta=f"{min_delta:,.0f} (10K KRW)"
            )

        with col2:
            st.metric(
                label=f"Maximum Price (10K KRW)", 
                value=f"{max_price:,.0f}", 
                delta=f"{max_delta:,.0f} (10K KRW)"
            )
        
        filtered_cgg_nm = filtered_cgg_nm[columns]
        filtered_cgg_nm_renamed = filtered_cgg_nm.rename(columns={
            'CGG_NM_EN': 'District',
            'STDG_NM': 'Neighborhood',
            'BLDG_NM': 'Building Name',
            'ARCH_AREA': 'Area (㎡)',
            'THING_AMT': 'Price (10K KRW)'
        })

        # Show top 5 and bottom 5 prices for selected district
        st.markdown(f"#### 🏠 Top 5 {selected_type} Prices")
        st.dataframe(filtered_cgg_nm_renamed.sort_values(by='Price (10K KRW)', ascending=False).head(5).reset_index(drop=True))

        st.markdown(f"#### 🏠 Bottom 5 {selected_type} Prices")
        st.dataframe(filtered_cgg_nm_renamed.sort_values(by='Price (10K KRW)', ascending=True).head(5).reset_index(drop=True))

    st.markdown("<hr>", unsafe_allow_html=True)
    st.caption("Source: [Seoul Real Estate Transaction Data](https://data.seoul.go.kr/dataList/OA-21275/S/1/datasetView.do)")
