# -*- coding:utf-8 -*-

import streamlit as st
from streamlit_option_menu import option_menu
from home import run_home
from utils import load_data
from ml.ml_home import run_ml 

st.set_page_config(
    page_title="US Election Dashboard",  
    layout="wide", 
    initial_sidebar_state="expanded" 
)


def main():
    total_df = load_data()
    with st.sidebar:
        selected = option_menu("Dashboard", ['Home', 'Election Predict'],
                                icons=['house', 'graph-up-arrow'], 
                                menu_icon="cast", 
                                default_index=0)
    
    if selected == "Home":
        run_home()
    elif selected == "Election Predict":
        run_ml(total_df)
    else:
        print("error..")

if __name__ == "__main__":
    main()