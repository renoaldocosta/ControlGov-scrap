from datetime import datetime
import calendar
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import lxml.html
import json
import pytz
from datetime import datetime
import time
import random
import sys
from pymongo.mongo_client import MongoClient
import os
from dotenv import load_dotenv
# Funcionando Pega tudas as informações da página de detalhes.
# 
# Pega link de detalhes.

#url = 'https://portal.sitesagapesistemas.com.br/agape2/portal/ext/despesa/?alias=cmpinhao&p=iDespesa&base=670&tipo=empenho&ano=2024&i=95&a=detalhes'
def pegar_detalhes(url):
    data_hora_acesso = datetime.now()
    HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    resp = requests.get(url, headers = HEADER, timeout=30)
    resp.raise_for_status()
    soup = bs(resp.text, 'lxml')


    # Encontrar apos Identificação: numero, Natureza de Crédito, Data do Empenho, Tipo de Empenho
    numero = soup.find('h2', string='Identificação').find_next('table').find_next('td', string='Número:').find_next('td').text
    Natureza_de_Crédito = soup.find('h2', string='Identificação').find_next('table').find_next('td', string='Natureza de Crédito:').find_next('td').text
    Data_do_Empenho = soup.find('h2', string='Identificação').find_next('table').find_next('td', string='Data do Empenho:').find_next('td').text
    Tipo_de_Empenho= soup.find('h2', string='Identificação').find_next('table').find_next('td', string='Tipo de Empenho:').find_next('td').text

    print('========== # Identificação: ==========')
    print('Número:', numero)
    print('Natureza de Crédito:', Natureza_de_Crédito)
    print('Data do Empenho:', Data_do_Empenho)
    print('Tipo de Empenho:', Tipo_de_Empenho)

    df_identicacao = pd.DataFrame({'Número': [numero], 'Natureza de Crédito': [Natureza_de_Crédito], 'Data do Empenho': [Data_do_Empenho], 'Tipo de Empenho': [Tipo_de_Empenho]})
    df_identicacao.head()



    # ===============================================

    # Encontrar apos Dotação: Poder, Função, Elemento de Despesa, Unid. Administradora, Subfunção, Subelemento, Unid. Orçamentária, Fonte de recurso, Projeto/Atividade

    Poder = soup.find('h2', string='Dotação').find_next('table').find_next('td', string='Poder:').find_next('td').text
    Função = soup.find('h2', string='Dotação').find_next('table').find_next('td', string='Função:').find_next('td').text
    Elemento_de_Despesa = soup.find('h2', string='Dotação').find_next('table').find_next('td', string='Elemento de Despesa:').find_next('td').text
    Unid_Administradora = soup.find('h2', string='Dotação').find_next('table').find_next('td', string='Unid. Administradora:').find_next('td').text
    Subfunção = soup.find('h2', string='Dotação').find_next('table').find_next('td', string='Subfunção:').find_next('td').text
    Subelemento = soup.find('h2', string='Dotação').find_next('table').find_next('td', string='Subelemento:').find_next('td').text
    Unid_Orçamentária = soup.find('h2', string='Dotação').find_next('table').find_next('td', string='Unid. Orçamentária:').find_next('td').text
    Fonte_de_recurso = soup.find('h2', string='Dotação').find_next('table').find_next('td', string='Fonte de recurso:').find_next('td').text
    Projeto_Atividade = soup.find('h2', string='Dotação').find_next('table').find_next('td', string='Projeto/Atividade').find_next('td').text



    # ===============================================

    # Encontrar apos Outras Informações: Categorias de base legal

    Categorias_base_legal = soup.find('h2', string='Outras Informações').find_next('table').find_next('td', string='Categorias de base legal').find_next('td').text


    # ==============================================

    # Encontrar apos Financeiro: Alteração, Empenhado, Liquidado, Pago, Histórico

    Alteracao = soup.find('h2', string='Financeiro').find_next('table').find_next('td', string='Alteração').find_next('td').text
    Empenhado = soup.find('h2', string='Financeiro').find_next('table').find_next('td', string='Empenhado').find_next('td').text
    Liquidado = soup.find('h2', string='Financeiro').find_next('table').find_next('td', string='Liquidado').find_next('td').text
    Pago = soup.find('h2', string='Financeiro').find_next('table').find_next('td', string='Pago').find_next('td').text
    Historico = soup.find('h2', string='Financeiro').find_next('table').find_next('td', string='Histórico').find_next('td').text

    # ==============================================

    # Encontrar apos Item(ns): 


    def pegar_nome_das_colunas(soup):
        column_names = [x.text for x in soup.find_next('tr') if x.text != '\n']
        return column_names


    def pegar_dados(soup):
        item_list = []
        itens = [item.text.split('\n') for item in soup.find('h2', string='Item(ns)').find_next('table') if item.text != '\n']
        itens = [item[1:-1] for item in itens]
        return itens[1:]

    table = soup.find('h2', string='Item(ns)').find_next('table')
    colunas = pegar_nome_das_colunas(table)
    linhas = pegar_dados(soup)

    itens = [colunas, linhas]

    # print('========== # Dotação: ==========')
    # print('Poder:', Poder)
    # print('Função:', Função)
    # print('Elemento de Despesa:', Elemento_de_Despesa)
    # print('Unid. Administradora:', Unid_Administradora)
    # print('Subfunção:', Subfunção)
    # print('Subelemento:', Subelemento)
    # print('Unid. Orçamentária:', Unid_Orçamentária)
    # print('Fonte de recurso:', Fonte_de_recurso)
    # print('Projeto/Atividade:', Projeto_Atividade)
    # print('========== # Outras Informações: ==========')
    # print('Categorias de base legal:', Categorias_base_legal)
    # print('========== # Financeiro: ==========')
    # print('Alteração:', Alteracao)
    # print('Empenhado:', Empenhado)
    # print('Liquidado:', Liquidado)
    # print('Pago:', Pago)
    # print('Histórico:', Historico)
    # print('========== # Item(ns): ==========')
    # print(itens)


    df_dotação = pd.DataFrame({'Poder': [Poder], 'Função': [Função], 'Elemento de Despesa': [Elemento_de_Despesa], 'Unid. Administradora': [Unid_Administradora], 'Subfunção': [Subfunção], 'Subelemento': [Subelemento], 'Unid. Orçamentária': [Unid_Orçamentária], 'Fonte de recurso': [Fonte_de_recurso], 'Projeto/Atividade': [Projeto_Atividade], 'Categorias de base legal': [Categorias_base_legal], 'Alteração': [Alteracao], 'Empenhado': [Empenhado], 'Liquidado': [Liquidado], 'Pago': [Pago], 'Histórico': [Historico], 'Item(ns)': [itens]})
    return df_dotação
