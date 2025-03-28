# -*- coding:utf-8 -*-

import pandas as pd
import numpy as np

import pingouin as pg
from pingouin import ttest

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px


import streamlit as st

plt.rcParams['font.family'] = "NanumGothic"

def twoMeans(total_df):
    total_df['month'] = total_df['CTRT_DAY'].dt.month
    apt_df = total_df[(total_df['BLDG_USG'] == '아파트') & (total_df['month'].isin([2, 3]))]
    st.markdown("### 집계 \n"
                "- 2월 3월의 아파트 가격을 비교한다.")
    ttest_df = round(apt_df.groupby('month')['THING_AMT'].agg(['mean', 'std', 'size']), 1)
    st.dataframe(ttest_df, use_container_width=True)

    st.markdown("### 서울시 통합 2월 vs 3월 차이 검정 \n"
                "- 2월과 3월의 아파트 평균 가격의 차이를 검정한다. \n"
                "- 가설설정 \n"
                "  + 귀무가설 : $H_{0}$: 2월과 3월의 아파트 평균 차이는 없다. \n"
                "  + 대립가설 : $H_{1}$: 2월과 3월의 아파트 평균 차이는 있다. \n")
    
    feb_df = apt_df[apt_df['month']==2]
    mar_df = apt_df[apt_df['month']==3]
    result = ttest(feb_df['THING_AMT'], mar_df['THING_AMT'], paired=False)
    st.dataframe(result, use_container_width=True)
    st.markdown(f"- 확인결과 p-value 값이 {result['p-val'].values[0]} 이므로 $H_{0}$을 채택하여, 2월과 3월의 아파트 평균 차이는 없다.")

    selected_cgg_nm = st.sidebar.selectbox("자치구명", sorted(total_df["CGG_NM"].unique()))
    st.markdown(f"### 서울시 {selected_cgg_nm} 2월 vs 3월 차이 검정 \n"
                "- 자치구를 선택하여 2월과 3월의 아파트 평균 차이가 있는지 확인하도록 한다.")

    cgg_df = apt_df[apt_df['CGG_NM']==selected_cgg_nm]
    cgg_feb_df = cgg_df[cgg_df['month']==2]
    cgg_mar_df = cgg_df[cgg_df['month']==3]
    cgg_result = ttest(cgg_feb_df['THING_AMT'], cgg_mar_df['THING_AMT'], paired=False)
    st.dataframe(cgg_result, use_container_width=True)
    if cgg_result['p-val'].values[0] > 0.05:
        st.markdown(f"- 확인결과 p-value 값이 {cgg_result['p-val'].values[0]} 이므로 $H_{0}$을 채택하여, 2월과 3월의 아파트 평균 차이는 없다.") # 귀무가설
    else:
        st.markdown(f"- 확인결과 p-value 값이 {cgg_result['p-val'].values[0]} 이므로 $H_{1}$을 채택하여, 2월과 3월의 아파트 평균 차이는 있다.") # 대립가설

    st.markdown(f"### 서울시 :Blue[{selected_cgg_nm}] 2월 vs 3월 시각화", unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(10,3))
    sns.pointplot(x='month', y='THING_AMT', data=cgg_df)
    sns.despine()
    st.pyplot(fig)
    st.dataframe(round(cgg_df.groupby('month')['THING_AMT'].agg(['mean', 'std', 'size']), 1), use_container_width=True)

