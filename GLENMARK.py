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
import datetime


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
    label="Wrzuć plik raportu od działu rozliczeń :"
)


import pandas as pd
import streamlit as st
import datetime
import io

# Umożliwienie wczytania pliku
df_file = st.file_uploader(
    label="Wrzuć plik raportu od działu rozliczeń :"
)

if df_file:
    try:
        # Załaduj plik główny oraz listę aptek
        df = pd.read_excel(df_file)
        lista = pd.read_excel('Lista aptek Glenmark_.xlsx')

        # Przetwarzanie danych dla promocji 'IPRA'
        df_ipra = df[df['Rodzaj promocji'] == 'IPRA']
        df_ipra = df_ipra.groupby(['Kod pocztowy', 'Indeks', 'Nazwa towaru']).agg({
            'Ilość sprzedana': 'sum',
            'Wartość sprzedaży': 'sum'
        }).reset_index()

        # Sprawdzenie sum ilości i wartości w df_ipra
        total_quantity_ipra = df_ipra['Ilość sprzedana'].sum()
        total_value_ipra = df_ipra['Wartość sprzedaży'].sum()
        st.write(f"Suma ilości dla IPRA: {total_quantity_ipra}, Suma wartości dla IPRA: {total_value_ipra}")

        # Flaga, czy kod pocztowy jest na liście
        df['Czy w liście'] = df['Kod pocztowy'].isin(lista['Kod pocztowy'])
        lista_unique = lista.drop_duplicates(subset=['Kod pocztowy'])
        kody = lista_unique['Kod pocztowy'].unique().tolist()

        # Funkcja do dopasowania podobnych kodów
        def dopasuj_inny_kod_pocztowy(kod, kody):
            prefix_3 = kod[:4]
            prefix_2 = kod[:2]

            # Najpierw próbujemy dopasować kod na podstawie trzech pierwszych cyfr
            for kod_z_listy in kody:
                if kod_z_listy.startswith(prefix_3) and kod_z_listy != kod:
                    return kod_z_listy

            # Następnie próbujemy dopasować na podstawie dwóch pierwszych cyfr
            for kod_z_listy in kody:
                if kod_z_listy.startswith(prefix_2) and kod_z_listy != kod:
                    return kod_z_listy

            # Jeżeli nie udało się znaleźć jeszcze dopasowania, dopasowujemy kod, który ma takie same dwie cyfry, ale pozwalamy na powtórzenia
            for kod_z_listy in kody:
                if kod_z_listy.startswith(prefix_2) and kod_z_listy != kod:
                    return kod_z_listy

            # Jeśli nie ma żadnego dopasowania, zwracamy None
            return None

        # Utwórz kolumnę z dopasowanym kodem pocztowym
        df['Dopasowany kod'] = df.apply(lambda row: dopasuj_inny_kod_pocztowy(row['Kod pocztowy'], kody) 
                                         if row['Rodzaj promocji'] == 'IPRA' and not row['Kod pocztowy'] in kody else row['Kod pocztowy'], axis=1)

        # Grupa danych na podstawie dopasowanych kodów
        df_dopasowany = df.groupby(['Dopasowany kod', 'Indeks', 'Nazwa towaru']).agg({
            'Ilość sprzedana': 'sum',
            'Wartość sprzedaży': 'sum'
        }).reset_index()

        # Połączenie z listą aptek dla dopasowanych kodów
        df_dopasowany = df_dopasowany.merge(lista_unique[['Kod pocztowy', 'SAP', 'Nazwa apteki', 'Miejscowość', 'Ulica', 'Nr domu']], 
                                             left_on='Dopasowany kod', right_on='Kod pocztowy', how='left')

        # Obliczanie sumy w df_dopasowany
        total_quantity_dopasowany = df_dopasowany['Ilość sprzedana'].sum()
        total_value_dopasowany = df_dopasowany['Wartość sprzedaży'].sum()

        st.write(f"Suma ilości dla dopasowanego: {total_quantity_dopasowany}, Suma wartości dla dopasowanego: {total_value_dopasowany}")

        # Sprawdzanie zgodności sum
        if total_quantity_ipra == total_quantity_dopasowany:
            st.write("Suma ilości zgadza się.")
        else:
            st.write("Suma ilości nie zgadza się.")

        if total_value_ipra == total_value_dopasowany:
            st.write("Suma wartości zgadza się.")
        else:
            st.write("Suma wartości nie zgadza się.")

        # Przygotowanie końcowego raportu
        df_ipra['Rok wystawienia'] = datetime.datetime.now().year
        df_ipra['Miesiąc wystawienia'] = datetime.datetime.now().month

        df_final = pd.concat([df_ipra, df_dopasowany], ignore_index=True)

        # Zapisz raport
        dzisiejsza_data = datetime.datetime.now().strftime("%d.%m.%Y")
        excel_file = io.BytesIO()
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df_final.to_excel(writer, index=False, sheet_name='Raport')
        excel_file.seek(0)

        # Udostępnienie pliku do pobrania
        nazwa_pliku = f"RAPORT GLENMARK_{dzisiejsza_data}.xlsx"
        st.download_button(
            label='PLIK RAPORTU',
            data=excel_file,
            file_name=nazwa_pliku,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        st.error("Wystąpił problem podczas przetwarzania pliku. Upewnij się, że plik ma odpowiedni format i zawiera odpowiednie kolumny.")
        st.write(f"Błąd szczegółowy: {e}")





