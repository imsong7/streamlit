# -*- coding:utf-8 -*-
import json
import io
import streamlit as st
import geopandas as gpd 

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import plotly.express as px
import os

def set_korean_font():
    font_path = os.path.join('seoul_housing', 'Nanum_Gothic', 'NanumGothic-Regular.ttf')
    font_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
    return font_prop


# def mapMatplotlib(merge_df):
#     font_prop = set_korean_font()
#     fig, ax = plt.subplots(ncols=3, sharey=True, figsize=(30, 18))
#     merge_df[merge_df['month'] == 1].plot(ax=ax[0], column='mean', cmap='Pastel1', legend=False, alpha=0.9, edgecolor='gray')
#     merge_df[merge_df['month'] == 2].plot(ax=ax[1], column='mean', cmap='Pastel1', legend=False, alpha=0.9, edgecolor='gray')
#     merge_df[merge_df['month'] == 3].plot(ax=ax[2], column='mean', cmap='Pastel1', legend=False, alpha=0.9, edgecolor='gray')

#     plt.subplots_adjust(wspace=0.05) 

#     patch_col = ax[0].collections[0]
#     cb = fig.colorbar(patch_col, ax=ax, orientation='horizontal', shrink=0.5, aspect=50, pad=0.1)
    
#     for i, row in merge_df[merge_df['month'] == 1].iterrows():
#         ax[0].annotate(row['SIG_KOR_NM'], xy=(row['lon'], row['lat']), xytext=(-7,2), textcoords='offset points', fontproperties=font_prop, fontsize=8, color='black')
#     for i, row in merge_df[merge_df['month'] == 2].iterrows():
#         ax[1].annotate(row['SIG_KOR_NM'], xy=(row['lon'], row['lat']), xytext=(-7,2), textcoords='offset points', fontproperties=font_prop, fontsize=8, color='black')
#     for i, row in merge_df[merge_df['month'] == 3].iterrows():
#         ax[2].annotate(row['SIG_KOR_NM'], xy=(row['lon'], row['lat']), xytext=(-7,2), textcoords='offset points', fontproperties=font_prop, fontsize=8, color='black')

#     ax[0].set_title('2025년 1월 아파트 평균(만원)', fontproperties=font_prop, fontsize=23, weight='heavy')
#     ax[1].set_title('2025년 2월 아파트 평균(만원)', fontproperties=font_prop, fontsize=23, weight='heavy')
#     ax[2].set_title('2025년 3월 아파트 평균(만원)', fontproperties=font_prop, fontsize=23, weight='heavy')
#     ax[0].set_axis_off()
#     ax[1].set_axis_off()
#     ax[2].set_axis_off()

    st.pyplot(fig)

def mapPlotly(merge_df, month):
    font_prop = set_korean_font()
    with open('seoul_housing/sig_20230729/seoul.geojson') as f:
        seouls = json.load(f)
    
    result = merge_df[merge_df['month'] == month].reset_index(drop=True)  
    mapbox_style = st.sidebar.selectbox('지도스타일', ['white-bg', 'open-street-map', 'carto-positron', 'carto-darkmatter'], index=1)

    fig = px.choropleth_mapbox(result,
                           geojson=seouls,
                           locations='SIG_KOR_NM', color='mean',
                           color_continuous_scale='Viridis',
                           featureidkey='properties.SIG_KOR_NM',
                           mapbox_style=mapbox_style,
                           zoom=10,
                           center={'lat': 37.563383, 'lon': 126.996039},  
                           opacity=0.5,
                           labels={'mean':'아파트 평균가격(만원)'})

    fig.update_layout(margin=dict(r=0, t=0, l=0, b=0))
    fig.update_traces(hovertemplate='<b>%{location}</b><br>아파트평균가격: %{z:,.0f}(만원)')
    fig.update_coloraxes(colorbar_tickformat='000')
    
    st.plotly_chart(fig)

def showMap(total_df, month):
    shapefile_path = "seoul_housing/sig_20230729/sig.shp"

    seoul_gpd  = gpd.read_file(shapefile_path, encoding='cp949')
    seoul_gpd = seoul_gpd[seoul_gpd['SIG_CD'].astype(str).str.startswith('11')]
    seoul_gpd = seoul_gpd.set_crs(epsg='5178', allow_override=True)
    seoul_gpd['center_point'] = seoul_gpd['geometry'].geometry.centroid
    seoul_gpd['geometry'] = seoul_gpd['geometry'].to_crs(epsg='4326')
    seoul_gpd['center_point'] = seoul_gpd['center_point'].to_crs(epsg='4326')
    seoul_gpd['lon'] = seoul_gpd['center_point'].map(lambda x: x.xy[0][0])
    seoul_gpd['lat'] = seoul_gpd['center_point'].map(lambda x: x.xy[1][0])

    total_df = total_df[['CTRT_DAY', 'month', 'CGG_CD', 'CGG_NM', 'THING_AMT','BLDG_USG']].reset_index(drop=True)
    
    summary_df = total_df.groupby(['CGG_CD', 'month'])['THING_AMT'].agg(['mean', 'std', 'size']).reset_index()
    summary_df = summary_df.rename(columns={'CGG_CD':'SIG_CD'})
    summary_df['SIG_CD'] = summary_df['SIG_CD'].astype(str)

    merge_df = seoul_gpd.merge(summary_df, on='SIG_CD')

    mapPlotly(merge_df, month)