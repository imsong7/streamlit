# -*- coding:utf-8 -*-

import streamlit as st
from streamlit_option_menu import option_menu
from home import run_home
from utils import load_data
from eda.eda_home import run_eda
from ml.ml_home import run_ml 

st.set_page_config(
    page_title="서울시 부동산 대시보드",  
    layout="wide", 
    initial_sidebar_state="expanded" 
)


def main():
    total_df = load_data()
    with st.sidebar:
        selected = option_menu("대시보드 메뉴", ['홈', '탐색적 분석', '부동산 예측'],
                                icons=['house', 'file-bar-graph', 'graph-up-arrow'], 
                                menu_icon="cast", 
                                default_index=0)
    
    if selected == "홈":
        run_home()
    elif selected == "탐색적 분석":
        run_eda(total_df)
    elif selected == "부동산 예측":
        run_ml(total_df)
    else:
        print("error..")

if __name__ == "__main__":
    main()