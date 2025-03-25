# -*- coding: utf-8 -*- 

import streamlit as st

@st.cache_data
def calculate_sales_revenue(price, total_sales):
    revenue = price * total_sales
    return revenue

def main():
    st.title("Steamlit Button Widget")
    price = st.slider("단가:", 1000, 10000, value=5000)
    total_sales = st.slider("전체 판매 갯수:", 1, 1000, value=500)

    if st.button("매출액 계산"):
        revenue = calculate_sales_revenue(price, total_sales)
        st.write(revenue)


if __name__ == "__main__":
    main()