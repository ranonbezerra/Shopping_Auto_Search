from product_search import ProductSearch
from data_manager import ProductList

product_list = ProductList('products.xlsx')
product_search = ProductSearch(product_list)
product_search.shopping_list_search()