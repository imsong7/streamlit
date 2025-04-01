# -*- coding:utf-8 -*-

import streamlit as st
from streamlit_option_menu import option_menu
from utils import load_data
import importlib

st.set_page_config(  
    layout="wide", 
    initial_sidebar_state="expanded" 
)


# Language selection
lang = st.sidebar.radio("Select Language", ["Korean", "English"])

# Language-specific modules and menu options
modules = {
    "Korean": {
        "menu_options": ["홈", "탐색적 분석", "부동산 예측"],
        "home_module": "seoul_housing.kr.home",
        "eda_module": "seoul_housing.kr.eda.eda_home",
        "ml_module": "seoul_housing.kr.ml.ml_home"
    },
    "English": {
        "menu_options": ["Home", "Exploratory Analysis", "Real Estate Prediction"],
        "home_module": "seoul_housing.en.home",
        "eda_module": "seoul_housing.en.eda.eda_home",
        "ml_module": "seoul_housing.en.ml.ml_home"
    }
}

# Load language-specific module paths and menu options
selected_lang = modules[lang]
menu_options, home_module_path, eda_module_path, ml_module_path = selected_lang.values()

home_module = importlib.import_module(home_module_path)
eda_module = importlib.import_module(eda_module_path)
ml_module = importlib.import_module(ml_module_path)

menu_icons = ['house', 'file-bar-graph', 'graph-up-arrow']

def main():
    try:
        total_df = load_data(lang)
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return

    selected = option_menu("Menu" if lang == "English" else "메뉴", 
                           menu_options, icons=menu_icons, menu_icon="cast", default_index=0)

    if selected == menu_options[0]:  # Home
        home_module.run_home(total_df)
    elif selected == menu_options[1]:  # EDA
        eda_module.run_eda(total_df)
    elif selected == menu_options[2]:  # ML
        ml_module.run_ml(total_df)
    else:
        st.warning("Invalid selection" if lang == "English" else "잘못된 선택입니다")

if __name__ == "__main__":
    main()
