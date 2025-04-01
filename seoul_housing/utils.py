# -*- coding:utf-8 -*-

import streamlit as st
import pandas as pd

# 데이터 캐싱 함수로, 데이터 불러오기 이후 메모리에 저장
@st.cache_data(ttl=3600, max_entries=5)
def load_data(lang):
    if lang == 'English':
        file_path = 'data/seoul_real_estate_en.csv'
    else:
        file_path = 'data/seoul_real_estate.csv'
    data = pd.read_csv(file_path)
    return data