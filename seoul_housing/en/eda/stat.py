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

def set_english_font():
    plt.rcParams['font.family'] = 'Arial'  
    plt.rcParams['axes.unicode_minus'] = False


def twoMeans(total_df):
    font_prop = set_english_font() 
    
    total_df['month'] = total_df['CTRT_DAY'].dt.month
    apt_df = total_df[(total_df['BLDG_USG'] == 'Apartment') & (total_df['month'].isin([1, 2, 3]))]
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📍 Summary \n"
                "Compare apartment prices between two selected months.")
    
    # Allow selection of two months with names
    month_names = ['January', 'Feburary', 'March']
    selected_months = st.sidebar.multiselect(
        "Select two months to compare", 
        options=month_names, 
        default=month_names[:2]
    )

    if len(selected_months) == 2:
        month1, month2 = selected_months
        month_map = {'January': 1, 'Feburary': 2, 'March': 3}
        month1, month2 = month_map[month1], month_map[month2]
        st.markdown(f"#### Compare apartment prices for {month_names[month1-1]} and {month_names[month2-1]}")

        apt_df = total_df[(total_df['BLDG_USG'] == 'Apartment') & (total_df['month'].isin([month1, month2]))]
        month1_df = apt_df[apt_df['month'] == month1]
        month2_df = apt_df[apt_df['month'] == month2]

        ttest_df = round(apt_df.groupby('month')['THING_AMT'].agg(['mean', 'std', 'size']), 1)
        st.dataframe(ttest_df, use_container_width=True)
    
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"#### Difference test between {month_names[month1-1]} and {month_names[month2-1]} in Seoul \n"
                    f"- Test the difference in average apartment prices between {month_names[month1-1]} and {month_names[month2-1]}. \n"
                    "- Hypothesis setup \n"
                    f"  + Null Hypothesis: $H_{0}$: No difference in average apartment prices between {month_names[month1-1]} and {month_names[month2-1]}. \n"
                    f"  + Alternative Hypothesis: $H_{1}$: There is a difference in average apartment prices between {month_names[month1-1]} and {month_names[month2-1]}. \n")
    
        result = ttest(month1_df['THING_AMT'], month2_df['THING_AMT'], paired=False)
        st.dataframe(result, use_container_width=True)
        st.markdown(f"Based on the p-value of **{result['p-val'].values[0]}**, we accept $H_{0}$, meaning there is no significant difference in average apartment prices between {month_names[month1-1]} and {month_names[month2-1]}.")

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(f"Select a district to check if there is a significant difference in average apartment prices for {month_names[month1-1]} and {month_names[month2-1]}. \n")
        selected_cgg_nm = st.selectbox("Select district", sorted(total_df["CGG_NM_EN"].unique()))
        cols = st.columns((2, 2), gap='medium')
        with cols[0]:
            st.markdown(f"#### {selected_cgg_nm} {month_names[month1-1]} vs {month_names[month2-1]} difference test \n")

            cgg_df = apt_df[apt_df['CGG_NM_EN'] == selected_cgg_nm]
            cgg_month1 = cgg_df[cgg_df['month'] == month1]
            cgg_month2 = cgg_df[cgg_df['month'] == month2]

            cgg_result = ttest(cgg_month1['THING_AMT'], cgg_month2['THING_AMT'], paired=False)
            st.dataframe(cgg_result, use_container_width=True)
            if cgg_result['p-val'].values[0] > 0.05:
                st.markdown(f"Based on the p-value of **{cgg_result['p-val'].values[0]}**, we accept $H_{0}$, meaning there is no significant difference in apartment prices between {month_names[month1-1]} and {month_names[month2-1]}.")  # Null hypothesis
            else:
                st.markdown(f"Based on the p-value of **{cgg_result['p-val'].values[0]}**, we accept $H_{1}$, meaning there is a significant difference in apartment prices between {month_names[month1-1]} and {month_names[month2-1]}.")  # Alternative hypothesis
            
        with cols[1]:
            st.markdown(f"#### {selected_cgg_nm} {month_names[month1-1]} vs {month_names[month2-1]} visualization", unsafe_allow_html=True)
            fig, ax = plt.subplots(figsize=(10, 3))
            sns.pointplot(x='month', y='THING_AMT', data=cgg_df)
            sns.despine()
            ax.set_xlabel("Month", fontproperties=font_prop, fontsize=12)
            ax.set_ylabel("Apartment Price (10,000 KRW)", fontproperties=font_prop, fontsize=12)
            st.pyplot(fig)
            st.dataframe(round(cgg_df.groupby('month')['THING_AMT'].agg(['mean', 'std', 'size']), 1), use_container_width=True)
    else:
        st.warning("Please select two months.")


