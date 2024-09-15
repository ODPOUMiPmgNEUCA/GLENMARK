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


df = st.file_uploader(
        label = "Wrzuć plik oryginalny raport od działu rozliczeń"
    )
if df:
    df= pd.read_excel(df)
    st.write('Podgląd danych z raportu :')
    st.write(df.head())
    
    
lista = pd.read_excel('Lista aptek Glenmark_.xlsx')

df = df[df['Rodzaj promocji'] =='IPRA']

df = df.groupby(['Kod pocztowy', 'Indeks', 'Nazwa towaru']).agg({
    'Ilość sprzedana': 'sum',
    'Wartość sprzedaży': 'sum'
}).reset_index()

st.write('Podgląd danych z raportu posortowanych po ilości i wartości sprzedaży :')
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

        # Jeśli nie uda się znaleźć na podstawie żadnych cyfr, próbujemy znaleźć kod o tych samych dwóch pierwszych cyfrach
        for kod_z_listy in kody:
            if kod_z_listy.startswith(prefix_2) and kod_z_listy != kod:
                return kod_z_listy

        # Jeśli nie ma żadnego dopasowania, nie zwracamy nic
        return None

    # Tworzymy nową kolumnę w df z dopasowanymi kodami
    df['dopasowany_kod'] = df['Kod pocztowy'].apply(znajdz_podobny_kod)
    
    return df


# Użycie funkcji do dopasowania kodów pocztowych
df_dopasowany = dopasuj_inny_kod_pocztowy(df1, 'Kod_pocztowy', kody)
df_dopasowany

st.write('Liczba kodów pocztowych w liście :')
st.write(len(lista))
st.write('Liczba kodów pocztowych w raporcie :')
st.write(len(df1))
st.write('Liczba kodów z raportu, które nie mają dopasowanego kodu :')
st.write(df_dopasowany['dopasowany_kod'].isna().sum())


liczba_duplikatow = (df_dopasowany['dopasowany_kod'] == df_dopasowany['Kod pocztowy']).sum()
st.write('Liczba kodów z raportu, które mają dopasowany identyczny kod :')
liczba_duplikatow


df_dopasowany = df_dopasowany.merge(lista, left_on='dopasowany_kod', right_on='Kod pocztowy', suffixes=('', '_dopasowany'))
df_dopasowany = df_dopasowany.drop(columns=['Kod pocztowy_dopasowany'])
df_dopasowany











