from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
from funcoes_auxiliares_geral import *
import pprint

class ProductSearch():
        
    def __init__(self, db_filename):
        self.db = pd.read_excel(db_filename)
        self.search_websites_dict = {'Google_Shopping': 'https://www.google.com/',
                                     'BuscaPe': 'https://www.buscape.com.br/'}

    def google_shopping_search(self):

        self.open_window()

        for product in self.db['Name']:

            self.open_search_website('Google_Shopping')
            self.search_product(product)
            self.click_shopping_page()
            self.sponsored_results(product)

    #     with pd.ExcelWriter("Results_Google_Shopping.xlsx",engine='xlsxwriter') as google_shopping_file:

        

    #             busca_google_shopping(window,product)

    #             dict1,dict2 = resultados_google_shopping(window, product, db)
                
    #             df_google = dataframe_google_shopping(dict1, dict2)

    #             aba = product + '_Google'
    #             aba = correct_aba_size(aba)

    #             df_google.to_excel(google_shopping_file, sheet_name=aba, index=False)

    def open_window(self):
        self.chrome_window = webdriver.Chrome()
        self.chrome_window.maximize_window()

    def open_search_website(self, search_website):
        self.chrome_window.get(self.search_websites_dict[search_website])
        sleep(2)

    def search_product(self, product):
        self.chrome_window.find_element('xpath','/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea').send_keys(product, Keys.ENTER)
        sleep(2)

    def click_shopping_page(self):
        buttons_list = self.chrome_window.find_elements(By.LINK_TEXT,'Shopping')

        for button in buttons_list:
            if 'Shopping' in button.text:
                button.click()
        sleep(4)

    def sponsored_results(self, product):
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
        
        lista_prod, lista_ban, preco_min, preco_max, sites_ban = informacoes_produto(product,self.db)

        resultados  = self.chrome_window.find_elements('class name','KZmu8e')
        
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
        
        pprint.pprint(dict_result)


if __name__ == "__main__":

    listSearch = ProductSearch('products.xlsx')
    listSearch.google_shopping_search()

    # def search_product(self, window, product):
    #     window.find_element('xpath','/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea').send_keys(product, Keys.ENTER)

    # def busca_google_shopping(window,product):
    #     '''Na janela do Google Chrome, busca em site (http://www.google.com/) de produto específico
    #     e acessar aba de compras (Shopping)

    #     Parameters
    #     ----------
    #     janela : WebDriver obj
    #         Janela do Google Chrome controlado pelo WebDriver
    #     produto : str
    #         Produto que será pesquisado no site 

    #     Returns
    #     -------
    #         None
    #     '''

    #     self.open_google_website(window)
    #     self.search_product(window, product)
    #     sleep(3)
    #     try:
    #         elementos = janela.find_elements('class name','GKS7s')
    #     except:
    #         elementos = janela.find_elements('class name','MUFPAc')
                
    #     for item in elementos:
    #         if 'Shopping' == item.text:
    #             item.click()
    #             break
                
    #     sleep(2)
          