def corrRelation(total_df):
    font_prop = set_english_font() 
    
    total_df['month'] = total_df['CTRT_DAY'].dt.month
    apt_df = total_df[(total_df['BLDG_USG'] == 'Apartment') & (total_df['month'].isin([1, 2, 3]))]
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📍 Data Check \n"
                "Let's first check the correlation between the building area and the price of the property. \n")
    corr_df = apt_df[['CTRT_DAY', 'THING_AMT', 'ARCH_AREA', 'CGG_NM_EN', 'month']].reset_index(drop=True)
    st.dataframe(corr_df.head())

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"### 📍 Correlation Analysis between Apartment Price and Building Area\n")
    col = st.columns((1.7, 2), gap='medium')
    with col[0]:        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(x='ARCH_AREA', y='THING_AMT', data=corr_df, ax=ax)
        ax.set_title('Correlation between Building Area and Apartment Price', fontproperties=font_prop, fontsize=15)
        ax.set_xlabel('Building Area', fontproperties=font_prop)
        ax.set_ylabel('Apartment Price (10K KRW)', fontproperties=font_prop)
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

    with col[1]:
        st.markdown("#### Correlation Coefficient and Test \n")
        seoul_coef = pg.corr(corr_df['ARCH_AREA'], corr_df['THING_AMT'])["r"].values[0] 
        st.dataframe(pg.corr(corr_df['ARCH_AREA'],  corr_df['THING_AMT']).round(3), use_container_width=True)
        st.markdown(f"The correlation coefficient is <span style='color:red'>{seoul_coef:.2f}</span>, showing a tendency that as the building area increases, the property price also increases. \n"
                    "Now, let's check the correlation and visualizations for each district.", unsafe_allow_html=True)
        
    
    st.markdown("<hr>", unsafe_allow_html=True)
    selected_cgg_nm = st.selectbox("Select district", sorted(corr_df['CGG_NM_EN'].unique()))
    selected_month = st.selectbox("Select month", sorted(corr_df['month'].unique()))
    
    cgg_df = corr_df[(corr_df['CGG_NM_EN'] == selected_cgg_nm) & (corr_df['month'] == selected_month)]
    corr_coef = pg.corr(cgg_df['ARCH_AREA'], cgg_df['THING_AMT'])

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(x='ARCH_AREA', y='THING_AMT', data=cgg_df)
    ax.text(0.95, 0.05, f'Pearson Correlation: {corr_coef["r"].values[0]:.2f}',
            transform=ax.transAxes, ha='right', fontsize=12)
    ax.set_title('Correlation Coefficient', fontproperties=font_prop, fontsize=15, weight='bold')
    ax.set_xlabel("Building Area", fontproperties=font_prop, fontsize=12)
    ax.set_ylabel("Apartment Price (10K KRW)", fontproperties=font_prop, fontsize=12)
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

    st.dataframe(corr_coef, use_container_width=True)

