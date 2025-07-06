# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from prophet import Prophet
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
import os
import json
from prophet.serialize import model_from_json

def set_english_font():
    plt.rcParams['font.family'] = 'Arial'  
    plt.rcParams['axes.unicode_minus'] = False  

def predict_plot(total_df, types, periods):
    set_english_font()  
    
    fig, ax = plt.subplots(figsize=(6,9), ncols=1, nrows=4)
    ax = ax.flatten()  
    
    for i in range(len(types)):
        model = Prophet()
        total_df2 = total_df.loc[total_df['BLDG_USG'] == types[i], ['CTRT_DAY', 'THING_AMT']]
        result_df = total_df2.groupby('CTRT_DAY')['THING_AMT'].agg('mean').reset_index()
        result_df = result_df.rename(columns={'CTRT_DAY': 'ds', 'THING_AMT': 'y'})
        model.fit(result_df)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        model.plot(forecast, ax=ax[i], uncertainty=True)
        ax[i].set_title(f"{types[i]}")
        ax[i].set_ylabel("Average Price (10,000 won)")
        ax[i].set_xlabel('')
        ax[i].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))
        ax[i].xaxis.set_major_locator(plt.matplotlib.dates.DayLocator(interval=7))
        plt.setp(ax[i].get_xticklabels(), rotation=45, ha='right')        
        ax[i].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x)))

    return fig

@st.cache_resource  # Load model once
def load_models(cgg_cds):
    models = []
    for cgg_cd in cgg_cds:
        print(cgg_cd)
        with open(f'seoul_housing/en/ml/model/{cgg_cd}.model.json', 'r') as fin:
            model = model_from_json(json.load(fin))
        models.append(model)
    return models

def predictDistrict(total_df, periods):
    set_english_font() 
    st.markdown(f"#### 📍 District-wise Average Price Prediction ({periods} days)")
    cgg_cds = sorted(list(total_df['CGG_NM_EN'].unique()))

    models = load_models(cgg_cds)
    fig, ax = plt.subplots(figsize=(30, 20), sharey=False, ncols=5, nrows=5)
    y_min, y_max = float('inf'), float('-inf')
    
    for i in range(len(cgg_cds)):  
        future = models[i].make_future_dataframe(periods=periods)
        forecast = models[i].predict(future)

        y_min = min(y_min, forecast['yhat_lower'].min())
        y_max = max(y_max, forecast['yhat_upper'].max())

    for i in range(len(cgg_cds)):  
        future = models[i].make_future_dataframe(periods=periods)
        forecast = models[i].predict(future)

        row, col = divmod(i, 5) 
        models[i].plot(forecast, ax=ax[row, col], uncertainty=True)

        ax[row, col].set_title(f"{cgg_cds[i]}", fontsize=18)
        ax[row, col].set_ylabel("Average Price (10,000 won)")
        ax[row, col].set_xlabel('')
        ax[row, col].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m/%d'))
        ax[row, col].xaxis.set_major_locator(plt.matplotlib.dates.DayLocator(interval=7))
        plt.setp(ax[row, col].get_xticklabels(), rotation=45, ha='right')
        
        min_date = forecast['ds'].min()
        max_date = forecast['ds'].max()
        ax[row, col].set_xlim([min_date, max_date])

        ax[row, col].set_ylim([y_min, y_max])

        ax[row, col].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x)))
        ax[row, col].grid(True, alpha=0.3)

    plt.subplots_adjust(bottom=0.15, hspace=0.15, wspace=0.3)
    fig.tight_layout()
    st.pyplot(fig)

def predictType(total_df, periods):
    st.markdown(f"#### 📍 Housing Type-wise Average Price Prediction ({periods} days)")
    types = list(total_df['BLDG_USG'].unique())

    fig = predict_plot(total_df, types, periods)
    fig.tight_layout()
    st.pyplot(fig)

def predict(total_df):
    st.markdown(f"### 2025 Seoul Average Price Prediction")
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    periods = int(st.number_input("Specify prediction period (1 to 30 days)", min_value=1, max_value=30, step=1))

    cols = st.columns((1, 2.2), gap='medium')
    with cols[0]:
        predictType(total_df, periods)
    with cols[1]:
        predictDistrict(total_df, periods)
