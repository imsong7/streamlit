# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
from prophet import Prophet

def predict_plot(total_df, types, periods):
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

        ax[row, col].set_title(f"서울시 {types[i]} 평균가격 예측 시나리오 {periods}일간")
        ax[row, col].set_xlabel("날짜")
        ax[row, col].set_ylabel("평균가격(만원)")
        for tick in ax[row, col].get_xticklabels():
            tick.set_rotation(30)
        
    return fig

def predictType(total_df):
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    types = list(total_df['BLDG_USG'].unique())
    periods = int(st.number_input("향후 예측기간을 지정하세요(1일~30일)", min_value=1, max_value=30, step=1))

    fig = predict_plot(total_df, types, periods)
    fig.tight_layout()
    st.pyplot(fig)
    st.markdown("<hr>", unsafe_allow_html=True)
