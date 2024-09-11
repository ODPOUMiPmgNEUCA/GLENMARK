# -*- coding: utf-8 -*-
"""Soczyste rabaty.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1bfU5lwdNa2GOPWmQ9-URaf30VnlBzQC0
"""

#importowanie potrzebnych bibliotek
import os
import openpyxl
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
import io



st.set_page_config(page_title='GLENMARK', layout='wide')




tabs_font_css = """
<style>
div[class*="stTextInput"] label {
  font-size: 26px;
  color: black;
}
div[class*="stSelectbox"] label {
  font-size: 26px;
  color: black;
}
</style>
"""

df = st.file_uploader(
        label = "Wrzuć plik oryginalny raport od działu rozliczeń"
    )
if df:
    df= pd.read_excel(df)
    st.write(df.head())
    
    
lista = pd.read_excel('Lista aptek Glenmark_.xlsx')

df = df[df['Rodzaj promocji'] =='IPRA']

df = df.groupby(['Kod pocztowy', 'Indeks', 'Nazwa towaru']).agg({
    'Ilość sprzedana': 'sum',
    'Wartość sprzedaży': 'sum'
}).reset_index()

df

df['Czy w liście'] = df['Kod pocztowy'].isin(lista['Kod pocztowy'])

df1 = df[df['Czy w liście'] == True]

df2 = df[df['Czy w liście'] == False]

df1 = df1.merge(lista[['Kod pocztowy','SAP','Nazwa apteki','Miejscowość','Ulica','Nr domu']], on='Kod pocztowy', how='left')
df1













