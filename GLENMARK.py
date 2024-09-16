# Importowanie potrzebnych bibliotek
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
from rapidfuzz import process, fuzz


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

df_file = st.file_uploader(
    label="Wrzuć plik oryginalny raport od działu rozliczeń:"
)

if df_file:
    try:
        # Próba załadowania pliku i wykonania operacji na nim
        df = pd.read_excel(df_file)

        lista = pd.read_excel('Lista aptek Glenmark_.xlsx')

        # Filtruj dane
        df = df[df['Rodzaj promocji'] == 'IPRA']

        # Grupowanie
        df = df.groupby(['Kod pocztowy', 'Indeks', 'Nazwa towaru']).agg({
            'Ilość sprzedana': 'sum',
            'Wartość sprzedaży': 'sum'
        }).reset_index()

        # Sprawdź, czy kod pocztowy znajduje się na liście
        df['Czy w liście'] = df['Kod pocztowy'].isin(lista['Kod pocztowy'])

        # Podziel dane na dwie grupy
        df1 = df[df['Czy w liście'] == True]
        df2 = df[df['Czy w liście'] == False]

        # Połącz z listą aptek
        df1 = df1.merge(lista[['Kod pocztowy', 'SAP', 'Nazwa apteki', 'Miejscowość', 'Ulica', 'Nr domu']], on='Kod pocztowy', how='left')

        # Wyświetl df1
        st.write(df1)

    except Exception as e:
        # Wyświetl przyjazny komunikat o błędzie
        st.error("Wystąpił problem podczas przetwarzania pliku. Upewnij się, że plik ma odpowiedni format.")
        # Opcjonalnie: Wyświetl szczegóły błędu w logach
        st.write(f"Błąd szczegółowy: {e}")





















