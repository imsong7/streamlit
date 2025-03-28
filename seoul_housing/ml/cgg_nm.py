# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import json
from prophet.serialize import model_from_json

plt.rcParams['font.family'] = "NanumGothic"

@st.cache_resource ## 모델 불러오는 것
def load_models(cgg_nms):
    models = []
    for cgg_nm in cgg_nms:
        print(cgg_nm)
        with open(f'/Users/songsooyeoun/Desktop/git_test/streamlit/project1/ml/model/{cgg_nm}.model.json', 'r') as fin:
            model = model_from_json(json.load(fin))
        models.append(model)
    models
    return models

def predictDistrict(total_df):
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    cgg_nms = sorted(list(total_df['CGG_NM'].unique()))
    periods = int(st.number_input("향후 예측기간을 지정하세요(1일~30일)", min_value=1, max_value=30, step=1))

    models = load_models(cgg_nms)
    fig, ax = plt.subplots(figsize=(20,10), sharex=True, sharey=False, ncols=5, nrows=5)
    for i in range(len(cgg_nms)):  
        future = models[i].make_future_dataframe(periods=periods)
        forecast = models[i].predict(future)

        row, col = divmod(i, 5) 
        models[i].plot(forecast, ax=ax[row, col], uncertainty=True)

        ax[row, col].set_title(f"서울시 {cgg_nms[i]} 평균가격 예측 시나리오 {periods}일간")
        ax[row, col].set_xlabel("날짜")
        ax[row, col].set_ylabel("평균가격(만원)")
        
        for tick in ax[row, col].get_xticklabels():
            tick.set_rotation(30)

    fig.tight_layout()
    st.pyplot(fig)