#url = 'https://portal.sitesagapesistemas.com.br/agape2/portal/ext/despesa/?alias=cmpinhao&p=iDespesa&base=670&tipo=empenho&ano=2024&i=95&a=detalhes'
#dicionario = pegar_detalhes(url)


def raspar_dados(pg, mes, ano, datade, dataate) -> bs:
    url = f'https://portal.sitesagapesistemas.com.br/agape2/portal/ext/despesa/?tipo_arq=&alias=cmpinhao&p=iDespesa&filtro=3&pg={pg}&mes={mes}&ano={ano}&datade={datade}&dataate={dataate}&tipo=empenho&credor=&classificacao=&documento=&v='
    print(url)
    HEADER = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"}
    try:
        resp = requests.get(url, headers = HEADER, timeout=30)
        resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    soup = bs(resp.text, 'lxml')
    return soup


def pegar_nome_das_colunas(soup):
    table_tag = soup.table
    column_names = [x.text for x in table_tag.thead.tr.find_all('strong') if x.text != '']
    column_names = column_names[:8]
    column_names.append('link_Detalhes')
    return column_names

def pegar_dados(soup):
    despesas = soup.select('table > tbody > tr ')
    rows = []
    for despesa in despesas:
        list_despesas=[]
        list_despesas = [x for x in despesa.stripped_strings]
        list_despesas = list_despesas[1:9]
        links_alias = despesa.find_all('a', href=lambda href: href and href.startswith('?alias'))
        links_alias = 'https://portal.sitesagapesistemas.com.br/agape2/portal/ext/despesa/'+links_alias[0].get('href').replace('amp;', '')
        list_despesas.append(links_alias)
        rows.append(list_despesas)
    return rows

def pegar_ultima_pagina(soup):
    try:
        last_page = max([int(x.text) for x in soup.select('div[id="paginacao"] ul[class="pagination pointer"] li') if x.text.isdigit()])
    except:
        print('Erro ao pegar a última página. Não há páginas para serem raspadas.')
        last_page = 1
    return last_page




def main(pg, mes, ano, datade, dataate):
    soup = raspar_dados(pg, mes, ano, datade, dataate)
    column_names = pegar_nome_das_colunas(soup)
    rows = pegar_dados(soup )
    df = pd.DataFrame(rows, columns=column_names)
    return df


