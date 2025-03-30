# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from prophet.serialize import model_from_json

@st.cache_resource 
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
    
    fig = make_subplots(
        rows=5, cols=5, 
        subplot_titles=[f"{cgg}" for cgg in cgg_nms],
        vertical_spacing=0.1, horizontal_spacing=0.02
    )
    
    all_yhat = []
    
    for i, cgg_nm in enumerate(cgg_nms):
        row, col = divmod(i, 5)
        row += 1
        col += 1
        
        future = models[i].make_future_dataframe(periods=periods)
        forecast = models[i].predict(future)
        all_yhat.extend(forecast['yhat'])
        
        # Main prediction line
        fig.add_trace(
            go.Scatter(
                x=forecast['ds'], y=forecast['yhat'], mode='lines',
                name=f"서울시 {cgg_nm} 평균가격 예측", line=dict(width=2)
            ), row=row, col=col
        )
        
        # Upper bound
        fig.add_trace(
            go.Scatter(
                x=forecast['ds'], y=forecast['yhat_upper'], mode='lines',
                name=f"상한선: {cgg_nm}", line=dict(width=0.5, color='gray', dash='dash'),
                fill='tonexty', fillcolor='rgba(0,100,80,0.2)'
            ), row=row, col=col
        )
        
        # Lower bound
        fig.add_trace(
            go.Scatter(
                x=forecast['ds'], y=forecast['yhat_lower'], mode='lines',
                name=f"하한선: {cgg_nm}", line=dict(width=0.5, color='gray', dash='dash'),
                fill='tonexty', fillcolor='rgba(0,100,80,0.2)'
            ), row=row, col=col
        )
    
    # Set consistent y-axis range and format axes
    yhat_min, yhat_max = min(all_yhat), max(all_yhat)
    
    fig.update_layout(
        title=f"2025년 서울시 평균가격 예측 ({periods}일간)",
        title_font=dict(size=20),
        width=1800, height=1000,
        showlegend=False
    )
    
    # Update all axes at once
    fig.update_xaxes(
        tickfont=dict(size=8),
        tickformat='%m월 %d일'
    )
    
    # Set y-axis formatting
    for i in range(1, 6):
        for j in range(1, 6):
            if j != 1:
                fig.update_yaxes(showticklabels=False, row=i, col=j)
            else:
                fig.update_yaxes(
                    title_text="평균가격 (만원)",
                    title_font=dict(size=8),
                    tickfont=dict(size=8),
                    range=[yhat_min, yhat_max],
                    row=i, col=j
                )
    
    # Update annotation font sizes
    for i in range(len(cgg_nms)):
        fig.layout.annotations[i].update(font=dict(size=8))
        
    st.plotly_chart(fig)