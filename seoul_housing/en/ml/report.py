# -*- coding:utf-8 -*-

import streamlit as st
import json
import os
import pandas as pd

from prophet.serialize import model_from_json
from prophet.plot import plot_plotly

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False, encoding='utf-8').encode('utf-8')  

def reportMain(total_df):
    cgg_nm = st.sidebar.selectbox("Select District", sorted(list(total_df['CGG_NM_EN'].unique())))
    periods = st.sidebar.number_input("Specify the forecast period (1 to 30 days)", min_value=1, max_value=30, step=1)

    model_path = f'en/ml/model/{cgg_nm}.model.json'
    
    if not os.path.exists(model_path):
        st.error(f"🚨 Error: Model file for {cgg_nm} not found.")
        return

    with open(model_path, 'r') as fin:
        model = model_from_json(json.load(fin))
    
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    output = convert_df(forecast)
    st.sidebar.download_button(
        label="Download Results (CSV)",
        data=output,
        file_name=f"{cgg_nm}_Apartment_Avg_Price_Forecast_{periods}_Days.csv",
        mime="text/csv"
    )

    forecast['ds'] = pd.to_datetime(forecast['ds'])
    
    end_date = forecast['ds'].max()
    start_date = end_date - pd.Timedelta(days=periods)
    future_data = forecast[forecast['ds'] > start_date]

    max_row = future_data.loc[future_data['yhat'].idxmax(), ['ds', 'yhat']]
    min_row = future_data.loc[future_data['yhat'].idxmin(), ['ds', 'yhat']]

    max_date = future_data.loc[future_data['yhat'].idxmax(), 'ds'].strftime('%m/%d')
    min_date = future_data.loc[future_data['yhat'].idxmin(), 'ds'].strftime('%m/%d')
    mean_yhat = future_data['yhat'].mean()

    start_date = start_date.strftime('%m/%d')
    end_date = end_date.strftime('%m/%d')
    st.markdown(f"### 📍 {cgg_nm} Apartment Price Forecast for the Next {periods} Days ({start_date} ~ {end_date})")
    st.markdown(f"#### The average price for the next {periods} days is <span style='color:green'>{mean_yhat:,.0f} (10K KRW)</span>", unsafe_allow_html=True)

    st.markdown(f"#### The highest price will be on {max_date} at <span style='color:red'>{max_row['yhat']:,.0f} (10K KRW)</span>, and the lowest price will be on {min_date} at <span style='color:blue'>{min_row['yhat']:,.0f} (10K KRW)</span>", unsafe_allow_html=True)

    fig = plot_plotly(model, forecast)
    fig.update_layout(
            title=f"{cgg_nm} Apartment Price Forecast ({periods} Days)",
            title_font=dict(size=20),
            xaxis_title="Date",
            yaxis_title="Apartment Average Price (10K KRW)",
            autosize=False,
            width=700,
            height=800
    )
    
    fig.update_yaxes(tickformat="000")
    st.plotly_chart(fig)
