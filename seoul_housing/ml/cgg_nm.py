# -*- coding:utf-8 -*-

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import json
import os
import matplotlib.font_manager as fm
from prophet.serialize import model_from_json

# 한글 폰트 설정
def set_korean_font():
    font_path = os.path.join('seoul_housing', 'Nanum_Gothic', 'NanumGothic-Regular.ttf')
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
    return font_prop


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
    font_prop = set_korean_font()

    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    cgg_nms = sorted(list(total_df['CGG_NM'].unique()))
    periods = int(st.number_input("향후 예측기간을 지정하세요(1일~30일)", min_value=1, max_value=30, step=1))

    models = load_models(cgg_nms)
    fig, ax = plt.subplots(figsize=(20,10) sharey=False, ncols=5, nrows=5)
    for i in range(len(cgg_nms)):  
        future = models[i].make_future_dataframe(periods=periods)
        forecast = models[i].predict(future)

        row, col = divmod(i, 5) 
        models[i].plot(forecast, ax=ax[row, col], uncertainty=True)

        ax[row, col].set_title(f"{cgg_nms[i]} 평균가격 예측", fontproperties=font_prop)
        ax[row, col].set_xlabel("날짜", fontproperties=font_prop)
        ax[row, col].set_ylabel("평균가격(만원)", fontproperties=font_prop)
        
        # 날짜 형식 설정 - '2025-02-11' 형식으로 표시
        ax[row, col].xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d'))
        
        # x축 레이블 설정
        plt.setp(ax[row, col].get_xticklabels(), rotation=45, ha='right', fontproperties=font_prop)
        
        # x축 틱 개수 조정 (너무 많으면 겹칠 수 있으므로)
        ax[row, col].xaxis.set_major_locator(plt.matplotlib.dates.MonthLocator())
        
        # 그리드 추가하여 가독성 향상
        ax[row, col].grid(True, alpha=0.3)
    
    # 서브플롯 간격 조정으로 레이블이 잘리지 않도록 함
    plt.subplots_adjust(bottom=0.15, hspace=0.5, wspace=0.3)
    
    # 중복 tight_layout 호출 제거
    fig.tight_layout()
    st.pyplot(fig)