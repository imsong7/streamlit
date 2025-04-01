# -*- coding:utf-8 -*-

import streamlit as st
import pandas as pd

@st.cache_data(ttl=3600, max_entries=5)
def load_data():
    data = pd.read_csv('us_election/data/1976-2020-president.csv')
    return data