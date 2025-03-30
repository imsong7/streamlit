# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from prophet.serialize import model_from_json

@st.cache_resource  # 모델 불러오는 것
def load_models(cgg_nms):
    models = []
    for cgg_nm in cgg_nms:
        print(cgg_nm)
        with open(f'seoul_housing/ml/model/{cgg_nm}.model.json', 'r') as fin:
            model = model_from_json(json.load(fin))
        models.append(model)
    return models

def predictDistrict(total_df):
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    cgg_nms = sorted(list(total_df['CGG_NM'].unique()))
    periods = int(st.number_input("향후 예측기간을 지정하세요(1일~30일)", min_value=1, max_value=30, step=1))

    models = load_models(cgg_nms)
    
    fig = make_subplots(
        rows=5, cols=5, 
        subplot_titles=[f"{cgg_nms[i]} 평균가격 예측 시나리오" for i in range(len(cgg_nms))],
        vertical_spacing=0.1,  horizontal_spacing=0.02
    )
    
    # To calculate the global Y-axis range
    all_yhat = []
    
    for i in range(len(cgg_nms)):  
        future = models[i].make_future_dataframe(periods=periods)
        forecast = models[i].predict(future)

        row, col = divmod(i, 5)

        # Collect all yhat values for determining the Y-axis range
        all_yhat.extend(forecast['yhat'])
        
        # Add trace for the forecast (yhat) to the appropriate subplot
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat'],
            mode='lines',
            name=f"서울시 {cgg_nms[i]} 평균가격 예측",
            line=dict(width=2)
        ), row=row+1, col=col+1)

        # Add uncertainty (yhat_upper, yhat_lower)
        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_upper'],
            mode='lines',
            name=f"상한선: {cgg_nms[i]}",
            line=dict(width=0.5, color='gray', dash='dash'),
            fill='tonexty',
            fillcolor='rgba(0,100,80,0.2)'
        ), row=row+1, col=col+1)

        fig.add_trace(go.Scatter(
            x=forecast['ds'],
            y=forecast['yhat_lower'],
            mode='lines',
            name=f"하한선: {cgg_nms[i]}",
            line=dict(width=0.5, color='gray', dash='dash'),
            fill='tonexty',
            fillcolor='rgba(0,100,80,0.2)'
        ), row=row+1, col=col+1)
    
    # Get the global min and max of yhat values to set the Y-axis range
    yhat_min = min(all_yhat)
    yhat_max = max(all_yhat)

    # Update layout for the subplots and titles
    fig.update_layout(
        title=f"2025년 서울시 평균가격 예측 ({periods}일간)",
        title_font=dict(size=20),
        autosize=False,
        width=1800,  # Increased width
        height=1000,  # Increased height
        showlegend=False
    )

    # Rotate x-axis labels for readability and set consistent x-axis ticks
    fig.update_xaxes(tickfont=dict(size=8), row=1, col=1)

    # Update x-axis format to '%m월 %d일' for all subplots
    for i in range(1, 6):
        for j in range(1, 6):
            fig.update_xaxes(
                row=i, col=j, 
                title_font=dict(size=8), 
                tickfont=dict(size=8),
                tickformat='%b, %d'  # Ensure the date format is 'Feb, 23'
            )
            # Only show y-axis labels on the first column (column 1)
            if j != 1:
                fig.update_yaxes(showticklabels=False, row=i, col=j)  # Hide y-axis labels for other columns
            else:
                fig.update_yaxes(
                    title_text="평균가격 (만원)", 
                    title_font=dict(size=8), 
                    tickfont=dict(size=8), 
                    row=i, col=j,
                    range=[yhat_min, yhat_max]  # Set the consistent Y-axis range
                )
    
    # Update font size for subplot titles
    for i in range(len(cgg_nms)):
        row, col = divmod(i, 5)
        fig.layout.annotations[i].update(font=dict(size=8))  # Set font size for subplot titles
    
    # Show the plot in Streamlit
    st.plotly_chart(fig)
