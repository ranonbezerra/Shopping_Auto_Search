from selenium import webdriver
import pandas as pd
from funcoes_auxiliares_google import *
from funcoes_auxiliares_buscape import *
from search_tools import open_window, ProductSearch

def execute_product_research():

    # Abrindo navegador e importando dados
    listSearch = ProductSearch('buscas.xlsx')
    listSearch.search_on_google_shopping(window)


#     with pd.ExcelWriter("Results_Google_Shopping.xlsx",engine='xlsxwriter') as google_shopping_file:
#         # Realização do loop para pesquisa e entrada na aba Shopping

#         for prod in db['Nome']:

#             busca_google_shopping(window,prod)

#             dict1,dict2 = resultados_google_shopping(window, prod, db)
            
#             df_google = dataframe_google_shopping(dict1, dict2)

#             aba = prod + '_Google'
#             aba = correct_aba_size(aba)

#             df_google.to_excel(google_shopping_file, sheet_name=aba, index=False)
#             #enviar_email(df_google, prod, 'Google Shopping', email)

#     with pd.ExcelWriter("Resultados_BuscaPe.xlsx",engine='xlsxwriter') as arquivo_final_buscape:
#         # Realização do loop para pesquisa e entrada na aba Shopping

#         for prod in db['Nome']:

#             busca_buscape(window,prod)

#             dict_buscape = resultados_buscape(window, prod, db)
            
#             df_buscape = dataframe_buscape(dict_buscape)

#             aba = prod + '_BuscaPe'
#             aba = correct_aba_size(aba)

#             df_buscape.to_excel(arquivo_final_buscape, sheet_name=aba, index=False)
#             #enviar_email(df_buscape, prod, 'BuscaPé', email)

# if __name__ == "__main__":
#     execute_product_research()