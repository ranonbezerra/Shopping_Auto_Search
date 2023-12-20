from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
import pprint
import re

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
            self.access_shopping_page()
            self.sponsored_results(product)
            self.other_matches(product)

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

    def access_shopping_page(self):
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

        dict_result = {'Product Name': [],'Price': [],'Link': []}
        
        product_words_list, banned_words_list, min_value, max_value, banned_websites_titles = self.product_information(product)

        results  = self.chrome_window.find_elements('class name','KZmu8e')
        
        for result in results:
        
            #nome do anúncio
            name_reference    = result.find_element('class name','ljqwrc')
            name_childern  = name_reference.find_element('tag name','h3')
            name        = name_childern.text
            name        = name.lower()
        
            #Se possuir todas palavras chaves e nenhuma banida, executa código
            if self.check_product_words(banned_words_list, product_words_list, name):
                #Preço do anúncio
                price = result.find_element('class name','T14wmb').find_element('tag name','b').text
                price = self.treat_price(price)
        
                if min_value <= price <= max_value:
                    #Link do anúncio
                    link_reference  = result.find_element('class name','ROMz4c')
                    link_parent  = link_reference.find_element('xpath','..')
                    link = link_parent.get_attribute('href')

                    if not self.check_banned_websites(banned_websites_titles, link):
                        dict_result['Product Name'].append(name)
                        dict_result['Price'].append(price)
                        dict_result['Link'].append(link)
        
        pprint.pprint(dict_result)

    def product_information(self, product):
        '''Retorna informações tratadas do produto advindas de Banco de Dados 

        Parameters
        ----------
        produto : list
            Nome do produto no banco de dados.
        
        Returns
        -------
        Tuple
            Tupla com lista de cada string já tratada no nome do produto, lista de strings proibidas no nome do produto,
            preço mínimo do produto, preço máximo do propduto e lista de sites proibidos
        '''
            
        banned_words = self.db['Banned Words'][self.db['Name'] == product].values[0]
        min_price = self.db['Min Value'][self.db['Name'] == product].values[0]
        max_price = self.db['Max Value'][self.db['Name'] == product].values[0]
        banned_websites = self.db['Banned Websites'][self.db['Name'] == product].values[0]

        product = product.lower()
        product_words_list = product.split(' ')
                
        banned_words = str(banned_words).lower()
        banned_words_list = banned_words.split(' ')

        banned_websites = str(banned_websites).lower()
        banned_websites = banned_websites.split(' ')

        return (product_words_list,banned_words_list,min_price,max_price, banned_websites)

    def check_product_words(self, lista_ban, lista_prod, nome):
        '''Confere se o produto encontrado possui algum item proibitivo ou faltante em sua nomenclatura 

        Parameters
        ----------
        lista_ban : list
            Lista de strings (palavras) proibidas no nome do produto. Lista advinda de base de dados lida previamente.
        lista_prod : list
            Lista de strings (palavras) obrigatórias no nome do produto. Lista advinda de base de dados lida previamente.
        nome : str
            Nome do produto na listagem do site analisado.
        
        Returns
        -------
        Boolean
            True se não encontrar palavras proibidas ou nenhuma das obrigatórias estiver faltando, False caso contrário
        '''

        possui_ban = False
        for palavra in lista_ban:
            if palavra in nome:
                possui_ban = True
        
        possui_prod = True
        for palavra in lista_prod:
            if palavra not in nome:
                possui_prod = False

        return (possui_prod and not possui_ban)

    def check_banned_websites(self, sites_ban, link):
        '''Confirma se o site não está na lista dos proibidos

        Parameters
        ----------
        sites_ban : list
            Lista de strings (título dos sites) proibidos. Lista advinda de base de dados lida previamente.
        link : str
            Link completo do site advindo da pesquisa.
        
        Returns
        -------
        Boolean
            True se não encontrar site proibido, False caso contrário
        '''
        
        for site in sites_ban:
            if site in link:
                return True
        
        return False
    
    def treat_price(preco):
        '''Trata string do preço advinda da pesquisa nos sites 

        Parameters
        ----------
        preco : str
            Preço do produto no formato str.
        
        Returns
        -------
        Float
            Valor do preço do produto no formato correto.
            
        '''

        preco = preco.replace('R$','').replace(' ','').replace('.','').replace(',','.')
        preco = re.sub("[^\d\.]", "", preco)

        return float(preco)
    
    def other_matches(self, product):
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

        dict_result = {'Product Name': [],'Price': [],'Link': []}
        product_words_list, banned_words_list, min_value, max_value, banned_websites_titles = self.product_information(product,self.db)
        
        results  = self.chrome_window.find_elements('class name','i0X6df')
        
        for result in results:
        
            #nome do anúncio
            name = result.find_element('class name','tAxDx').text
            name = name.lower()
        
            #Se possuir todas palavras chaves e nenhuma banida, executa código
            if self.check_product_words(banned_words_list, product_words_list, name):
                #preço do anúncio
                price = result.find_element('class name','a8Pemb').text
                price = self.treat_price(price)
        
                if min_value <= price <= max_value:
                    #link do anúncio
                    link_reference  = result.find_element('class name','bONr3b')
                    link_parent  = link_reference.find_element('xpath','..')
                    link = link_parent.get_attribute('href')

                    if not self.check_banned_websites(banned_websites_titles, link):
                        dict_result['Product Name'].append(name)
                        dict_result['Price'].append(price)
                        dict_result['Link'].append(link)
        
        return dict_result



if __name__ == "__main__":

    listSearch = ProductSearch('products.xlsx')
    listSearch.google_shopping_search()

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
          