def regRession(total_df):
    font_prop = set_english_font() 
    
    total_df['month'] = total_df['CTRT_DAY'].dt.month
    apt_df = total_df[(total_df['BLDG_USG'] == 'Apartment') & (total_df['month'].isin([1, 2, 3]))]
    corr_df = apt_df[['CTRT_DAY', 'THING_AMT', 'ARCH_AREA', 'CGG_NM_EN', 'month']].reset_index(drop=True)
    
    selected_cgg_nm = st.sidebar.selectbox("District Name", sorted(corr_df['CGG_NM_EN'].unique()))
    selected_month = st.sidebar.selectbox("Month", sorted(corr_df['month'].unique()))
    reg_df = corr_df[(corr_df['CGG_NM_EN'] == selected_cgg_nm) & (corr_df['month'] == selected_month)]
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📍 Data Check")
    st.dataframe(reg_df, use_container_width=True)

    # Regression formula
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 📍 Building Area and Apartment Price Regression Analysis \n"
                "Check if the statistical assumptions are met. \n")
    
    col = st.columns((2, 2), gap='medium')
    with col[0]:
        st.markdown("#### 1) Normality Test \n"
                    "First, visually check the normality of the residuals.")
        
        mod1 = pg.linear_regression(reg_df['ARCH_AREA'], reg_df['THING_AMT'])
        res = mod1.residuals_
        res = pd.DataFrame(res, columns=['Residuals'])
        
        fig = px.histogram(res, x='Residuals')
        st.plotly_chart(fig)
        
        sw = pg.normality(res, method='shapiro')
        st.dataframe(sw, use_container_width=True)
        
        st.markdown("- Changing the district name may show statistically significant results in some areas and not in others. \n"
                    "- If the p-value is very small (less than 0.05), the normality of the residuals is violated, and the typical regression results should not be interpreted. \n"
                    "- In such cases, a process of removing extreme outliers is required.")
    
    with col[1]:
        st.markdown("#### 2) Check Regression Model \n"
                    "Check the coefficient of determination $R^2$ and p-value.")
        st.dataframe(mod1.round(2), use_container_width=True)
        
        intercept, slope = mod1['coef'].values[0], mod1['coef'].values[1]
        st.write("Intercept:", intercept, "Slope:", slope)

        fig, ax = plt.subplots(figsize=(10,6))
        x = np.linspace(0, reg_df['ARCH_AREA'].max())
        
        sns.scatterplot(data=reg_df, x='ARCH_AREA', y='THING_AMT', ax=ax)
        ax.set_title("Regression Line", fontproperties=font_prop, fontsize=15, weight='bold')
        ax.set_xlabel("Building Area", fontproperties=font_prop, fontsize=12)
        ax.set_ylabel("Apartment Transaction Price (10K KRW)", fontproperties=font_prop, fontsize=12)
        ax.plot(x, slope*x + intercept, color='red')
        ax.grid(True, alpha=0.3)

        if intercept < 0:
            equation_line = f'$Y={slope:.1f}X{intercept:.1f}, R^2={np.round(mod1["adj_r2"].values[0], 3)}$'
        else:
            equation_line = f'$Y={slope:.1f}X+{intercept:.1f}, R^2={np.round(mod1["adj_r2"].values[0], 3)}$'
            
        ax.text(0.95, 0.05, equation_line, transform=ax.transAxes, ha='right', fontsize=12)
        st.pyplot(fig)

    
    
def showStat(total_df):
    total_df['CTRT_DAY'] = pd.to_datetime(total_df['CTRT_DAY'], format='%Y-%m-%d')
    selected = st.sidebar.selectbox("Analysis Menu", ['Two-Sample t-Test', 'Correlation Analysis', 'Regression Analysis'])
    if selected == 'Two-Sample t-Test':
        st.markdown("### 📍 Two-Sample t-Test Theory \n"
                    "- The t-test is a statistical test used to determine if there is a significant difference between the means of two independent data samples. \n")
        st.markdown("- The t-statistic is calculated as follows: ($\\bar{X}$ represents the sample mean.)")
        st.latex(r'''
        t = \frac{{\bar{X} - \mu}}{{s/\sqrt{n}}}
        ''')
        twoMeans(total_df)
    elif selected == "Correlation Analysis":
        st.markdown("### 📍 Correlation Analysis Theory \n"
            "- Pearson Correlation Coefficient: Measures the strength of the linear relationship between two variables. \n"
            "- Spearman Correlation Coefficient: Measures the rank relationship between two variables. \n"
            "- Both methods range from -1 to 1, with 0 indicating no correlation.")

        corrRelation(total_df)
    elif selected == "Regression Analysis":
        st.markdown("### 📍 Regression Analysis Theory \n"
            "- Regression analysis is a technique used to model the relationship between two variables. \n"
            "- It expresses the relationship between independent and dependent variables mathematically, allowing for predictions. \n"
            "- Key assumptions: independence, linearity, normality of residuals, homoscedasticity, etc.")
        regRession(total_df)
    else:
        st.warning("Wrong")