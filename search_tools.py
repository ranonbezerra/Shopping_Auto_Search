from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
import re

class ProductSearch():
        
    def __init__(self, product_list):

        self.database = product_list.self.database
        self.search_websites_dict = {'Google_Shopping': 'https://www.google.com/'}
        self.search_results_filename = ['Search_Results_Google_Shopping.xlsx']
        
    def google_shopping_search(self):

        self.open_window()

        with self.xlsx_writer() as self.search_results_file:

            for product in self.database['Name']:

                self.product_on_search = product
                self.open_search_website('Google_Shopping')
                self.search_product()
                self.access_shopping_page()
                search_results = self.get_search_results()
                self.generate_dataframe(search_results)
                self.export_product_sheet()

    #     with pd.ExcelWriter("Results_Google_Shopping.xlsx",engine='xlsxwriter') as google_shopping_file:

    #             busca_google_shopping(window,product)

    #             dict1,dict2 = resultados_google_shopping(window, product, db)
                
    #             df_google = dataframe_google_shopping(dict1, dict2)

    #             aba = product + '_Google'
    #             aba = correct_aba_size(aba)

    #             df_google.to_excel(google_shopping_file, sheet_name=aba, index=False)
                
    def xlsx_writer(self):
        return pd.ExcelWriter(self.search_results_filename ,engine='xlsxwriter')

    def open_window(self):
        self.chrome_window = webdriver.Chrome()
        self.chrome_window.maximize_window()

    def open_search_website(self, search_website):
        self.chrome_window.get(self.search_websites_dict[search_website])
        sleep(2)

    def search_product(self):
        self.chrome_window.find_element('xpath','/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea').send_keys(self.product_on_search, Keys.ENTER)
        sleep(2)

    def access_shopping_page(self):
        buttons_list = self.chrome_window.find_elements(By.LINK_TEXT,'Shopping')

        for button in buttons_list:
            if 'Shopping' in button.text:
                button.click()
        sleep(4)

    def get_search_results(self):

        sponsored_results = self.sponsored_results()
        other_matches = self.other_matches()

        return (sponsored_results, other_matches)

    def sponsored_results(self):
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

        dict_returned = {'Product Name': [],'Price': [],'Link': []}
        
        product_words_list, banned_words_list, min_value, max_value, banned_websites_titles = self.product_information()

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
                        dict_returned['Product Name'].append(name)
                        dict_returned['Price'].append(price)
                        dict_returned['Link'].append(link)

        return dict_returned

    def product_information(self):
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
            
        banned_words = self.database['Banned Words'][self.database['Name'] == self.product_on_search].values[0]
        min_price = self.database['Min Value'][self.database['Name'] == self.product_on_search].values[0]
        max_price = self.database['Max Value'][self.database['Name'] == self.product_on_search].values[0]
        banned_websites = self.database['Banned Websites'][self.database['Name'] == self.product_on_search].values[0]

        product = self.product_on_search.lower()
        product_words_list = product.split(' ')
                
        banned_words = str(banned_words).lower()
        banned_words_list = banned_words.split(' ')

        banned_websites = str(banned_websites).lower()
        banned_websites = banned_websites.split(' ')

        return (product_words_list,banned_words_list,min_price,max_price, banned_websites)

    def check_product_words(self, banned_words_list, product_words_list, name):
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

        has_banned_word = False
        for word in banned_words_list:
            if word in name:
                has_banned_word = True
        
        has_mandatory_words = True
        for word in product_words_list:
            if word not in name:
                has_mandatory_words = False

        return (has_mandatory_words and not has_banned_word)

    def check_banned_websites(self, banned_websites_titles, link):
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
        
        for site in banned_websites_titles:
            if site in link:
                return True
        
        return False
    
    def treat_price(self, price):
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

        price = price.replace('R$','').replace(' ','').replace('.','').replace(',','.')
        price = re.sub("[^\d\.]", "", price)

        return float(price)
    
    def other_matches(self):
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

        dict_returned = {'Product Name': [],'Price': [],'Link': []}
        product_words_list, banned_words_list, min_value, max_value, banned_websites_titles = self.product_information()
        
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
                        dict_returned['Product Name'].append(name)
                        dict_returned['Price'].append(price)
                        dict_returned['Link'].append(link)
        
        return dict_returned

    def generate_dataframe(self, search_results):
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

        dict1, dict2 = search_results

        final_dataframe = {}
        columns = ['Product Name','Price','Link']
        for column in columns:
            final_dataframe[column] = dict1[column]
            final_dataframe[column].extend(dict2[column])

        self.product_dataframe = pd.DataFrame.from_dict(final_dataframe).sort_values(by=['Price'])

    def export_product_sheet(self):
        sheetname = self.set_sheetname()
        self.product_dataframe.to_excel(self.search_results_file, sheet_name=sheetname, index=False)

    def set_sheetname(self):

        sheetname = self.product_on_search + '_Google'
        return self.correct_sheetname_size(sheetname)

    def correct_sheetname_size(self, sheetname):

        if len(sheetname) > 31:
            return sheetname[:31]
        else:
            return sheetname


if __name__ == "__main__":

    listSearch = ProductSearch('products.xlsx')
    listSearch.google_shopping_search()


