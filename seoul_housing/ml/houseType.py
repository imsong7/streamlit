# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from prophet import Prophet
import matplotlib.font_manager as fm
import matplotlib.ticker as ticker
import os

# 한글 폰트 설정
def set_korean_font():
    font_path = os.path.join('seoul_housing', 'Nanum_Gothic', 'NanumGothic-Regular.ttf')
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
    return font_prop

def predict_plot(total_df, types, periods):
    # 한글 폰트 설정 적용
    font_prop = set_korean_font()
    
    fig, ax = plt.subplots(figsize=(10,6), sharex=True, ncols=2, nrows=2)
    for i in range(0, len(types)):
        model = Prophet()
        total_df2 = total_df.loc[total_df['BLDG_USG']==types[i], ['CTRT_DAY', 'THING_AMT']]
        result_df = total_df2.groupby('CTRT_DAY')['THING_AMT'].agg('mean').reset_index()
        result_df = result_df.rename(columns={'CTRT_DAY':'ds', 'THING_AMT':'y'})
        model.fit(result_df)
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)

        row, col = divmod(i, 2)
        model.plot(forecast, ax=ax[row, col], uncertainty=True)

        # 타이틀, 라벨에 한글 폰트 적용
        ax[row, col].set_title(f"서울시 {types[i]} 평균가격 예측 시나리오 {periods}일간", fontproperties=font_prop)
        ax[row, col].set_ylabel("평균가격(만원)", fontproperties=font_prop)
        ax[row, col].set_xlabel('')
        for tick in ax[row, col].get_xticklabels():
            tick.set_rotation(30)
        
        ax[row, col].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%m-%d'))
        ax[row, col].xaxis.set_major_locator(plt.matplotlib.dates.DayLocator(interval=7))
        plt.setp(ax[row, col].get_xticklabels(), rotation=45, ha='right', fontproperties=font_prop)        
        ax[row, col].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: '{:,.0f}'.format(x)))

    return fig

def predictType(total_df):
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    types = list(total_df['BLDG_USG'].unique())
    periods = int(st.number_input("향후 예측기간을 지정하세요(1일~30일)", min_value=1, max_value=30, step=1))
    st.markdown(f"### 2025년 서울시 주거형태별 평균가격 예측 {periods}일간 ")

    fig = predict_plot(total_df, types, periods)
    fig.tight_layout()
    st.pyplot(fig)
    st.markdown("<hr>", unsafe_allow_html=True)