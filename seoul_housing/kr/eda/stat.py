# -*- coding:utf-8 -*-

import pandas as pd
import numpy as np
import os

import pingouin as pg
from pingouin import ttest

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import matplotlib.font_manager as fm


import streamlit as st

def set_korean_font():
    font_path = os.path.join('seoul_housing', 'Nanum_Gothic', 'NanumGothic-Regular.ttf')
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
    return font_prop

def twoMeans(total_df):
    font_prop = set_korean_font() 
    
    total_df['month'] = total_df['CTRT_DAY'].dt.month
    apt_df = total_df[(total_df['BLDG_USG'] == '아파트') & (total_df['month'].isin([1, 2, 3]))]
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📍 집계 \n"
                "2개의 월을 선택하여 아파트 가격을 비교한다.")
    
    # 두 개의 월을 선택하도록 함
    selected_months = st.multiselect(
        "비교하고 싶은 두 개의 월을 선택하세요", 
        options=[1, 2, 3], 
        default=[1, 2]
    )

    if len(selected_months) == 2:
        month1, month2 = selected_months
        st.markdown(f"#### {month1}월과 {month2}월 아파트 가격 비교")

        apt_df = total_df[(total_df['BLDG_USG'] == '아파트') & (total_df['month'].isin(selected_months))]
        month1_df = apt_df[apt_df['month'] == month1]
        month2_df = apt_df[apt_df['month'] == month2]

        ttest_df = round(apt_df.groupby('month')['THING_AMT'].agg(['mean', 'std', 'size']), 1)
        st.dataframe(ttest_df, use_container_width=True)
    
        st.markdown("<hr>", unsafe_allow_html=True)
        # 가설설정 강조
        st.markdown(f"""
        #### 서울시 통합 {month1}월 vs {month2}월 차이 검정  
        **{month1}월과 {month2}월의 아파트 평균 가격 차이를 통계적으로 검정합니다.**

        **가설 설정**  
        > **귀무가설 $H_0$**: {month1}월과 {month2}월의 아파트 평균 가격 차이는 **없다**.  
        > **대립가설 $H_1$**: {month1}월과 {month2}월의 아파트 평균 가격 차이는 **있다**.  
        """, unsafe_allow_html=True)

        # 통계결과 컬럼 설명
        st.markdown(""" 
        - **T**: t-통계량 (두 집단 평균 차이에 대한 검정값)<br>
        - **dof**: 자유도<br>
        - **p-val**: 유의확률 (0.05 미만이면 통계적으로 유의함)<br>
        - **CI95%**: 평균 차이에 대한 95% 신뢰구간<br>
        - **cohen-d**: 효과 크기 (0.2=작음, 0.5=중간, 0.8=큼)
        """, unsafe_allow_html=True)

        result = ttest(month1_df['THING_AMT'], month2_df['THING_AMT'], paired=False)
        pval = result['p-val'].values[0]

        selected_cols = ['T', 'dof', 'p-val', 'CI95%', 'cohen-d']
        st.dataframe(result[selected_cols], use_container_width=True)

        if pval > 0.05:
            st.markdown(
                f"확인 결과 p-value = <span style='color:red;'>{pval:.4f}</span> 으로, 유의수준 0.05보다 크므로 귀무가설을 기각할 수 없습니다.<br>"
                f"→ 따라서 <span style='color:red;'>{month1}월과 {month2}월의 아파트 평균 가격 차이는 통계적으로 유의하지 않습니다.</span>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"확인 결과 p-value = <span style='color:red;'>{pval:.4f}</span> 으로, 유의수준 0.05보다 작으므로 귀무가설을 기각합니다.<br>"
                f"→ 따라서 <span style='color:red;'>{month1}월과 {month2}월의 아파트 평균 가격 차이는 통계적으로 유의합니다.</span>",
                unsafe_allow_html=True
            )



        st.markdown("<hr>", unsafe_allow_html=True)
        selected_cgg_nm = st.selectbox("자치구명", sorted(total_df["CGG_NM"].unique()))
        cgg_df = apt_df[apt_df['CGG_NM']==selected_cgg_nm]
        cgg_month1 = cgg_df[cgg_df['month']==month1]
        cgg_month2 = cgg_df[cgg_df['month']==month2]
        
        st.markdown(f"#### {selected_cgg_nm} {month1}월 vs {month2}월 시각화", unsafe_allow_html=True)

        fig, ax = plt.subplots(figsize=(10, 3))
        sns.boxplot(x='month', y='THING_AMT', data=cgg_df, palette="pastel")
        sns.despine()
        ax.set_xlabel("월", fontproperties=font_prop, fontsize=12)
        ax.set_ylabel("아파트 거래가격(원)", fontproperties=font_prop, fontsize=12)
        st.pyplot(fig)

        # 월별 통계 요약
        summary_df = round(cgg_df.groupby('month')['THING_AMT'].agg(['mean', 'std', 'size']), 1)
        st.dataframe(summary_df, use_container_width=True)

        st.markdown(f"#### {selected_cgg_nm} {month1}월 vs {month2}월 차이 검정 \n")
        cgg_result = ttest(cgg_month1['THING_AMT'], cgg_month2['THING_AMT'], paired=False)
        st.dataframe(cgg_result[selected_cols], use_container_width=True)
        if cgg_result['p-val'].values[0] > 0.05:
            st.markdown(
                f"확인 결과 p-value = <span style='color:red;'>{cgg_result['p-val'].values[0]:.4f}</span> 으로, 유의수준 0.05보다 크므로 귀무가설을 기각할 수 없습니다. <br>"
                f"→ 따라서 <span style='color:red;'>{selected_cgg_nm}의 {month1}월과 {month2}월 아파트 평균 가격 차이는 통계적으로 유의하지 않습니다.</span>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"확인 결과 p-value = <span style='color:red;'>{cgg_result['p-val'].values[0]:.4f}</span> 으로, 유의수준 0.05보다 작으므로 귀무가설을 기각합니다. <br>"
                f"→ 따라서 <span style='color:red;'>{selected_cgg_nm}의 {month1}월과 {month2}월 아파트 평균 가격 차이는 통계적으로 유의합니다.</span>",
                unsafe_allow_html=True
            )

    else:
        st.warning("두 개의 월을 선택해주세요.")