def corrRelation(total_df):
    total_df['month'] = total_df['CTRT_DAY'].dt.month
    apt_df = total_df[(total_df['BLDG_USG'] == '아파트') & (total_df['month'].isin([2, 3]))]
    st.markdown("### 상관관계 분석을 위한 데이터 확인 \n"
                "- 건물면적과 물건금액의 상관관계를 확인해보도록 한다. \n"
                "- 먼저 추출된 데이터를 확인한다.")
    corr_df = apt_df[['CTRT_DAY', 'THING_AMT', 'ARCH_AREA', 'CGG_NM', 'month']].reset_index(drop=True)
    st.dataframe(corr_df.head())

    st.markdown("### 상관관계 분석 시각화 \n"
                "- 상관관계 데이터 시각화를 진행한다. \n")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='ARCH_AREA', y='THING_AMT', data=corr_df, ax=ax)
    st.pyplot(fig)

    st.markdown("### 상관관계 계수 및 검정 \n"
                "- 계수를 확인한다. \n")
    seoul_coef = pg.corr(corr_df['ARCH_AREA'], corr_df['THING_AMT'])["r"].values[0] 
    st.dataframe(pg.corr(corr_df['ARCH_AREA'],  corr_df['THING_AMT']).round(3), use_container_width=True)
    st.markdown(f"- 상관계수는 {seoul_coef:.2f} 이며 건물면적이 증가할 때마다, 물건금액도 같이 증가하는 경향성을 나타나는 것을 확인하라 수 있다. \n"
                "그렇다면, 각 자치구별로 상관관계 시각화 및 상관계수는 어떻게 다른지 확인해본다. \n")
    selected_cgg_nm = st.sidebar.selectbox("자치구명", sorted(corr_df['CGG_NM'].unique()))
    selected_month = st.sidebar.selectbox("월", sorted(corr_df['month'].unique()))
    st.markdown(f"### 서울시 {selected_cgg_nm} {selected_month}월 아파트 가격 ~ 건물면적 상관관계 분석 \n"
                "- 각 자치구 및 월별 시각화 및 상관계수를 표시할 수 있다.")
    cgg_df = corr_df[(corr_df['CGG_NM']==selected_cgg_nm) & (corr_df['month']==selected_month)]
    corr_coef = pg.corr(cgg_df['ARCH_AREA'], cgg_df['THING_AMT'])
    st.dataframe(corr_coef, use_container_width=True)

    fig, ax = plt.subplots(figsize=(10,6))
    sns.scatterplot(x='ARCH_AREA', y='THING_AMT', data=cgg_df)
    ax.text(0.95, 0.05, f'Pearson Correlation: {corr_coef["r"].values[0]:.2f}',
            transform=ax.transAxes, ha='right', fontsize=12)
    ax.set_title(f'{selected_cgg_nm} 상관계수')
    st.pyplot(fig)

    st.markdown("### 거래건수 및 아파트 가격 상관관계")
    mean_size = cgg_df.groupby("CTRT_DAY")['THING_AMT'].agg(['mean', 'size'])
    corr_coef_df = pg.corr(mean_size['size'], mean_size['mean'])
    st.dataframe(corr_coef_df, use_container_width=True)

    fig, ax = plt.subplots(figsize=(10,6))
    sns.scatterplot(x='size', y='mean', data=mean_size)
    ax.text(0.95, 0.05, f'Pearson Correlation: {corr_coef["r"].values[0]:.2f}',
            transform=ax.transAxes, ha='right', fontsize=12)
    ax.set_title(f'{selected_cgg_nm} 상관계수')
    ax.set_xlabel("거래건수") 
    ax.set_ylabel("아파트 평균 가격")
    st.pyplot(fig)

