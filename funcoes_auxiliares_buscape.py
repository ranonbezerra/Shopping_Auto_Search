# Importando Bibliotecas

from selenium.webdriver.common.keys import Keys
from time import sleep
import pandas as pd
import re
from funcoes_auxiliares_geral import *

def busca_buscape(janela,produto):
    '''Na janela do Google Chrome, busca em site (http://www.buscape.com.br/) de produto específico
    e executa busca

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

    janela.get('https://www.buscape.com.br/')
    janela.find_element('xpath','/html/body/div[1]/header/div[1]/div/div/div[3]/div/div/div[2]/div/div[1]/input').send_keys(produto, Keys.ENTER)
    sleep(3)
    

    return

def dataframe_buscape(dict_buscape):
    '''Realiza construção do DataFrame do Pandas a partir de dados da busca no BuscaPé

    Parameters
    ----------
    dict_buscape: dictionary
        Dicionário gerado a partir da função resultados_patrocinados

    Returns
    -------
    Pandas DataFrame obj
        DataFrame do Pandas gerado a partir dos dicionário passado
    '''
    
    return pd.DataFrame.from_dict(dict_buscape).sort_values(by=['Preço'])

def resultados_buscape(janela, prod, db):
    '''Constrói dicinário advindo dos dados da busca no BuscaPé

    Parameters
    ----------
    janela : WebDriver obj
        Janela do Google Chrome controlado pelo WebDriver
    prod : str
        Dicionário que será pesquisado no site outras_correspondencias
    db : Pandas DataBase obj
        Base de dados do Pandas extraída de arquivo base (buscas.xlsx)
    
    Returns:
    Dictionary
        Dicionário gerado a partir dos dados advindos da busca no BuscaPé
    '''

    dict_result = {'Nome do Produto': [],
                   'Preço':           [],
                   'Link':            []}
    
    lista_prod, lista_ban, preco_min, preco_max, sites_ban = informacoes_produto(prod,db)

    resultados = janela.find_elements('class name','ProductCard_ProductCard_Inner__tsD4M')  
    
    for resultado in resultados:
    
        #nome do anúncio
        nome        = resultado.find_element('class name','ProductCard_ProductCard_Name__LT7hv').text
        nome        = nome.lower()
    
        #Se possuir todas palavras chaves e nenhuma banida, executa código
        if checklist_ban_prod(lista_ban, lista_prod, nome):
            #Preço do anúncio
            preco = resultado.find_element('class name','Text_MobileHeadingS__Zxam2').text
            preco = trata_preco(preco)
            
            if preco_min <= preco <= preco_max:
                #Link do anúncio
                link = resultado.get_attribute('href')

                if not checklist_sites_ban(sites_ban, link):
                    dict_result['Nome do Produto'].append(nome)
                    dict_result['Preço'].append(preco)
                    dict_result['Link'].append(link)
      
    return dict_result