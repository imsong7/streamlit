# -*- coding:utf-8 -*-

import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600, max_entries=5)
def load_data(lang):
    if lang == 'English':
        file_path = 'seoul_housing/data/seoul_real_estate_en.csv'
    else:
        file_path = 'seoul_housing/data/seoul_real_estate.csv'
    data = pd.read_csv(file_path)
    return data