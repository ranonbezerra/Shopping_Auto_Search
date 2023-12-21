from search_tools import ProductSearch

def execute_product_research():

    # Abrindo navegador e importando dados
    product_search = ProductSearch('buscas.xlsx')
    product_search.google_shopping_search()