def regRession(total_df):
    total_df['month'] = total_df['CTRT_DAY'].dt.month
    apt_df = total_df[(total_df['BLDG_USG'] == '아파트') & (total_df['month'].isin([2, 3]))]
    corr_df = apt_df[['CTRT_DAY', 'THING_AMT', 'ARCH_AREA', 'CGG_NM', 'month']].reset_index(drop=True)
    selected_cgg_nm = st.sidebar.selectbox("자치구명", sorted(corr_df['CGG_NM'].unique()))
    selected_month = st.sidebar.selectbox("월", sorted(corr_df['month'].unique()))
    reg_df = corr_df[(corr_df['CGG_NM']==selected_cgg_nm) & (corr_df['month']==selected_month)]
    st.markdown("### 데이터 확인")
    st.dataframe(reg_df, use_container_width=True)

    # 회귀식
    st.markdown("### 건물면적과 아파트가격 회귀분석 \n"
                "- 통계의 가정들이 맞는지 확인해보도록 한다. \n"
                "#### 정규성 검정 \n"
                "- 먼저 시각적으로 확인한다. 잔차의 정규성 검정한다.")
    mod1 = pg.linear_regression(reg_df['ARCH_AREA'], reg_df['THING_AMT'])
    res = mod1.residuals_
    res = pd.DataFrame(res, columns=['Residuals'])
    fig = px.histogram(res, x='Residuals')
    st.plotly_chart(fig)
    sw = pg.normality(res, method='shapiro')
    st.dataframe(sw, use_container_width=True)
    st.markdown("- 자치구명을 변경하면 통계적으로 유의하게 나온 것도 잇고, 그렇지 않은 곳도 있다. \n"
                "- 만약 p-value가 0.05보다 매우 작으면, 잔차의 정규성은 위반되었기 때문에, 여기에서는 통상적인 회귀의 결괏값을 해석할 필요가 없다. \n"
                "- 이런 경우, 극단적인 이상치를 제거해야 하는 과정이 필요하다.")
            
    st.markdown("#### 회귀모형 확인 \n"
                "- 결정계수 $R^2$와 p-value를 확인한다.")
    st.dataframe(mod1.round(2), use_container_width=True)
    intercept, slope = mod1['coef'].values[0], mod1['coef'].values[1]
    st.write("상수:", intercept, "기울기:", slope)

    fig, ax = plt.subplots(figsize=(10,6))
    x = np.linspace(0, reg_df['ARCH_AREA'].max())

    sns.scatterplot(data=reg_df, x='ARCH_AREA', y='THING_AMT', ax=ax)
    ax.set_title("The best-fitting regression line")
    ax.set_xlabel("건물면적")
    ax.set_ylabel("아파트거래가격(만원)")
    ax.plot(x, slope*x + intercept)

    if intercept < 0:
        equation_line = f'$Y={slope:.1f}X{intercept:.1f}, R^2={np.round(mod1["adj_r2"].values[0], 3)}$'
    else:
        equation_line = f'$Y={slope:.1f}X+{intercept:.1f}, R^2={np.round(mod1["adj_r2"].values[0], 3)}$'\
        
    ax.text(0.95, 0.05, equation_line, transform=ax.transAxes, ha='right', fontsize=12)
    st.pyplot(fig)
    
    
def showStat(total_df):
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    selected = st.sidebar.selectbox("분석 메뉴", ['두 집단간 차이 검정', '상관분석', '회귀분석'])
    if selected == '두 집단간 차이 검정':
        st.markdown("### 두 집단간 차이 검정 이론 설명 \n"
                    "- t-검정은 두 개의 독립적인 데이터 샘플의 평균 간에 유의미한 차이가 있는지 확인하는데 사용할 수 있는 통계 테스트입니다. \n")
        st.markdown("t-통계량을 구하는 것은 아래와 같습니다.")
        st.latex(r'''
        t = \frac{{\bar{X} - \mu}}{{s/\sqrt{n}}}
        ''')
        st.markdown("- $\={X}$ : 표본의 평균을 말합니다. \n"
                    "...")
        twoMeans(total_df)
    elif selected == "상관분석":
        st.markdown("### 상관분석 이론 설명 \n"
                    "- 피어슨 상관계수 ... \n"
                    "- 스피어만 상관계수 ... \n")
        corrRelation(total_df)
    elif selected == "회귀분석":
        st.markdown("### 회귀분석 이론 설명 \n"
                     "회귀식의 가정 \n"
                     "회귀식의 가설 \n")
        regRession(total_df)
    else:
        st.warning("Wrong")
                        