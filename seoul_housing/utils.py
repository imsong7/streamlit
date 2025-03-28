# -*- coding:utf-8 -*-

import streamlit as st
import pandas as pd

# 데이터 캐싱 함수로, 데이터 불러오기 이후 메모리에 저장
@st.cache_data
def load_data():
    data =pd.read_csv('data/seoul_real_estate.csv')

    return data