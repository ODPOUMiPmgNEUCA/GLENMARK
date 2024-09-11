'''
# Funkcja do wyszukiwania najbardziej podobnych kodów pocztowych, uwzględniająca pierwsze dwa znaki
def znajdz_podobny_kod(kod, lista_kodow, limit=1):
    prefix = kod[:2]
    # Filtracja kody pocztowe, które zaczynają się od tych samych dwóch znaków
    kody_do_porownania = [k for k in lista_kodow if k.startswith(prefix)]
    
    # Jeśli nie ma dopasowań na podstawie prefiksu, zwróć None
    if not kody_do_porownania:
        return None
    
    # Wyszukiwanie najbardziej podobnego kodu wśród przefiltrowanych
    podobny_kod = process.extractOne(kod, kody_do_porownania, scorer=fuzz.token_sort_ratio)
    return podobny_kod[0] if podobny_kod else None

# Dodanie kolumny z najbardziej podobnym kodem pocztowym
df2['Podobny kod pocztowy'] = df2['Kod pocztowy'].apply(lambda x: znajdz_podobny_kod(x, lista['Kod pocztowy']))

# Opcjonalnie: łączenie danych po znalezionym podobnym kodzie pocztowym
df2_merged = df2.merge(lista[['Kod pocztowy', 'SAP', 'Nazwa apteki', 'Miejscowość', 'Ulica', 'Nr domu']],
                       left_on='Podobny kod pocztowy', right_on='Kod pocztowy', how='left')

# Wyświetlenie wyniku
df2_merged



#TERAZ CYRK
#1 ETAP CYRKU
df2['Prefix'] = df2['Kod pocztowy'].astype(str).str[:5]
lista['Prefix'] = lista['Kod pocztowy'].astype(str).str[:5]

# Dopasowanie kodów pocztowych na podstawie pierwszych dwóch cyfr
df2 = df2.merge(lista[['Kod pocztowy', 'SAP', 'Nazwa apteki', 'Miejscowość', 'Ulica', 'Nr domu', 'Prefix']],
                       left_on='Prefix', right_on='Prefix', how='left', suffixes=('_df2', '_lista'))

# Usuwamy duplikaty, pozostawiając tylko pierwsze dopasowanie
df2 = df2.drop_duplicates(subset=['Kod pocztowy_df2'])

df2

#2 ETAP CYRKU

df2 = df2[df2['Kod pocztowy_lista'].isna()]
df2 = df2.drop('Prefix', errors = 'ignore')


df2['Prefix'] = df2['Kod pocztowy_df2'].astype(str).str[:4]
lista = lista.drop('Prefix', errors = 'ignore')
lista['Prefix'] = lista['Kod pocztowy'].astype(str).str[:4]

# Dopasowanie kodów pocztowych na podstawie pierwszych dwóch cyfr
df2 = df2.merge(lista[['Kod pocztowy', 'SAP', 'Nazwa apteki', 'Miejscowość', 'Ulica', 'Nr domu', 'Prefix']],
                       left_on='Prefix', right_on='Prefix', how='left', suffixes=('_df2', '_lista'))

# Usuwamy duplikaty, pozostawiając tylko pierwsze dopasowanie
df2 = df2.drop_duplicates(subset=['Kod pocztowy_df2'])

df2

'''
