# -*- coding:utf-8 -*-

import streamlit as st
import pandas as pd
from plotly.subplots import make_subplots
import plotly.express as px

def meanChart(total_df, cgg_nm_en):
    st.markdown(f"### 📍  <u>{cgg_nm_en}</u> Average Price Trend by Household \n", unsafe_allow_html=True)
    filtered_df = total_df[total_df["CGG_NM_EN"] == cgg_nm_en]
    filtered_df = filtered_df[filtered_df["CTRT_DAY"].between("2025-02-01", "2025-03-30")]
    result = filtered_df.groupby(["CTRT_DAY", "BLDG_USG"])["THING_AMT"].agg('mean').reset_index()

    df1 = result[result["BLDG_USG"] == 'Apartment']
    df2 = result[result["BLDG_USG"] == 'Detached House']
    df3 = result[result["BLDG_USG"] == 'Officetel']
    df4 = result[result["BLDG_USG"] == 'Multiplex House']

    # Create subplots with 2 rows and 2 columns
    fig = make_subplots(rows=2, cols=2, shared_xaxes=True, 
                        subplot_titles=('Apartment', 'Detached House', 'Officetel', 'Multiplex House'),
                        horizontal_spacing=0.1)
    
    # Add line graphs to the subplots
    fig.add_trace(px.line(df1,
                          x='CTRT_DAY',
                          y='THING_AMT',
                          title='Apartment Transaction Price', markers=True).data[0], row=1, col=1)
    fig.add_trace(px.line(df2,
                          x='CTRT_DAY',
                          y='THING_AMT',
                          title='Detached House Transaction Price', markers=True).data[0], row=1, col=2)
    fig.add_trace(px.line(df3,
                          x='CTRT_DAY',
                          y='THING_AMT',
                          title='Officetel Transaction Price', markers=True).data[0], row=2, col=1)
    fig.add_trace(px.line(df4,
                          x='CTRT_DAY',
                          y='THING_AMT',
                          title='Multiplex House Transaction Price', markers=True).data[0], row=2, col=2)
    fig.update_layout(
        width=800,
        height=600, 
        showlegend=True,
        template='plotly_white'
    )

    # Display the figure
    st.plotly_chart(fig)

def cntChart(total_df, cgg_nm_en):
    st.markdown(f"### 📍 <u>{cgg_nm_en}</u> Transaction Count Trend by Household \n", unsafe_allow_html=True)
    filtered_df = total_df[total_df['CGG_NM_EN'] == cgg_nm_en]
    filtered_df = filtered_df[filtered_df["CTRT_DAY"].between("2025-02-01", "2025-03-30")]
    result = filtered_df.groupby(["CTRT_DAY", "BLDG_USG"])["THING_AMT"].count().reset_index().rename(columns={'THING_AMT':'Transaction Count'})

    df1 = result[result["BLDG_USG"] == 'Apartment']
    df2 = result[result["BLDG_USG"] == 'Detached House']
    df3 = result[result["BLDG_USG"] == 'Officetel']
    df4 = result[result["BLDG_USG"] == 'Multiplex House']

    # Create subplots with 2 rows and 2 columns
    fig = make_subplots(rows=2, cols=2, shared_xaxes=True, 
                        subplot_titles=('Apartment', 'Detached House', 'Officetel', 'Multiplex House'),
                        horizontal_spacing=0.1)
    
    # Add line graphs to the subplots
    fig.add_trace(px.line(df1,
                          x='CTRT_DAY',
                          y='Transaction Count',
                          title='Apartment Transaction Count', markers=True).data[0], row=1, col=1)
    fig.add_trace(px.line(df2,
                          x='CTRT_DAY',
                          y='Transaction Count',
                          title='Detached House Transaction Count', markers=True).data[0], row=1, col=2)
    fig.add_trace(px.line(df3,
                          x='CTRT_DAY',
                          y='Transaction Count',
                          title='Officetel Transaction Count', markers=True).data[0], row=2, col=1)
    fig.add_trace(px.line(df4,
                          x='CTRT_DAY',
                          y='Transaction Count',
                          title='Multiplex House Transaction Count', markers=True).data[0], row=2, col=2)
    fig.update_layout(
        width=800,
        height=600, 
        showlegend=True,
        template='plotly_white'
    )
    # Display the figure
    st.plotly_chart(fig)

def barChart(total_df):
    st.markdown("## Average Price by Region Bar Chart")
    month_selected = st.selectbox("Select Month", [1, 2, 3])
    house_selected = st.selectbox("Select Household Type", total_df['BLDG_USG'].unique())
    total_df['month'] = total_df['CTRT_DAY'].dt.month
    result = total_df[(total_df['month'] == month_selected) & (total_df['BLDG_USG'] == house_selected)]
    bar_df = result.groupby('CGG_NM_EN')['THING_AMT'].agg('mean').reset_index()

    df_sorted = bar_df.sort_values('THING_AMT', ascending=False)

    # Create the bar chart using Plotly Express
    fig = px.bar(df_sorted, x='CGG_NM_EN', y='THING_AMT')

    # Update layout
    fig.update_yaxes(tickformat=".0f",
                    title_text="Price (10K KRW)",
                    range=[0, df_sorted['THING_AMT'].max()])
    fig.update_layout(xaxis_title='District',
                      yaxis_title='Transaction Count')
    st.plotly_chart(fig)

def showViz(total_df):
    total_df["CTRT_DAY"] = pd.to_datetime(total_df["CTRT_DAY"], format="%Y-%m-%d")
    barChart(total_df)

    st.markdown("<hr>", unsafe_allow_html=True)
    cgg_nm_en = st.selectbox("Select District", sorted(total_df["CGG_NM_EN"].unique()))
    col = st.columns((2, 2), gap='medium')
    with col[0]:
        meanChart(total_df, cgg_nm_en)
    with col[1]:
        cntChart(total_df, cgg_nm_en)

        
