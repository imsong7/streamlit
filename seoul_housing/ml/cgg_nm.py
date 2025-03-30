# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from prophet.serialize import model_from_json

@st.cache_resource ## 모델 불러오는 것
def load_models(cgg_nms):
    models = []
    for cgg_nm in cgg_nms:
        print(cgg_nm)
        with open(f'seoul_housing/ml/model/{cgg_nm}.model.json', 'r') as fin:
            model = model_from_json(json.load(fin))
        models.append(model)
    models
    return models

def predictDistrict(total_df):
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    cgg_nms = sorted(list(total_df['CGG_NM'].unique()))
    periods = int(st.number_input("향후 예측기간을 지정하세요(1일~30일)", min_value=1, max_value=30, step=1))

    models = load_models(cgg_nms)
    
    fig = go.Figure()

    for i in range(len(cgg_nms)):  
        future = models[i].make_future_dataframe(periods=periods)
        forecast = models[i].predict(future)

        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat'],
            mode='lines',
            name=f"서울시 {cgg_nms[i]} 평균가격 예측",
            line=dict(width=2)
        ))

        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_upper'],
            mode='lines',
            name=f"상한선: {cgg_nms[i]}",
            line=dict(width=0.5, color='gray', dash='dash'),
            fill='tonexty', 
            fillcolor='rgba(0,100,80,0.2)'
        ))
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_lower'],
            mode='lines',
            name=f"하한선: {cgg_nms[i]}",
            line=dict(width=0.5, color='gray', dash='dash'),
            fill='tonexty',
            fillcolor='rgba(0,100,80,0.2)'
        ))

    fig.update_layout(
        title=f"서울시 평균가격 예측 ({periods}일간)",
        title_font=dict(size=20),
        xaxis_title="날짜",
        yaxis_title="평균가격 (만원)",
        autosize=False,
        width=1000,
        height=600,
        template="plotly_dark",  
        showlegend=True
    )

    fig.update_xaxes(tickangle=45)

    st.plotly_chart(fig)