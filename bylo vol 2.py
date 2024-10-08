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


if df_file:
    try:
        # Załaduj plik główny oraz listę aptek
        df = pd.read_excel(df_file)
        lista = pd.read_excel('Lista aptek Glenmark_.xlsx')

        # Utwórz flagę, czy kod pocztowy jest na liście
        df['Czy w liście'] = df['Kod pocztowy'].isin(lista['Kod pocztowy'])

        # Unikalne kody z listy aptek
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
        df['Dopasowany kod'] = None
        
        # Sprawdzamy tylko te wiersze, które mają Rodzaj promocji 'IPRA' i nie są na liście
        for index, row in df.iterrows():
            if row['Rodzaj promocji'] == 'IPRA' and not row['Kod pocztowy'] in kody:
                df.at[index, 'Dopasowany kod'] = dopasuj_inny_kod_pocztowy(row['Kod pocztowy'], kody)
            else:
                df.at[index, 'Dopasowany kod'] = row['Kod pocztowy']  # Zachowaj oryginalny kod

        # Dodaj dane aptek na podstawie dopasowanego kodu
        df_dopasowany = df.merge(lista_unique[['Kod pocztowy', 'SAP', 'Nazwa apteki', 'Miejscowość', 'Ulica', 'Nr domu']],
                                  left_on='Dopasowany kod', right_on='Kod pocztowy', how='left',
                                  suffixes=('', '_dopasowany'))

        # Przygotuj wynik do zapisu
        df_dopasowany.drop(columns=['Kod pocztowy_dopasowany', 'SAP', 'Nazwa apteki', 'Miejscowość', 'Ulica', 'Nr domu'], inplace=True)
        
        # Zapisz wynikowy plik do pobrania
        excel_file = io.BytesIO()
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df_dopasowany.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_file.seek(0)

        # Udostępnij plik do pobrania w aplikacji Streamlit
        st.download_button(
            label='PLIK RAPORTU CENTRALNY (1)',
            data=excel_file,
            file_name=f"RAPORT GLENMARK OSTATECZNY_{datetime.datetime.now().strftime('%d.%m.%Y')}.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        # Obsługa błędów i wyświetlanie komunikatu o błędzie
        st.error("Wystąpił problem podczas przetwarzania pliku. Upewnij się, że plik ma odpowiedni format i zawiera odpowiednie kolumny.")
        st.write(f"Błąd szczegółowy: {e}")

if df_file:
    try:
        df = pd.read_excel(df_file)
        lista = pd.read_excel('Lista aptek Glenmark_.xlsx')

        # Przetwarzanie danych
        df = df[df['Rodzaj promocji'] == 'IPRA']
        df = df.groupby(['Kod pocztowy', 'Indeks', 'Nazwa towaru']).agg({
            'Ilość sprzedana': 'sum',
            'Wartość sprzedaży': 'sum'
        }).reset_index()

        # Zidentyfikuj, czy kody pocztowe są w liście
        df['Czy w liście'] = df['Kod pocztowy'].isin(lista['Kod pocztowy'])

        # Wydziel dane w liście
        df1 = df[df['Czy w liście'] == True]
        df2 = df[df['Czy w liście'] == False]

        # Dodaj dane aptek dla df1
        lista_unique = lista.drop_duplicates(subset=['Kod pocztowy'])
        df1 = df1.merge(lista_unique[['Kod pocztowy', 'SAP', 'Nazwa apteki', 'Miejscowość', 'Ulica', 'Nr domu']],
                         on='Kod pocztowy', how='left')

        # Przygotuj dane do eksportu
        new_order = ['SAP', 'Nazwa apteki', 'Miejscowość', 'Ulica', 'Nr domu', 'Kod pocztowy', 'Indeks', 'Nazwa towaru', 'Ilość sprzedana', 'Wartość sprzedaży']
        df1 = df1[new_order]

        # Zapisywanie raportu
        dzisiejsza_data = datetime.datetime.now().strftime("%d.%m.%Y")

        st.write('Kliknij, aby pobrać plik z raportem:')
        excel_file = io.BytesIO()
        with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
            df1.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_file.seek(0)

        nazwa_pliku = f"RAPORT GLENMARK_{dzisiejsza_data}.xlsx"
        st.download_button(
            label='PLIK RAPORTU (1)',
            data=excel_file,
            file_name=nazwa_pliku,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        st.error("Wystąpił problem podczas przetwarzania pliku. Upewnij się, że plik ma odpowiedni format i zawiera odpowiednie kolumny.")
        st.write(f"Błąd szczegółowy: {e}")












