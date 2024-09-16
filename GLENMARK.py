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

df_file = st.file_uploader("Wrzuć plik oryginalny raport od działu rozliczeń:")

# Sprawdzanie, czy użytkownik załadował plik
if df_file is not None:
    try:
        # Próba załadowania pliku
        df = pd.read_excel(df_file)

        # Sprawdzenie, czy kolumna istnieje
        if 'Rodzaj promocji' in df.columns:
            df_filtered = df[df['Rodzaj promocji'] == 'IPRA']
            st.write(df_filtered)  # Wyświetlenie przefiltrowanych danych
        else:
            st.error("Kolumna 'Rodzaj promocji' nie istnieje w pliku.")
    except ValueError:
        st.error("Nieprawidłowy format pliku. Proszę załadować plik Excel.")
    except Exception as e:
        # Własny, bezpieczny komunikat o błędzie bez śladu stosu
        st.error("Wystąpił nieoczekiwany błąd. Skontaktuj się z administratorem.")
else:
    st.info("Proszę załadować plik, aby kontynuować.")

lista = pd.read_excel('Lista aptek Glenmark_.xlsx')

df = df[df['Rodzaj promocji'] =='IPRA']

df = df.groupby(['Kod pocztowy', 'Indeks', 'Nazwa towaru']).agg({
    'Ilość sprzedana': 'sum',
    'Wartość sprzedaży': 'sum'
}).reset_index()

df['Czy w liście'] = df['Kod pocztowy'].isin(lista['Kod pocztowy'])

df1 = df[df['Czy w liście'] == True]

df2 = df[df['Czy w liście'] == False]

df1 = df1.merge(lista[['Kod pocztowy','SAP','Nazwa apteki','Miejscowość','Ulica','Nr domu']], on='Kod pocztowy', how='left')
df1

# Wszystkie dostępne kody :
kody = lista['Kod pocztowy'].unique().tolist()

def dopasuj_inny_kod_pocztowy(df, kolumna_kodu, kody):
    # Tworzymy słownik, aby przechowywać liczbę użyć każdego kodu
    liczba_uzyc = {kod: 0 for kod in kody}

    # Funkcja pomocnicza do dopasowania kodu
    def znajdz_podobny_kod(kod):
        prefix_3 = kod[:4]
        prefix_2 = kod[:2]

        # Najpierw próbujemy dopasować kod na podstawie trzech pierwszych cyfr
        for kod_z_listy in kody:
            if kod_z_listy.startswith(prefix_3) and liczba_uzyc[kod_z_listy] == 0 and kod_z_listy != kod:
                liczba_uzyc[kod_z_listy] += 1
                return kod_z_listy

        # Następnie próbujemy dopasować na podstawie dwóch pierwszych cyfr
        for kod_z_listy in kody:
            if kod_z_listy.startswith(prefix_2) and liczba_uzyc[kod_z_listy] == 0 and kod_z_listy != kod:
                liczba_uzyc[kod_z_listy] += 1
                return kod_z_listy

        # Jeżeli nie udało się znaleźć jeszcze dopasowania, dopasowujemy kod, który ma takie same dwie cyfry, ale pozwalamy na powtórzenia
        for kod_z_listy in kody:
            if kod_z_listy.startswith(prefix_2) and kod_z_listy != kod:
                liczba_uzyc[kod_z_listy] += 1
                return kod_z_listy

        # Jeśli nie ma żadnego dopasowania, nie zwracamy nic
        return None

    # Tworzymy nową kolumnę w df z dopasowanymi kodami
    df['dopasowany_kod'] = df['Kod pocztowy'].apply(znajdz_podobny_kod)
    
    return df


# Użycie funkcji do dopasowania kodów pocztowych
df_dopasowany = dopasuj_inny_kod_pocztowy(df2, 'Kod_pocztowy', kody)

df_dopasowany = df_dopasowany.merge(lista[['Kod pocztowy', 'SAP', 'Nazwa apteki', 'Miejscowość', 'Ulica', 'Nr domu']], left_on='dopasowany_kod', right_on='Kod pocztowy',how='left',
                                   suffixes=('','_dopasowany'))
df_dopasowany = df_dopasowany.drop(columns=['Kod pocztowy_dopasowany'])
df_dopasowany