def corrRelation(total_df):
    font_prop = set_korean_font() 
    
    total_df['month'] = total_df['CTRT_DAY'].dt.month
    apt_df = total_df[(total_df['BLDG_USG'] == '아파트') & (total_df['month'].isin([1, 2, 3]))]
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("#### 📍 데이터 확인 \n")
    corr_df = apt_df[['CTRT_DAY', 'CGG_NM', 'month', 'BLDG_NM', 'ARCH_AREA', 'THING_AMT']].reset_index(drop=True)
    cols = ['CTRT_DAY', 'CGG_NM', 'BLDG_NM', 'ARCH_AREA', 'THING_AMT']
    st.dataframe(corr_df[cols].head())

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"### 📍 아파트 가격 ~ 건물면적 상관관계 분석 \n")
        
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='ARCH_AREA', y='THING_AMT', data=corr_df, ax=ax)
    ax.set_title('상관관계', fontproperties=font_prop, fontsize=15)
    ax.set_xlabel('건물 면적', fontproperties=font_prop)
    ax.set_ylabel('아파트 거래가격(원)', fontproperties=font_prop)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

    corr_res = pg.corr(corr_df['ARCH_AREA'], corr_df['THING_AMT']).round(3)
    seoul_coef = corr_res["r"].values[0]
    st.markdown("""
    - **n**: 샘플 수 (관측치 개수)<br>
    - **r**: 피어슨 상관계수 (-1~1 사이 값으로, 1에 가까울수록 강한 양의 상관관계)<br>
    - **CI95%**: 상관계수의 95% 신뢰구간<br>
    - **pval**: 유의확률 (0.05 미만이면 통계적으로 유의함)<br>
    """, unsafe_allow_html=True)

    # 주요 컬럼만 선택
    corr_res_display = corr_res[['n', 'r', 'CI95%', 'p-val']]
    st.dataframe(corr_res_display, use_container_width=True)

    st.markdown(
        f"전체 서울시 데이터 기준으로 건물면적과 아파트 거래금액 간의 상관계수는 <span style='color:red'>{seoul_coef:.2f}</span>입니다. "
        "이는 건물면적이 증가할수록 아파트 가격도 함께 증가하는 경향이 있음을 의미합니다.<br><br>",
        unsafe_allow_html=True
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    selected_cgg_nm = st.selectbox("자치구명", sorted(corr_df['CGG_NM'].unique()))
    selected_month = st.selectbox("월", sorted(corr_df['month'].unique()))
    
    cgg_df = corr_df[(corr_df['CGG_NM']==selected_cgg_nm) & (corr_df['month']==selected_month)]
    corr_coef = pg.corr(cgg_df['ARCH_AREA'], cgg_df['THING_AMT'])
    corr_res_display = ['n', 'r', 'CI95%', 'p-val']
    st.dataframe(corr_coef[corr_res_display], use_container_width=True)

    fig, ax = plt.subplots(figsize=(10,6))
    sns.scatterplot(x='ARCH_AREA', y='THING_AMT', data=cgg_df)
    ax.text(0.95, 0.05, f'r = {corr_coef["r"].values[0]:.2f}',
            transform=ax.transAxes, ha='right', fontsize=12)
    ax.set_title('상관관계', fontproperties=font_prop, fontsize=15, weight='bold')
    ax.set_xlabel("건물 면적", fontproperties=font_prop, fontsize=12)
    ax.set_ylabel("아파트 거래가격(원)", fontproperties=font_prop, fontsize=12)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

def regRession(total_df):
    font_prop = set_korean_font() 
    
    total_df['month'] = total_df['CTRT_DAY'].dt.month
    apt_df = total_df[(total_df['BLDG_USG'] == '아파트') & (total_df['month'].isin([1, 2, 3]))]
    corr_df = apt_df[['CTRT_DAY', 'THING_AMT', 'BLDG_NM', 'ARCH_AREA', 'CGG_NM', 'month']].reset_index(drop=True)
    
    selected_cgg_nm = st.selectbox("자치구명", sorted(corr_df['CGG_NM'].unique()))
    selected_month = st.selectbox("월", sorted(corr_df['month'].unique()))
    reg_df = corr_df[(corr_df['CGG_NM'] == selected_cgg_nm) & (corr_df['month'] == selected_month)]
    cols = ['CTRT_DAY', 'BLDG_NM', 'THING_AMT', 'ARCH_AREA']
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📍 데이터 확인")
    st.dataframe(reg_df[cols], use_container_width=True)

    # 회귀식
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📍 건물면적과 아파트가격 회귀분석 \n"
                "통계의 가정들이 맞는지 확인해보도록 한다. \n")

    st.markdown("#### 1) 정규성 검정 \n"
                "시각적으로 잔차의 정규성을 확인한다. \n"
                "- 히스토그램에서 잔차가 종 모양(정규분포)인지 살펴본다. \n"
                "- 비대칭이 심하거나 한쪽으로 쏠린 모양이면 정규성 가정 위반 가능성이 있다.\n")

    # 회귀분석 수행 (Pingouin 사용)
    mod1 = pg.linear_regression(reg_df['ARCH_AREA'], reg_df['THING_AMT'])
    res = mod1.residuals_
    res = pd.DataFrame(res, columns=['Residuals'])

    # 잔차 히스토그램 그리기
    fig = px.histogram(res, x='Residuals')
    fig.update_layout(title_text='잔차(Residuals) 분포 히스토그램')
    st.plotly_chart(fig)

    st.markdown("""
    - **W**        : Shapiro-Wilk 검정 통계량 (1에 가까울수록 정규성 충족)
    - **pval**     : p-value (0.05 이상이면 정규성 만족)
    - **normal**   : 정규성 만족 여부 (True/False)
    """)

    # Shapiro-Wilk 정규성 검정
    sw = pg.normality(res, method='shapiro')
    st.dataframe(sw, use_container_width=True)



    st.markdown("#### 2) 회귀모형 확인 \n"
                "회귀모형의 적합도를 나타내는 결정계수($R^2$)와 회귀계수들의 유의성을 확인한다.\n"
                "- **r^2**: 모형이 종속변수 변동성을 얼마나 잘 설명하는지를 나타내는 지표로, 0~1 사이 값이다. 1에 가까울수록 모형 설명력이 좋다.\n"
                "- **coef**: 회귀계수 (각 독립변수가 종속변수에 미치는 영향력 크기)\n"
                "- **se**: 표준오차 (회귀계수의 추정 정확도를 나타냄)\n"
                "- **t**: t-통계량 (회귀계수의 유의성 검정 통계값)\n")

    # 필요한 컬럼만 선택해서 출력
    cols_to_show = ['names', 'coef', 'se', 'T', 'pval', 'r2', 'adj_r2']
    st.dataframe(mod1[cols_to_show].round(4), use_container_width=True)

    # 계수 소수점 4자리 반올림
    intercept, slope = round(mod1['coef'].values[0], 4), round(mod1['coef'].values[1], 4)
    
    # 산점도 및 회귀선 그리기
    fig, ax = plt.subplots(figsize=(10,6))
    x = np.linspace(0, reg_df['ARCH_AREA'].max())

    sns.scatterplot(data=reg_df, x='ARCH_AREA', y='THING_AMT', ax=ax)
    ax.set_title("건물면적과 아파트 거래가격 간의 회귀선", fontproperties=font_prop, fontsize=15, weight='bold')
    ax.set_xlabel("건물면적", fontproperties=font_prop, fontsize=12)
    ax.set_ylabel("아파트 거래가격(원)", fontproperties=font_prop, fontsize=12)
    ax.plot(x, slope*x + intercept, color='red')  # 회귀선
    ax.grid(True, alpha=0.3)
    
    # 해석 문장
    slope_text = f"건물면적이 1㎡ 증가할 때 아파트 가격은 평균적으로 약 <span style='color:red;'>{slope}만 원</span> 증가합니다."
    st.markdown("#### 회귀계수 해석")
    st.markdown(slope_text, unsafe_allow_html=True)


    # 회귀방정식 및 결정계수 텍스트 표시
    adj_r2 = np.round(mod1["adj_r2"].values[0], 3)
    if intercept < 0:
        equation_line = f'$Y = {slope:.4f}X {intercept:.4f}, \\ R^2 = {adj_r2}$'
    else:
        equation_line = f'$Y = {slope:.4f}X + {intercept:.4f}, \\ R^2 = {adj_r2}$'

    ax.text(0.95, 0.05, equation_line, transform=ax.transAxes, ha='right', fontsize=12)

    st.pyplot(fig)

    
