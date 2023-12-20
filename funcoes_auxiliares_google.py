# Importando Bibliotecas

from selenium.webdriver.common.keys import Keys
from time import sleep
import pandas as pd
import re
from funcoes_auxiliares_geral import *

def busca_google_shopping(janela,produto):
    '''Na janela do Google Chrome, busca em site (http://www.google.com/) de produto específico
    e acessar aba de compras (Shopping)

    Parameters
    ----------
    janela : WebDriver obj
        Janela do Google Chrome controlado pelo WebDriver
    produto : str
        Produto que será pesquisado no site 

    Returns
    -------
        None
    '''

    janela.get('https://www.google.com/')
    janela.find_element('xpath','/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea').send_keys(produto, Keys.ENTER)
    sleep(3)
    try:
        elementos = janela.find_elements('class name','GKS7s')
    except:
        elementos = janela.find_elements('class name','MUFPAc')
            
    for item in elementos:
        print(item.text)
            
    sleep(2)

    return

def dataframe_google_shopping(dict1, dict2):
    '''Realiza construção do DataFrame do Pandas de a partir de dados da busca no Google Shopping

    Parameters
    ----------
    dict1: dictionary
        Dicionário gerado a partir da função resultados_patrocinados
    dict2: dictionary
        Dicionário gerado a partir da função outras_correspondencias
    Returns
    -------
    Pandas DataFrame obj
        DataFrame do Pandas gerado a partir dos dicionários passados como parâmetros concatenados (extendidos)
    '''

    dict_final = {}
    colunas = ['Nome do Produto','Preço','Link']
    for coluna in colunas:
        dict_final[coluna] = dict1[coluna]
        dict_final[coluna].extend(dict2[coluna])

    return pd.DataFrame.from_dict(dict_final).sort_values(by=['Preço'])

def resultados_google_shopping(janela, prod, db):
    '''Constrói os dois dicinários advindos dos dados da busca no Google Shopping, um para cada
    tipo de listagem (resultados patrocinados e outras correspondências) 

    Parameters
    ----------
    janela : WebDriver obj
        Janela do Google Chrome controlado pelo WebDriver
    prod : str
        Dicionário que será pesquisado no site outras_correspondencias
    db : Pandas DataBase obj
        Base de dados do Pandas extraída de arquivo base (buscas.xlsx)
    
    Returns:
    Tuple
        Tupla com os dicionários gerados a partir dos dados advindos da busca no Google Shopping
    '''

    dict1 = resultados_patrocinados(janela, prod, db)
    dict2 = outras_correspondencias(janela, prod, db)

    return dict1,dict2

# Função Resultados Patrocinados:

def resultados_patrocinados(janela, prod, db):
    ''' Obtém os dados da lista dos Resultados Patrocinados do Google Shopping

    Parameters
    ----------
    janela : WebDriver object
        Janela do Google Chrome controlado pelo WebDriver
    prod : str
        Dicionário que será pesquisado no site outras_correspondencias
    db : Pandas DataBase obj
        Base de dados do Pandas extraída de arquivo base (buscas.xlsx)
    
    Returns
    -------
    dict
        Dicionário gerado a partir dos dados obtidos
    '''

    dict_result = {'Nome do Produto': [],
                   'Preço':           [],
                   'Link':            []}
    
    lista_prod, lista_ban, preco_min, preco_max, sites_ban = informacoes_produto(prod,db)

    resultados  = janela.find_elements('class name','KZmu8e')
    
    for resultado in resultados:
    
        #nome do anúncio
        nome_ref    = resultado.find_element('class name','ljqwrc')
        nome_filho  = nome_ref.find_element('tag name','h3')
        nome        = nome_filho.text
        nome        = nome.lower()
    
        #Se possuir todas palavras chaves e nenhuma banida, executa código
        if checklist_ban_prod(lista_ban, lista_prod, nome):
            #Preço do anúncio
            preco = resultado.find_element('class name','T14wmb').find_element('tag name','b').text
            preco = trata_preco(preco)
    
            if preco_min <= preco <= preco_max:
                #Link do anúncio
                link_ref  = resultado.find_element('class name','ROMz4c')
                link_pai  = link_ref.find_element('xpath','..')
                link = link_pai.get_attribute('href')

                if not checklist_sites_ban(sites_ban, link):
                    dict_result['Nome do Produto'].append(nome)
                    dict_result['Preço'].append(preco)
                    dict_result['Link'].append(link)
      
    return dict_result

#Função Outras Correspondências

def outras_correspondencias(janela, prod, db):
    ''' Obtém os dados da lista dos Outras Correspondências do Google Shopping

    Parameters
    ----------
    janela : WebDriver obj
        Janela do Google Chrome controlado pelo WebDriver
    prod : str
        Dicionário que será pesquisado no site outras_correspondencias
    db : Pandas DataBase obj
        Base de dados do Pandas extraída de arquivo base (buscas.xlsx)
    
    Returns
    -------
    dict
        Dicionário gerado a partir dos dados obtidos
    '''

    dict_result = {'Nome do Produto': [],
                   'Preço':           [],
                   'Link':            []}
    lista_prod, lista_ban, preco_min, preco_max, sites_ban = informacoes_produto(prod,db)
    
    resultados  = janela.find_elements('class name','i0X6df')
    
    for resultado in resultados:
    
        #nome do anúncio
        nome = resultado.find_element('class name','tAxDx').text
        nome = nome.lower()
    
        #Se possuir todas palavras chaves e nenhuma banida, executa código
        if checklist_ban_prod(lista_ban, lista_prod, nome):
            #preço do anúncio
            preco = resultado.find_element('class name','a8Pemb').text
            preco = trata_preco(preco)
    
            if preco_min <= preco <= preco_max:
                #link do anúncio
                link_ref  = resultado.find_element('class name','bONr3b')
                link_pai  = link_ref.find_element('xpath','..')
                link = link_pai.get_attribute('href')

                if not checklist_sites_ban(sites_ban, link):
                    dict_result['Nome do Produto'].append(nome)
                    dict_result['Preço'].append(preco)
                    dict_result['Link'].append(link)
    
    return dict_result