def ultimo_dia_mes(ano: int, mes: int) -> int:
    # O método monthrange retorna uma tupla (primeiro_dia_da_semana, ultimo_dia_do_mes)
    ultimo_dia = calendar.monthrange(ano, mes)[1]
    return ultimo_dia


def mes_atual_somado(somar_mes: int) -> str:
    now = datetime.now()
    mes = now.strftime('%m')
    mes = int(mes) + somar_mes

    # Verifica se o mês é maior que 12, para garantir que permanece dentro do intervalo válido de meses
    while mes > 12:
        mes -= 12

    # Formata o mês com duas casas decimais
    mes = str(mes).zfill(2)
    return mes

def obter_mes_atual_e_anterior() -> (str, str):
    """
    Função para obter o mês atual e o mês anterior com duas casas decimais.
    Retorna uma tupla (mes_atual, mes_anterior).
    """
    mes_atual = mes_atual_somado(0).zfill(2)
    mes_anterior = mes_atual_somado(-1).zfill(2)
    return mes_atual, mes_anterior

def obter_intervalo_datas(mes_atual, mes_anterior, ano_atual) -> (str, str):
    """
    Função para definir o intervalo de datas baseado no mês atual.
    Retorna as variáveis 'datade' e 'dataate'.
    """
    ano_de_datade = ano_atual - 1 if int(mes_atual) == 1 else ano_atual
    datade = f'01%2F{mes_anterior}%2F{ano_de_datade}'
    ultimo_dia_mes_atual = ultimo_dia_mes(ano_atual, int(mes_atual))
    dataate = f'{ultimo_dia_mes_atual}%2F{mes_atual}%2F{ano_atual}'
    print(f'Data de inicio da Raspagem: {datade.replace("%2F", "/")}')
    print(f'Data final da Raspagem: {dataate.replace("%2F", "/")}')
    return datade, dataate

def processar_pagina(pg, mes_atual, ano_atual, datade, dataate) -> int:
    """
    Função para realizar o processo de raspagem e pegar o número da última página.
    """
    soup = raspar_dados(pg, mes_atual, ano_atual, datade, dataate)
    last_page = pegar_ultima_pagina(soup)
    return last_page

def pega_ultima_pagina() -> int:
    # Configurações iniciais
    pg = '1'
    ano_atual = datetime.now().year

    # Obtendo o mês atual e o mês anterior
    mes_atual, mes_anterior = obter_mes_atual_e_anterior()

    # Definindo o intervalo de datas
    datade, dataate = obter_intervalo_datas(mes_atual, mes_anterior, ano_atual)

    # Processando a página e obtendo o número da última página
    ultima_pagina = processar_pagina(pg, mes_atual, ano_atual, datade, dataate)

    return mes_atual, ano_atual, datade, dataate, ultima_pagina

def adicionar_linhas(df_base, df_novo):
    """
    Função para concatenar as linhas de df_novo ao df_base.
    """
    return pd.concat([df_base, df_novo], ignore_index=True)


def tempo_espera(tempo_inicial:int, tempo_final:int) -> None:
    """
    Função para aguardar um tempo aleatório em segundos.
    """
    tempo_espera = random.randint(tempo_inicial, tempo_final)
    print('Esperando por', tempo_espera, 'segundos...')
    time.sleep(tempo_espera)

def pega_df_geral(manual: bool, config:str) -> pd.DataFrame:
    df_geral = pd.DataFrame()
    pagina_inicial = 1
    if manual and len(config) > 0:
        lista = config.split(';')
        pagina_inicial = int(lista[0])
        mes_atual = lista[1]
        ano_atual = int(lista[2])
        datade = lista[3]
        dataate = lista[4]
        ultima_pagina = processar_pagina(pagina_inicial, mes_atual, ano_atual, datade, dataate)
    else:
        mes_atual, ano_atual, datade, dataate, ultima_pagina = pega_ultima_pagina()
    print('=|'*50)
    print(f'Página {pagina_inicial} de {ultima_pagina} - {mes_atual}/{ano_atual} - {datade} - {dataate}')
    print('=|'*50)
    for pg in range(pagina_inicial, ultima_pagina + 1):
    #for pg in range(1, 3):
        print(f'Processando a página {pg} de {ultima_pagina}...')
        tempo_espera(10,15)
        soup = raspar_dados(pg, mes_atual, ano_atual, datade, dataate)
        column_names = pegar_nome_das_colunas(soup)
        rows = pegar_dados(soup )
        df = pd.DataFrame(rows, columns=column_names)
        print('Shape geral',df_geral.shape)
        print('Shape df',df.shape)
        #display(df.head())
        df_geral = adicionar_linhas(df_geral, df)
        print('Adicionou linhas')
        print('Shape geral',df_geral.shape)
        print('Shape df',df.shape)
        
        print('====================')
    print('Shape geral',df_geral.shape)
    #display(df_geral.head())
    return df_geral