def showStat(total_df):
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    selected = st.selectbox("분석 메뉴", ['두 집단간 차이 검정', '상관분석', '회귀분석'])
    if selected == '두 집단간 차이 검정':
        st.markdown("### 📍 두 집단간 차이 검정 이론 설명 \n"
                    "- t-검정은 두 개의 독립적인 데이터 샘플의 평균 간에 유의미한 차이가 있는지 확인하는데 사용할 수 있는 통계 테스트입니다. \n")
        st.markdown("- t-통계량을 구하는 것은 아래와 같습니다. ($\\bar{X}$ : 표본의 평균을 말합니다.)")
        st.latex(r'''
        t = \frac{{\bar{X} - \mu}}{{s/\sqrt{n}}}
        ''')
        twoMeans(total_df)
    elif selected == "상관분석":
        st.markdown("### 📍 상관분석 이론 설명 \n"
            "- 피어슨 상관계수: 두 변수 간의 선형 관계 강도를 측정합니다. \n"
            "- 스피어만 상관계수: 두 변수 간의 순위 관계를 측정합니다. \n"
            "- 두 방법 모두 -1에서 1 사이의 값을 가지며, 0은 상관관계가 없음을 의미합니다.")

        corrRelation(total_df)
    elif selected == "회귀분석":
        st.markdown("### 📍 회귀분석 이론 설명 \n"
            "- 회귀분석은 두 변수 간의 관계를 모델링하는 기법입니다. \n"
            "- 독립 변수와 종속 변수 간의 관계를 수학적 식으로 표현하며, 이를 통해 예측할 수 있습니다. \n"
            "- 주요 가정: 독립성, 선형성, 잔차의 정규성, 등분산성 등이 있습니다.")
        regRession(total_df)
    else:
        st.warning("Wrong")
                        