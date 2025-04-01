# -*- coding:utf-8 -*-

import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

from en.ml.predict import predict
from en.ml.report import reportMain

def home():
    st.markdown("### ⚙️ Machine Learning Prediction Overview \n"
                "- Household Prediction Trend: Visualize predicted changes over time. \n"
                "- District-wise Prediction Trend: Analyze regional variations in predictions. \n"
                "- Algorithms Used: \n"
                "   + **Facebook Prophet**: A model effective for time series forecasting, automatically learning seasonality and trends. \n"
                "   + **Source**: https://arxiv.org/pdf/2303.01903")

def run_ml(total_df):
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    st.markdown("## Real Estate Prediction Overview \n")
    
    selected = option_menu(None, ["Home", "Prediction", "Report"],
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
    elif selected == 'Prediction':
        predict(total_df)   
        pass
    elif selected == 'Report':
        reportMain(total_df)
        pass
    else:
        pass
    