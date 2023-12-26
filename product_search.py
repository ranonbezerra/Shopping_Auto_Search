from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from data_manager import ProductList
import pandas as pd
from time import sleep
import re
from pprint import pprint

class ProductSearch():
        
    def __init__(self, product_list):

        self.product_list = product_list
        self.search_websites = ['https://www.google.com/']
        self.search_results_filename = ['Search_Results_Google_Shopping.xlsx']
        self.NUMBER_OF_SEARCH_WEBSITES = 1
        
    def shopping_list_search(self):
        ''' Execute the list search on Google Shopping

        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''

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
        ''' Create the file where the search results will be inserted later 

        Parameters
        ----------
        search_website_number : Intenger
            Index of the website being searched in the websites list
        
        Returns
        -------
        Pandas Object
            Pandas Object with data regarding the created file
        '''
        return pd.ExcelWriter(self.search_results_filename[search_website_number] ,engine='xlsxwriter')

    def open_window(self):
        ''' Open a Google Chrome window 

        Parameters
        ----------
        search_website_number : Intenger
            Index of the website being searched in the websites list
        
        Returns
        -------
        None
        '''

        self.chrome_window = webdriver.Chrome()
        self.chrome_window.maximize_window()

    def open_search_website(self, search_website_number):
        ''' Open a search website in Google Chrome window previously opened 

        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        self.chrome_window.get(self.search_websites[search_website_number])
        sleep(2)

    def search_product(self):
        ''' Execute search of product in the Google homepage 

        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        
        self.chrome_window.find_element('xpath','/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/textarea').send_keys(self.product_on_search, Keys.ENTER)
        sleep(2)

    def access_shopping_page(self):
        ''' Loads, after the search, the Google Shopping page 

        Parameters
        ----------
        None
        
        Returns
        -------
        None
        '''
        buttons_list = self.chrome_window.find_elements(By.LINK_TEXT,'Shopping')

        for button in buttons_list:
            if 'Shopping' in button.text:
                button.click()
        sleep(2)

    def get_search_results(self):
        ''' Extract the results, accordling with the parameters given in the "products.xlsx", 
        from the Google Shopping page 

        Parameters
        ----------
        None
        
        Returns
        -------
        Tuple
            Tuple with two dictionaries of each kind of result list
        '''

        sponsored_results = self.get_sponsored_results()

        other_matches = self.get_other_matches()

        return (sponsored_results, other_matches)

    def get_sponsored_results(self):
        ''' Get the data from the "Sponsored Results" list of Google Shopping

        Parameters
        ----------
        None
        
        Returns
        -------
        dict
            DataFrame Object from Pandas generated with the data obtained
        '''
        
        print('Starting to analyse values on the Sponsored List for {}'.format(self.product_on_search))

        self.scrapping_location = 'Sponsored Results'
        self.product_list.set_product_information(self.product_on_search)

        resulting_webpages  = self.get_resulting_webpages()
        dict_to_return = {'Product Name': [],'Price': [],'Link': []}
        
        for result in resulting_webpages:

            name_on_webpage    = self.get_name_from_webpage(result)
            product_name       = self.treat_name_from_webpage(name_on_webpage)
        
            if self.product_list.assert_mandatory_words(product_name) and self.product_list.assert_no_banned_words(product_name):
                price_on_webpage = self.get_price_from_webpage(result)
                price = self.treat_price_from_webpage(price_on_webpage)
        
                if self.product_list.assert_price_in_range(price):
                    link = self.get_link_from_webpage(result)
    
                    if self.product_list.assert_no_banned_websites(link):
                        dataframe_to_return = self.set_dataframe_dictionary(product_name, price, link, dict_to_return)
        if 'dataframe_to_return' in locals():
            print('Got values on the Sponsored List for {}'.format(self.product_on_search))
            return dataframe_to_return
                    
    def get_resulting_webpages(self):
        ''' Select which list from the Google Shopping to get the data

        Parameters
        ----------
        None
        
        Returns
        -------
        Selenium Object
            Selenium object with information regarding the list of results to be extracted 
        '''

        if self.scrapping_location == 'Sponsored Results':
            return self.chrome_window.find_elements('class name','KZmu8e')
        
        elif self.scrapping_location == 'Other Matches': 
            return self.chrome_window.find_elements('class name','i0X6df')

    def get_name_from_webpage(self, result):
        ''' Get the name of the product from the websearch

        Parameters
        ----------
        result : Selenium Object
            Data from the website containing the price information of one of the products results.
        
        Returns
        -------
        String
            String with the name of the product obtained from the search 
        '''
        
        if self.scrapping_location == 'Sponsored Results':
            name_on_webpage = result.find_element('class name','ljqwrc')
            name_children = name_on_webpage.find_element('tag name','h3')
            return name_children.text
        
        elif self.scrapping_location == 'Other Matches':
            return result.find_element('class name','tAxDx').text

    def treat_name_from_webpage(self, product_title):
        '''Treat the name string on the search result 

        Parameters
        ----------
        name : String
            String of the title from the product search
        
        Returns
        -------
        String
            Product title treated.
        '''
        
        return product_title.lower()

    def get_price_from_webpage(self, result):
        '''Extract the price string of on of the search results obtained from the website 

        Parameters
        ----------
        result : Selenium Object
            Data from the website containing the price information of one of the products results.
        
        Returns
        -------
        String
            Product price in float format.
        '''
            
        if self.scrapping_location == 'Sponsored Results':
            return result.find_element('class name','T14wmb').find_element('tag name','b').text
        
        elif self.scrapping_location == 'Other Matches':
            return result.find_element('class name','kHxwFf').text

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

        price = price[:price.find(',')+3]
        price = price.replace('R$','').replace(' ','').replace('.','').replace(',','.')
        price = re.sub("[^\d\.]", "", price)
        return float(price)
    
    def get_link_from_webpage(self, result):
        '''Extract the price string of on of the search results obtained from the website 

        Parameters
        ----------
        result : Selenium Object
            Data from the website containing the link information of one of the products results.
        
        Returns
        -------
        String
            String with the link of the product.
        '''
            
        if self.scrapping_location == 'Sponsored Results':

            webpage_link = result.find_element('class name','ROMz4c')
            link_parent  = webpage_link.find_element('xpath','..')
            return link_parent.get_attribute('href')
        
        elif self.scrapping_location == 'Other Matches':

            link_reference  = result.find_element('class name','bONr3b')
            link_parent  = link_reference.find_element('xpath','..')
            return link_parent.get_attribute('href')

    def set_dataframe_dictionary(self, name, price, link, dict_to_return):

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

        print('Starting to analyse values on the Others List for {}'.format(self.product_on_search))

        self.scrapping_location = 'Other Matches'
        self.product_list.set_product_information(self.product_on_search)

        resulting_webpages  = self.get_resulting_webpages()
        dict_to_return = {'Product Name': [],'Price': [],'Link': []}

        for result in resulting_webpages:
        
            name_on_webpage = self.get_name_from_webpage(result)
            product_name = self.treat_name_from_webpage(name_on_webpage)
        
            if self.product_list.assert_mandatory_words(product_name) and self.product_list.assert_no_banned_words(product_name):
                
                price_on_webpage = self.get_price_from_webpage(result)
                price = self.treat_price_from_webpage(price_on_webpage)
        
                if self.product_list.assert_price_in_range(price):
                    
                    link  = self.get_link_from_webpage(result)
    
                    if self.product_list.assert_no_banned_websites(link):
                        dataframe_to_return =  self.set_dataframe_dictionary(product_name, price, link, dict_to_return)
        if 'dataframe_to_return' in locals():
            print('Got values on the Others List for {}'.format(self.product_on_search))
            return dataframe_to_return

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

        if not dict1:
            dict1 = {'Product Name': [],
                        'Price': [],
                        'Link': []}
        if not dict2:
            dict2 = {'Product Name': [],
                        'Price': [],
                        'Link': []}

        final_dataframe = {}
        columns = ['Product Name','Price','Link']
        for column in columns:
            final_dataframe[column] = dict1[column]
            final_dataframe[column].extend(dict2[column])

        self.product_dataframe = pd.DataFrame.from_dict(final_dataframe).sort_values(by=['Price'])

    def export_product_sheet(self):
        '''Execute the extraction of the results into a sheet inside of a file in XLSX format

        Parameters
        ----------
        None
            
        Returns
        -------
        None
        '''

        sheetname = self.set_sheetname()
        self.product_dataframe.to_excel(self.search_results_file, sheet_name=sheetname, index=False)

    def set_sheetname(self):
        '''Sets sheetname for the product being extracted

        Parameters
        ----------
        None
            
        Returns
        -------
        String
            String with the sheet name
        '''


        sheetname = self.product_on_search + '_Google'
        return self.correct_sheetname_size(sheetname)

    def correct_sheetname_size(self, sheetname):
        '''Treat sheetname string

        Parameters
        ----------
        sheetname : String
            String with the sheetname non treated
            
        Returns
        -------
        String
            String with the sheet name treated
        '''


        return sheetname[:31] if len(sheetname) > 31 else sheetname

if __name__ == "__main__":

    product_list   = ProductList('products.xlsx')
    product_search = ProductSearch(product_list)
    product_search.shopping_list_search()