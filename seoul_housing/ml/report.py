# -*- coding:utf-8 -*-

import streamlit as st
import json
import os
from prophet.serialize import model_from_json
from prophet.plot import plot_plotly

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False, encoding='utf-8').encode('utf-8')  

def reportMain(total_df):
    cgg_nm = st.sidebar.selectbox("자치구", sorted(list(total_df['CGG_NM'].unique())))
    periods = st.sidebar.number_input("향후 예측기간을 지정하세요 (1일~30일)", min_value=1, max_value=30, step=1)

    model_path = f'/Users/songsooyeoun/Desktop/git_test/streamlit/project1/ml/model/{cgg_nm}.model.json'
    
    # ✅ Handle missing model file
    if not os.path.exists(model_path):
        st.error(f"🚨 오류: {cgg_nm} 모델 파일을 찾을 수 없습니다.")
        return

    with open(model_path, 'r') as fin:
        model = model_from_json(json.load(fin))
    
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)

    output = convert_df(forecast)
    st.sidebar.download_button(
        label="결과 다운로드 (CSV)",
        data=output,
        file_name=f"{cgg_nm}_아파트 평균값 예측_{periods}일간.csv",
        mime="text/csv"
    )

    fig = plot_plotly(model, forecast)
    fig.update_layout(
            title=f"{cgg_nm} 아파트 평균값 예측 {periods}일간",
            title_font=dict(size=20),
            xaxis_title="날짜",
            yaxis_title="아파트 평균값 (만원)",
            autosize=False,
            width=700,
            height=800
    )
    
    fig.update_yaxes(tickformat="000")
    st.plotly_chart(fig)

