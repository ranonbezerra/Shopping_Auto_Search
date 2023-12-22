from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import pandas as pd
from time import sleep
import re

class ProductSearch():
        
    def __init__(self, product_list):

        self.product_list = product_list
        self.search_websites = ['https://www.google.com/']
        self.search_results_filename = ['Search_Results_Google_Shopping.xlsx']
        self.NUMBER_OF_SEARCH_WEBSITES = 1
        
    def google_shopping_search(self):

        self.open_window()

        for search_website_number in range(self.NUMBER_OF_SEARCH_WEBSITES):

            with self.xlsx_writer(search_website_number) as self.search_results_file:

                for product in self.product_list.database['Name']:

                    self.product_on_search = product
                    self.open_search_website(search_website_number)
                    self.search_product()
                    self.access_shopping_page()
                    search_results = self.get_search_results()
                    self.generate_dataframe(search_results)
                    self.export_product_sheet()
                
    def xlsx_writer(self, search_website_number):
        return pd.ExcelWriter(self.search_results_filename[search_website_number] ,engine='xlsxwriter')

    def open_window(self):
        self.chrome_window = webdriver.Chrome()
        self.chrome_window.maximize_window()

    def open_search_website(self, search_website_number):
        self.chrome_window.get(self.search_websites[search_website_number])
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

        sponsored_results = self.get_sponsored_results()
        other_matches = self.get_other_matches()

        return (sponsored_results, other_matches)

    def get_sponsored_results(self):
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

        self.scrapping_location = 'Sponsored Results'
        self.product_list.set_product_information(self.product_on_search)
        resulting_webpages  = self.get_resulting_webpages()
        
        for result in resulting_webpages:
        
            name_on_webpage    = self.get_name_from_webpage(result)
            product_name       = self.treat_name_from_webpage(name_on_webpage)
        
            if self.product_list.assert_mandatory_words(product_name) and self.product_list.assert_no_banned_words(product_name):
                
                price_on_webpage = self.get_price_from_webpage(result)
                price = self.treat_price_from_webpage(price_on_webpage)
        
                if self.product_list.assert_price_in_range(price):
                    
                    link  = self.get_link_from_webpage(result)
    
                    if not self.assert_no_banned_websites(link):

                        return self.set_dataframe_dictionary(product_name, price, link)
                    
    def get_resulting_webpages(self):

        if self.scrapping_location == 'Sponsored Results':
            return self.chrome_window.find_elements('class name','KZmu8e')
        elif self.scrapping_location == 'Other Matches': 
            return self.chrome_window.find_elements('class name','i0X6df')

    def get_name_from_webpage(self, result):
        
        if self.scrapping_location == 'Sponsored Results':
            return result.find_element('class name','ljqwrc')
        elif self.scrapping_location == 'Other Matches':
            return result.find_element('class name','tAxDx').text

    def treat_name_from_webpage(self, name_on_webpage):

        name_childern     = name_on_webpage.find_element('tag name','h3')
        name              = name_childern.text
        return name.lower()

    def get_price_from_webpage(self, result):
            
        if self.scrapping_location == 'Sponsored Results':
            return result.find_element('class name','T14wmb').find_element('tag name','b').text
        elif self.scrapping_location == 'Other Matches':
            return result.find_element('class name','a8Pemb').text

    def treat_price_from_webpage(self, price):
        '''Treat the price string obtained from the website 

        Parameters
        ----------
        price : str
            Product price in string format.
        
        Returns
        -------
        Float
            Product price in float format.
            
        '''

        price = price.replace('R$','').replace(' ','').replace('.','').replace(',','.')
        price = re.sub("[^\d\.]", "", price)

        return float(price)
    
    def get_link_from_webpage(self, result):
            
        if self.scrapping_location == 'Sponsored Results':

            webpage_link = result.find_element('class name','ROMz4c')
            link_parent  = webpage_link.find_element('xpath','..')
            return link_parent.get_attribute('href')
        
        elif self.scrapping_location == 'Other Matches':

            link_reference  = result.find_element('class name','bONr3b')
            link_parent  = link_reference.find_element('xpath','..')
            return link_parent.get_attribute('href')

    def set_dataframe_dictionary(self, name, price, link):

        dict_to_return = {'Product Name': [],'Price': [],'Link': []}

        dict_to_return['Product Name'].append(name)
        dict_to_return['Price'].append(price)
        dict_to_return['Link'].append(link)

        return dict_to_return


    def get_other_matches(self):
        ''' Obtains the data from the Google Shopping websites classified by it as "Other Correpondencies"

        Parameters
        ----------
        None
        
        Returns
        -------
        dict
            Dictionry generated with the obtained data
        '''

        self.scrapping_location = 'Other Matches'
        self.product_list.set_product_information(self.product_on_search)
        
        resulting_webpages  = self.get_resulting_webpages()

        for result in resulting_webpages:
        
            name_on_webpage = self.get_name_from_webpage(result)
            product_name = self.treat_name_from_webpage(name_on_webpage)
        
            if self.product_list.assert_mandatory_words(product_name) and self.product_list.assert_no_banned_words(product_name):
                
                price_on_webpage = self.get_price_from_webpage(result)
                price = self.treat_price_from_webpage(price_on_webpage)
        
                if self.product_list.assert_price_in_range(price):
                    
                    link  = self.get_link_from_webpage(result)
    
                    if not self.product_list.assert_no_banned_websites(link):

                        return self.set_dataframe_dictionary(product_name, price, link)

    def generate_dataframe(self, search_results):
        '''Build Pandas dataframe from the google shopping search results collected, setting it to a ProductSearch attribute

        Parameters
        ----------
        search_results: tuple
            Tuple with 2 dictionaries generated from the websearch
            
        Returns
        -------
        None
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

        return sheetname[:31] if len(sheetname) > 31 else sheetname

if __name__ == "__main__":

    listSearch = ProductSearch('products.xlsx')
    listSearch.google_shopping_search()


# product_list = ProductList('buscas.xlsx')
# product_search = ProductSearch(product_list)
# product_search.google_shopping_search()