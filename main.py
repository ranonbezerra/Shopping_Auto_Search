from search_tools import ProductSearch
from data_manager import ProductList

product_list = ProductList('buscas.xlsx')
product_search = ProductSearch(product_list)
product_search.google_shopping_search()

