# -*- coding:utf-8 -*-

import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from kr.eda.viz import showViz
from kr.eda.stat import showStat


def home():
    st.markdown("### 📈 Visualization 개요 \n"
    "- 가구당 평균 가격 추세 \n"
    "- 가구당 거래 건수 추세 \n"
    "- 지역별 평균 가격 막대 그래프 \n")
    st.markdown("### 🔢 Statistics 개요 \n"
                "- 두 집단간 차이 검정 \n"
                "- 상관분석 \n"
                "- 회귀분석 \n")

def run_eda(total_df):
    total_df["CTRT_DAY"] = pd.to_datetime(total_df["CTRT_DAY"], format="%Y-%m-%d")
    st.markdown("## 탐색적 자료 분석 개요 \n")
    
    selected = option_menu(None, ["Home", "Visualization", "Statistics"],
                                icons=['house', 'bar-chart', 'file-spreadsheet'],
                                menu_icon="cast", default_index=0, orientation="horizontal",
                                styles={
                                    "container": {"padding":"0!important", "background-color":"#fafafa"},
                                    "icon": {"color":"orange", "font-size":"25px"},
                                    "nav-link": {"font-size":"18px", "text-align":"left", "margin":"0px",
                                    "--hover-color":"#eee"},
                                    "nav-link-selected": {"background-color":"green"},
                                }
                            )
    
    if selected == "Home":
        home()
    elif selected == "Visualization":
        # st.title("Visualization")
        showViz(total_df)
    elif selected == "Statistics":
        # st.title("Statistics")
        showStat(total_df)
    else:
        st.warning("Wrong")
                        