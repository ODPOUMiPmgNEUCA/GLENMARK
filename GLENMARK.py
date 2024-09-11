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

# Wszystkie dostępne kody :
kody = df['Kod pocztowy'].unique().tolist()

def dopasuj_inny_kod_pocztowy(df, kolumna_kodu, kody):
    # Tworzymy zbiór, aby przechowywać już użyte kody
    wykorzystane_kody = set()

    # Funkcja pomocnicza do dopasowania kodu
    def znajdz_podobny_kod(kod):
        # Pobieramy pierwsze trzy cyfry kodu
        prefix_3 = kod[:4]
        prefix_2 = kod[:2]
        prefix_1 = kod[:1]
        
        # Próbujemy znaleźć kod pocztowy na podstawie trzech pierwszych cyfr
        for kod_z_listy in kody:
            if kod_z_listy.startswith(prefix_3) and kod_z_listy not in wykorzystane_kody and kod_z_listy != kod:
                wykorzystane_kody.add(kod_z_listy)
                return kod_z_listy
        
        # Jeśli nie uda się znaleźć na podstawie trzech cyfr, próbujemy z dwoma pierwszymi
        for kod_z_listy in kody:
            if kod_z_listy.startswith(prefix_2) and kod_z_listy not in wykorzystane_kody and kod_z_listy != kod:
                wykorzystane_kody.add(kod_z_listy)
                return kod_z_listy

        # Jeśli nie uda się znaleźć na podstawie dwóch cyfr, próbujemy z pierwszą
        for kod_z_listy in kody:
            if kod_z_listy.startswith(prefix_1) and kod_z_listy not in wykorzystane_kody and kod_z_listy != kod:
                wykorzystane_kody.add(kod_z_listy)
                return kod_z_listy

        # Jeśli nie ma żadnego dopasowania, nie zwracamy nic (można ewentualnie dodać inne zachowanie)
        return None

    # Tworzymy nową kolumnę w df z dopasowanymi kodami
    df['dopasowany_kod'] = df['Kod pocztowy'].apply(znajdz_podobny_kod)
    
    return df


# Użycie funkcji do dopasowania kodów pocztowych
df_dopasowany = dopasuj_inny_kod_pocztowy(df1, 'Kod_pocztowy', kody)
df_dopasowany


st.write(len(lista))
st.write(len(df1))






















