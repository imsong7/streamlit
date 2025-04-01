# -*- coding:utf-8 -*-

import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from en.eda.viz import showViz
from en.eda.stat import showStat


def home():
    st.markdown("### 📈 Visualization Overview \n"
                "- Average price per household trend \n"
                "- Number of transactions per household trend \n"
                "- Average price by region (Bar Chart) \n")
    st.markdown("### 🔢 Statistics Overview \n"
                "- Hypothesis testing between two groups \n"
                "- Correlation analysis \n"
                "- Regression analysis \n")
   

def run_eda(total_df):
    total_df["CTRT_DAY"] = pd.to_datetime(total_df["CTRT_DAY"], format="%Y-%m-%d")
    st.markdown("## Exploratory Data Analysis Overview \n")
    
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