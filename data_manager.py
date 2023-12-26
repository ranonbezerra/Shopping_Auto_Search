import pandas as pd
import re


class ProductList():

    def __init__(self, db_filename):

        self.database = pd.read_excel(db_filename)

    def set_product_information(self, product_on_search):
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
            
        self.min_price = self.database['Min Value'][self.database['Name'] == product_on_search].values[0]
        self.max_price = self.database['Max Value'][self.database['Name'] == product_on_search].values[0]
        
        banned_words = self.database['Banned Words'][self.database['Name'] == product_on_search].values[0]
        banned_websites = self.database['Banned Websites'][self.database['Name'] == product_on_search].values[0]

        product = product_on_search.lower()
        self.product_words_list = product.split(' ')
                
        banned_words = str(banned_words).lower()
        self.banned_words_list = banned_words.split(' ')

        banned_websites = str(banned_websites).lower()
        self.banned_websites = banned_websites.split(' ')

    def assert_mandatory_words(self, name):
        '''Confere se o produto encontrado possui algum item proibitivo ou faltante em sua nomenclatura 

        Parameters
        ----------
        name : str
            Nome do produto na listagem do site analisado.
        
        Returns
        -------
        Boolean
            True se não encontrar palavras proibidas ou nenhuma das obrigatórias estiver faltando, False caso contrário
        '''

        has_mandatory_words = True
        for word in self.product_words_list:
            if word not in name:
                has_mandatory_words = False

        return has_mandatory_words
    
    def assert_no_banned_words(self, name):

        has_no_banned_word = True
        for word in self.banned_words_list:
            if word in name:
                has_no_banned_word = False
        return has_no_banned_word
    
    def assert_price_in_range(self, price):
        return self.min_price <= price <= self.max_price

    def assert_no_banned_websites(self, link):
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
        for site in self.banned_websites:
            if site in link:
                return False
        return True
    
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