# -*- coding:utf-8 -*-

import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

from ml.houseType import predictType
from ml.cgg_nm import predictDistrict
from ml.report import reportMain

def home():
    st.markdown("### 머신러닝 예측 개요 \n"
                "- 가구당 예측 그래프 추세 \n"
                "- 자치구볍ㄹ 예측 그래프 추세 \n"
                "- 사용된 알고리즘 소개 \n"
                "   + Facebook Prophet 알고리즘 사용\n"
                "   + 출처 : hpp")

def run_ml(total_df):
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    st.markdown("## 머신러닝 예측 개요 \n"
                "머신러닝 에측 페이지입니다.")

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
    