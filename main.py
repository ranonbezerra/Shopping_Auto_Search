from search_tools import ProductSearch

def execute_product_research():

    # Abrindo navegador e importando dados
    listSearch = ProductSearch('buscas.xlsx')
    listSearch.google_shopping_search()