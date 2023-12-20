import re
# import win32com.client as win32
import smtplib
from email.message import EmailMessage

def check_banned_words(lista_ban, lista_prod, nome):
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

def checklist_sites_ban(sites_ban, link):
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
    
def correct_aba_size(aba):
    '''Trata título da aba da planilha do excel gerado

    Parameters
    ----------
    aba : str
        Título previsto da aba.
    
    Returns
    -------
    String
        Título da aba tratado para que fique no tamanho máximo de 32 caracteres.
        
    '''

    if len(aba) > 31:
        return aba[:31]
    else:
         return aba
    
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

def enviar_email(df, produto, site, emails):
    '''Envia email com tabelas geradas na pesquisa do produto

    Parameters
    ----------
    df : Pandas DataFrame obj
        DataFrame do Pandas com todos os valores encontrados dentro dos parâmetros do produto especificado.
    produto : str
        Nome do produto.
    site : str
        Site em que pesquisa foi realizada.
    emails : list
        Lista de emails que receberam pesquisa.
    
    Returns
    -------
    None
        
    '''

    # outlook = win32.Dispatch('outlook.application')
    # mail = outlook.CreateItem(0)
    # mail.To = email
    # mail.Subject = f' Pesquisa de Preço Automatizada - {produto} - {site}'
    # mail.HTMLBody = f"""
    #                 <p>Prezado,</p>
    #                 <p>Segue tabela dos valores encontrados no {site}:</p>
    #                 {df.to_html(index=False)}
    #                  <p>Att,</p>
    #                  """
    # mail.Send()
    
    sender = "ranonbezerra@hotmail.com"
    recipient = emails
    message = f"""
                <p>Prezado,</p>
                <p>Segue tabela dos valores encontrados no {site}:</p>
                {df.to_html(index=False)}
                <p>Att,</p>
                """

    email = EmailMessage()
    email["From"] = sender
    email["To"] = recipient
    email["Subject"] = f'Pesquisa de Preço Automatizada - {produto} - {site}'
    email.set_content(message, subtype="html")

    smtp = smtplib.SMTP("smtp-mail.outlook.com", 587)
    smtp.starttls()
    smtp.login(sender, "Milka@2019")
    smtp.sendmail(sender, recipient, email.as_string())
    smtp.quit()

    return


