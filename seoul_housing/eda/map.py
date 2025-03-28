# -*- coding:utf-8 -*-
import json
import io
import streamlit as st
import geopandas as gpd 

import matplotlib.pyplot as plt
import plotly.express as px

def mapMatplotlib(merge_df):
    fig, ax = plt.subplots(ncols=2, sharey=True, figsize=(15, 10))
    merge_df[merge_df['month'] == 2].plot(ax=ax[0], column='mean', cmap='Pastel1', legend=False, alpha=0.9, edgecolor='gray')
    merge_df[merge_df['month'] == 3].plot(ax=ax[1], column='mean', cmap='Pastel1', legend=False, alpha=0.9, edgecolor='gray')

    patch_col = ax[0].collections[0]
    cb = fig.colorbar(patch_col, ax=ax, shrink=0.5)
    for i, row in merge_df[merge_df['month'] == 2].iterrows():
        ax[0].annotate(row['SIG_KOR_NM'], xy=(row['lon'], row['lat']), xytext=(-7,2), textcoords='offset points', fontsize=8, color='black')
    for i, row in merge_df[merge_df['month'] == 3].iterrows():
        ax[1].annotate(row['SIG_KOR_NM'], xy=(row['lon'], row['lat']), xytext=(-7,2), textcoords='offset points', fontsize=8, color='black')

    ax[0].set_title('2023-2월 아파트 평균(만원)')
    ax[1].set_title('2023-3월 아파트 평균(만원)')
    ax[0].set_axis_off()
    ax[1].set_axis_off()

    st.pyplot(fig)

def mapPlotly(merge_df):
    with open('/Users/songsooyeoun/Desktop/git_test/streamlit/project1/sig_20230729/seoul.geojson') as f:
        seouls = json.load(f)
    
    moth = st.sidebar.radio("월", [2, 3])  # Fix: Use `moth` instead of `month`
    result = merge_df[merge_df['month'] == moth].reset_index(drop=True)  # Fix: Correct variable name
    mapbox_style = st.sidebar.selectbox('지도스타일', ['white-bg', 'open-street-map', 'carto-positron', 'carto-darkmatter', 
                                                    'stamen-terrain', 'stamen-toner', 'stamen-watercolor'])
    fig = px.choropleth_mapbox(result,
                           geojson=seouls,
                           locations='SIG_KOR_NM', color='mean',
                           color_continuous_scale='Viridis',
                           featureidkey='properties.SIG_KOR_NM',
                           mapbox_style=mapbox_style,
                           zoom=10,
                           center={'lat': 37.563383, 'lon': 126.996039},  # Fix: Correct lat value
                           opacity=0.5,
                           labels={'mean':'아파트 평균가격(만원)'})

    fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0})
    fig.update_traces(hovertemplate='<b>%{location}</b><br>아파트평균가격: %{z:,.0f}(만원)')
    fig.update_coloraxes(colorbar_tickformat='000')
    
    st.plotly_chart(fig)

def showMap(total_df):
    st.markdown("### 병합 데이터 확인 \n"
                "- 컬럼명 확인")
    shapefile_path = "/Users/songsooyeoun/Desktop/git_test/streamlit/project1/sig_20230729/sig.shp"

    seoul_gpd  = gpd.read_file(shapefile_path, encoding='cp949')
    seoul_gpd = seoul_gpd[seoul_gpd['SIG_CD'].astype(str).str.startswith('11')]
    seoul_gpd = seoul_gpd.set_crs(epsg='5178', allow_override=True)
    seoul_gpd['center_point'] = seoul_gpd['geometry'].geometry.centroid
    seoul_gpd['geometry'] = seoul_gpd['geometry'].to_crs(epsg='4326')
    seoul_gpd['center_point'] = seoul_gpd['center_point'].to_crs(epsg='4326')
    seoul_gpd['lon'] = seoul_gpd['center_point'].map(lambda x: x.xy[0][0])
    seoul_gpd['lat'] = seoul_gpd['center_point'].map(lambda x: x.xy[1][0])

    total_df['month'] = total_df['CTRT_DAY'].dt.month
    total_df = total_df[(total_df['BLDG_USG'] == '아파트') & (total_df['month'].isin([2, 3]))]
    total_df = total_df[['CTRT_DAY', 'month', 'CGG_CD', 'CGG_NM', 'THING_AMT','BLDG_USG']].reset_index(drop=True)
    
    summary_df = total_df.groupby(['CGG_CD', 'month'])['THING_AMT'].agg(['mean', 'std', 'size']).reset_index()
    summary_df = summary_df.rename(columns={'CGG_CD':'SIG_CD'})
    summary_df['SIG_CD'] = summary_df['SIG_CD'].astype(str)

    merge_df = seoul_gpd.merge(summary_df, on='SIG_CD')

    st.write(merge_df.info()) 

    buffer = io.StringIO()
    merge_df.info(buf=buffer)  
    df_info = buffer.getvalue()
    st.text(df_info)

    st.markdown("- 일부 데이터만 확인")
    st.write(merge_df[['SIG_KOR_NM', 'geometry', 'mean']].head(3))
    st.markdown("<hr>", unsafe_allow_html=True)
    selected_lib = st.sidebar.radio("라이브러리 종류", ['Matplotlib', 'Plotly'])

    if selected_lib == "Matplotlib":
        st.markdown("### Matplotlib Style")
        mapMatplotlib(merge_df)
    elif selected_lib == "Plotly":
        st.markdown("### Plotly Style")
        mapPlotly(merge_df)
    else:
        pass
