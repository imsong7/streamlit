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

def set_korean_font():
    font_path = os.path.join('Nanum_Gothic', 'NanumGothic-Regular.ttf')
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
    return font_prop

def predict_plot(total_df, types, periods):
    font_prop = set_korean_font()
    
    fig, ax = plt.subplots(figsize=(6,9), ncols=1, nrows=4)
    ax = ax.flatten()  
    
    for i in range(len(types)):
        model = Prophet()
        total_df2 = total_df.loc[total_df['BLDG_USG']==types[i], ['CTRT_DAY', 'THING_AMT']]
        result_df = total_df2.groupby('CTRT_DAY')['THING_AMT'].agg('mean').reset_index()
        result_df = result_df.rename(columns={'CTRT_DAY':'ds', 'THING_AMT':'y'})
        model.fit(result_df)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        model.plot(forecast, ax=ax[i], uncertainty=True)
        ax[i].set_title(f"{types[i]}", fontproperties=font_prop)
        ax[i].set_ylabel("평균가격(만원)", fontproperties=font_prop)
        ax[i].set_xlabel('')
        ax[i].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))
        ax[i].xaxis.set_major_locator(plt.matplotlib.dates.DayLocator(interval=7))
        plt.setp(ax[i].get_xticklabels(), rotation=45, ha='right', fontproperties=font_prop)        
        ax[i].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x)))

    return fig


@st.cache_resource ## 모델 불러오는 것
def load_models(cgg_nms):
    models = []
    for cgg_nm in cgg_nms:
        print(cgg_nm)
        with open(f'kr/ml/model/{cgg_nm}.model.json', 'r') as fin:
            model = model_from_json(json.load(fin))
        models.append(model)
    models
    return models

def predictDistrict(total_df, periods):
    st.markdown(f"#### 📍 자치구별 평균가격 예측 ({periods}일간)")
    font_prop = set_korean_font()
    cgg_nms = sorted(list(total_df['CGG_NM'].unique()))

    models = load_models(cgg_nms)
    fig, ax = plt.subplots(figsize=(30,20), sharey=False, ncols=5, nrows=5)
    y_min, y_max = float('inf'), float('-inf')
    for i in range(len(cgg_nms)):  
        future = models[i].make_future_dataframe(periods=periods)
        forecast = models[i].predict(future)

        y_min = min(y_min, forecast['yhat_lower'].min())
        y_max = max(y_max, forecast['yhat_upper'].max())

    for i in range(len(cgg_nms)):  
        future = models[i].make_future_dataframe(periods=periods)
        forecast = models[i].predict(future)

        row, col = divmod(i, 5) 
        models[i].plot(forecast, ax=ax[row, col], uncertainty=True)

        ax[row, col].set_title(f"{cgg_nms[i]}", fontproperties=font_prop, fontsize=18)
        ax[row, col].set_ylabel("평균가격(만원)", fontproperties=font_prop)
        ax[row, col].set_xlabel('')
        ax[row, col].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))
        ax[row, col].xaxis.set_major_locator(plt.matplotlib.dates.DayLocator(interval=7))
        plt.setp(ax[row, col].get_xticklabels(), rotation=45, ha='right', fontproperties=font_prop)
        
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
    st.markdown(f"#### 📍 주거형태별 평균가격 예측 ({periods}일간)")
    types = list(total_df['BLDG_USG'].unique())

    fig = predict_plot(total_df, types, periods)
    fig.tight_layout()
    st.pyplot(fig)

def predict(total_df):
    st.markdown(f"### 2025년 서울시 평균가격 예측")
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    periods = int(st.number_input("향후 예측기간을 지정하세요(1일~30일)", min_value=1, max_value=30, step=1))

    cols = st.columns((1, 2.2), gap='medium')
    with cols[0]:
        predictType(total_df, periods)
    with cols[1]:
        predictDistrict(total_df, periods)