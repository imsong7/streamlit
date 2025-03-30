# -*- coding:utf-8 -*-

import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

from ml.houseType import predictType
from ml.cgg_nm import predictDistrict
from ml.report import reportMain

st.set_page_config(
    page_title="ML 분석 페이지",  
    layout="wide",  # 전체 너비 설정되지만, CSS로 제한
    initial_sidebar_state="expanded" 
)

# 🔽 본문 너비 제한 (1000px 이하로 조정)
st.markdown(
    """
    <style>
    .main {
        max-width: 1000px;  /* 최대 너비 제한 */
        margin: 0 auto;  /* 가운데 정렬 */
    }
    </style>
    """,
    unsafe_allow_html=True
)

def home():
    st.markdown("### ⚙️ 머신러닝 예측 개요 \n"
            "- 가구당 예측 그래프 추세: 가구당 예측 결과를 시간에 따라 시각화하여 예측된 변화 추이를 확인합니다. \n"
            "- 자치구역별 예측 그래프 추세: 각 자치구별 예측 결과를 시각화하여 지역별 변화를 분석합니다. \n"
            "- 사용된 알고리즘 소개: \n"
            "   + **Facebook Prophet** 알고리즘: 시계열 예측에 효과적인 모델로, 계절성과 트렌드를 자동으로 학습하고 예측합니다. \n"
            "   + **출처**: https://arxiv.org/pdf/2303.01903")


def run_ml(total_df):
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    st.markdown("## 머신러닝 예측 개요 \n")

    selected = option_menu(None, ["Home", "주거형태별", "자치구역별", "보고서"],
                                icons=['house','bar-chart','map'],
                                menu_icon='cast', default_index=0, orientation='horizontal',
                                styles = {
                                    "container":{'padding':'0!important', 'background-color':'#fafafa'},
                                    "icon": {"color":'orange', 'font-size':'25px'},
                                    'nav-link':{'font-size':'18px', 'text-align':'left', 'margin':'0px', '--hover-color':'#eee'},
                                    'nav-link-selected': {'background-color':'green'},
                                }
                            )
    
    if selected == 'Home':
        home()
    elif selected == '주거형태별':
        predictType(total_df)
        pass
    elif selected == '자치구역별':
        predictDistrict(total_df)
        pass
    elif selected == '보고서':
        reportMain(total_df)
        pass
    else:
        pass
    