import os
from dotenv import load_dotenv
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
import requests
import unicodedata

# Função para normalizar IDs para ASCII
def normalize_id(text):
    normalized = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    return normalized.replace(" ", "_")

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar embeddings e LLM
embedding_model = OpenAIEmbeddings()
llm = OpenAI(temperature=0)

# Configurar Pinecone
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_CLOUD = os.getenv("PINECONE_CLOUD")
PINECONE_REGION = os.getenv("PINECONE_REGION")
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "subelementos"

# Conectar ou criar o índice
try:
    if index_name not in [index_info["name"] for index_info in pc.list_indexes()]:
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud=PINECONE_CLOUD, region=PINECONE_REGION)
        )
        print(f"Índice '{index_name}' criado com sucesso.")
    else:
        print(f"Índice '{index_name}' já existe.")

    index = pc.Index(index_name)
    print(f"Conectado ao índice '{index_name}'.")
except Exception as e:
    print(f"Ocorreu um erro ao conectar ao índice: {e}")
    exit()

# Criar vector store
vector_store = PineconeVectorStore(index=index, embedding=embedding_model)

# Obter dados da API
url = 'https://api.controlgov.org/subelementos/empenhado-sum/'
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Falha ao obter dados da API: {response.status_code}")
data = response.json()

# Preparar textos e IDs para upsert
texts_to_upsert = []
ids_to_upsert = []

for item in data.get('subelementos', []):
    subelemento = item.get('subelemento', 'Desconhecido')
    total = item.get('total_empenhado', 'Não disponível')
    text = f"O total empenhado para o subelemento '{subelemento}' é {total}."

    # Normalizar ID para compatibilidade com ASCII
    doc_id = f"subelemento-{normalize_id(subelemento)}"
    texts_to_upsert.append(text)
    ids_to_upsert.append(doc_id)

# Adicionar ou atualizar vetores
try:
    print("Atualizando textos no Pinecone...")
    vector_store.add_texts(texts=texts_to_upsert, ids=ids_to_upsert)
    print("Textos atualizados com sucesso.")
except Exception as e:
    print(f"Ocorreu um erro ao atualizar os textos: {e}")

# # Realizar consulta e gerar resposta
# query = "Qual é o total empenhado para o subelemento 'Frete'?"

# try:
#     retrieved_docs = vector_store.similarity_search(query)
#     print("Documentos recuperados com sucesso.")

#     for doc in retrieved_docs:
#         print(f"Documento: {doc.page_content}")

#     context = "\n".join([doc.page_content for doc in retrieved_docs])
#     prompt = f"Com base nestes documentos:\n{context}\n\nPergunta: {query}\nResposta:"
#     response = llm.invoke(prompt)

#     print("Resposta gerada pelo LLM:")
#     print(response)

# except Exception as e:
#     print(f"Ocorreu um erro na busca de similaridade: {e}")
# INSERE INFORMAÇÕES DE VALORES EMPENHADOS CREDORES NO PINECONE E GERA RESPOSTA COM O LLM

# Obter dados da API
url = 'https://api.controlgov.org/credores/empenhado-sum/'
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Falha ao obter dados da API: {response.status_code}")
data = response.json()

# Preparar textos e IDs para upsert
texts_to_upsert = []
ids_to_upsert = []

for item in data.get('credores', []):
    credor = item.get('credor', 'Desconhecido')
    total = item.get('total_empenhado', 'Não disponível')
    text = f"O total empenhado para o credor '{credor}' foi {total}."

    # Normalizar ID para compatibilidade com ASCII
    doc_id = f"credor-{normalize_id(credor)}"
    texts_to_upsert.append(text)
    ids_to_upsert.append(doc_id)

# Adicionar ou atualizar vetores
try:
    print("Atualizando textos no Pinecone...")
    vector_store.add_texts(texts=texts_to_upsert, ids=ids_to_upsert)
    print("Textos atualizados com sucesso.")
except Exception as e:
    print(f"Ocorreu um erro ao atualizar os textos: {e}")

# # Realizar consulta e gerar resposta
# query = "Qual é o total pago ao credor 'Renoaldo'?"

# try:
#     retrieved_docs = vector_store.similarity_search(query)
#     print("Documentos recuperados com sucesso.")

#     for doc in retrieved_docs:
#         print(f"Documento: {doc.page_content}")

#     context = "\n".join([doc.page_content for doc in retrieved_docs])
#     prompt = f"Com base nestes documentos:\n{context}\n\nPergunta: {query}\nResposta:"
#     response = llm.invoke(prompt)

#     print("Resposta gerada pelo LLM:")
#     print(response)

# except Exception as e:
#     print(f"Ocorreu um erro na busca de similaridade: {e}")
# INSERE INFORMAÇÕES DE CNPJ E CPF DOS CREDORES NO PINECONE E GERA RESPOSTA COM O LLM

# Obter dados da API
url = 'https://api.controlgov.org/credores/'
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Falha ao obter dados da API: {response.status_code}")
data = response.json()

# Preparar textos e IDs para upsert
texts_to_upsert = []
ids_to_upsert = []

for item in data.get('credores', []):
    
    c = item.split(" - ")
    Identificacao = c[0]
    Nome = c[1]
    if '***' in Identificacao:
        tipo_identificacao = 'CPF'
        text = f"O CPF do credor {Nome} é {Identificacao}."
    else:
        tipo_identificacao = 'CNPJ'
        text = f"O CNPJ do credor {Nome} é {Identificacao}."
    
        
    # Normalizar ID para compatibilidade com ASCII
    doc_id = f"{tipo_identificacao}_CREDOR-{normalize_id(Identificacao)}"
    texts_to_upsert.append(text)
    ids_to_upsert.append(doc_id)

# Adicionar ou atualizar vetores
try:
    print("Atualizando textos no Pinecone...")
    vector_store.add_texts(texts=texts_to_upsert, ids=ids_to_upsert)
    print("Textos atualizados com sucesso.")
except Exception as e:
    print(f"Ocorreu um erro ao atualizar os textos: {e}")

# Realizar consulta e gerar resposta
# query = "Qual é o cpf do credor 'Renoaldo'?"

# try:
#     retrieved_docs = vector_store.similarity_search(query)
#     print("Documentos recuperados com sucesso.")

#     for doc in retrieved_docs:
#         print(f"Documento: {doc.page_content}")

#     context = "\n".join([doc.page_content for doc in retrieved_docs])
#     prompt = f"Com base nestes documentos:\n{context}\n\nPergunta: {query}\nResposta:"
#     response = llm.invoke(prompt)

#     print("Resposta gerada pelo LLM:")
#     print(response)

# except Exception as e:
#     print(f"Ocorreu um erro na busca de similaridade: {e}")