def retornar_df_completo(df: pd.DataFrame) -> pd.DataFrame:
    # Inicializar o DataFrame vazio para armazenar os dados
    df_completo = pd.DataFrame()
    cont = 1

    # Iterar pelas linhas do DataFrame
    for idx, linha in df.iterrows():
        print('='*50)
        print(idx)
        print(f'Preparando para pegar detalhes da linha: {cont}, total de linhas: {len(df)}')
        tempo_espera(10, 15)  # Aguarda um tempo aleatório entre 10 e 15 segundos
        
        # A última coluna deve conter a URL
        url = linha.iloc[-1]  # Usar iloc para acessar a posição da coluna corretamente
        print(f"Processando URL: {url}")
        
        # Chama a função pegar_detalhes para obter os detalhes da URL
        df_temp = pegar_detalhes(url)
        
        # Verifica se df_temp é um DataFrame e possui dados antes de concatenar
        if df_temp is not None and not df_temp.empty:
            # Converte a linha original em um DataFrame (1 linha, várias colunas)
            df_linha_original = pd.DataFrame([linha])
            
            # Concatenar horizontalmente (lado a lado)
            df_expandido = pd.concat([df_linha_original.reset_index(drop=True), df_temp.reset_index(drop=True)], axis=1)
            
            # Adicionar a linha combinada ao df_completo
            df_completo = pd.concat([df_completo, df_expandido], ignore_index=True)
            print(df_completo.head())
        
        cont += 1

    # Exibe o novo DataFrame com as linhas combinadas
    print(df_completo.head())
    print(f"Dimensões do df_completo: {df_completo.shape}")
    return df_completo

def testa_conexao_mongodb(tuple: (str, str)):
    # Carregar automaticamente o arquivo .env no mesmo diretório ou em diretórios pais
    load_dotenv()

    # pega db_password do ambiente
    db_password = os.environ.get('db_password')

    uri = f"mongodb+srv://renoaldo_teste:{db_password}@cluster0.zmdkz1p.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    # Create a new client and connect to the server
    client = MongoClient(uri)

    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        db = client['CMP']
        collection = db['EMPENHOS_DETALHADOS_STAGE']
        return collection
    except Exception as e:
        print(e)
        raise SystemExit("Unable to connect to the database. Please check your URI.")
    
def inserir_df_no_mongodb_sem_duplicados(df, collection, campos_unicos):
    """
    Insere os documentos de um DataFrame no MongoDB, mas somente se eles não existirem.
    
    Args:
        df: O DataFrame contendo os documentos a serem inseridos.
        collection: A coleção MongoDB onde os documentos serão inseridos.
        campos_unicos: Lista de campos que formam a chave única (exemplo: ['Número', 'Data', 'Atualizado']).
    """
    # Converte o DataFrame em uma lista de dicionários (cada linha é um documento)
    documentos = df.to_dict(orient='records')
    
    documentos_inseridos = 0
    
    for documento in documentos:
        # Criar o filtro para a chave composta
        filtro = {campo: documento[campo] for campo in campos_unicos}
        
        # Verificar se o documento com a chave composta já existe
        if collection.count_documents(filtro) == 0:
            # Se não existir, insere o documento
            collection.insert_one(documento)
            documentos_inseridos += 1
        else:
            print(f"Documento com {filtro} já existe.")
    
    print(f"{documentos_inseridos} novos documentos inseridos.")
    



    
if __name__ == '__main__':
    mongodb_collection = testa_conexao_mongodb(('CMP', 'EMPENHOS_DETALHADOS_STAGE'))
    #config = '1;12;2021;01%2F01%2F2021;31%2F12%2F2021'
    #config = '1;12;2022;01%2F01%2F2022;31%2F12%2F2022'
    #config = '1;12;2023;01%2F01%2F2023;31%2F12%2F2023'
    #config = '1;12;2024;01%2F04%2F2024;31%2F07%2F2024'
    #df_geral = pega_df_geral(manual=True, config=config)
    
    df_geral = pega_df_geral(manual=False, config='')
    #df_geral = df_geral.head(3)
    df_completo = retornar_df_completo(df_geral)

    # Inserir no MongoDB, evitando duplicação com base nos campos 'Número', 'Data', 'Atualizado'
    chave_composta = ['Número', 'Data', 'Atualizado','Empenhado','Liquidado','Pago']
    inserir_df_no_mongodb_sem_duplicados(df_completo, mongodb_collection, chave_composta)
    
    
