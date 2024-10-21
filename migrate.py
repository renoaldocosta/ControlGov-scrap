import pymongo
from pymongo import MongoClient, ReplaceOne
from datetime import datetime
import re
import os
from dotenv import load_dotenv

from pydantic import BaseModel, ValidationError, Field
from typing import List

# Definição dos modelos Pydantic com aliases para campos com nomes especiais
class Item(BaseModel):
    descricao: str
    tipo: str
    quantidade: float  # Alterado de int para float
    valor_unitario: float
    valor_total: float

class EmpenhoDetalhado(BaseModel):
    original_id: str = Field(..., alias="original_id")  # Campo para armazenar o antigo _id como string
    numero: str = Field(..., alias="Número")
    data: datetime = Field(..., alias="Data")
    credor: str = Field(..., alias="Credor")
    alteracao: float = Field(..., alias="Alteração")
    empenhado: float = Field(..., alias="Empenhado")
    liquidado: float = Field(..., alias="Liquidado")
    pago: float = Field(..., alias="Pago")
    atualizado: datetime = Field(..., alias="Atualizado")
    link_detalhes: str = Field(..., alias="link_Detalhes")
    poder: str = Field(..., alias="Poder")
    funcao: str = Field(..., alias="Função")
    elemento_de_despesa: str = Field(..., alias="Elemento de Despesa")
    unid_administradora: str = Field(..., alias="Unid. Administradora")
    subfuncao: str = Field(..., alias="Subfunção")
    subelemento: str = Field(..., alias="Subelemento")
    unid_orcamentaria: str = Field(..., alias="Unid. Orçamentária")
    fonte_de_recurso: str = Field(..., alias="Fonte de recurso")
    projeto_atividade: str = Field(..., alias="Projeto/Atividade")
    categorias_de_base_legal: str = Field(..., alias="Categorias de base legal")
    historico: str = Field(..., alias="Histórico")
    itens: List[Item] = Field(..., alias="Item(ns)")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

# Função para converter valores monetários de string para float
def parse_monetary(value: str) -> float:
    if not value:
        return 0.0
    # Remove "R$ ", espaços e pontos (separadores de milhares), substitui vírgula por ponto
    value = re.sub(r'[R$\s]', '', value)
    value = value.replace('.', '').replace(',', '.')
    try:
        return float(value)
    except ValueError:
        # Log ou tratamento adicional pode ser adicionado aqui
        return 0.0

# Função para converter datas de string para datetime
def parse_date(value: str) -> datetime:
    try:
        return datetime.strptime(value, "%d/%m/%Y")
    except ValueError:
        # Log ou tratamento adicional pode ser adicionado aqui
        return datetime(1970, 1, 1)  # Data padrão em caso de erro

def migrate_data():
    # Carrega variáveis de ambiente
    load_dotenv()

    # Conexão com o MongoDB
    mongodb_url = os.getenv("MONGODB_URL")
    if not mongodb_url:
        print("MONGODB_URL não está definido nas variáveis de ambiente.")
        return

    client = MongoClient(mongodb_url)
    db = client["CMP"]
    stage_collection = db["EMPENHOS_DETALHADOS_STAGE"]
    target_collection = db["EMPENHOS_DETALHADOS"]

    # Contador para monitoramento
    count = 0
    batch_size = 1000  # Tamanho do lote para inserção

    # Preparar uma lista para operações de upsert
    operations = []

    try:
        cursor = stage_collection.find()
        for doc in cursor:
            try:
                # Converter campos monetários
                empenhado = parse_monetary(doc.get('Empenhado', 'R$ 0,00'))
                liquidado = parse_monetary(doc.get('Liquidado', 'R$ 0,00'))
                pago = parse_monetary(doc.get('Pago', 'R$ 0,00'))
                alteracao = parse_monetary(doc.get('Alteração', 'R$ 0,00'))

                # Converter datas
                data = parse_date(doc.get('Data', '01/01/1970'))
                atualizado = parse_date(doc.get('Atualizado', '01/01/1970'))

                # Estruturar os itens
                itens = doc.get('Item(ns)', [])
                headers = itens[0] if itens else []
                detalhes_itens = itens[1] if len(itens) > 1 else []

                itens_convertidos = []
                for item in detalhes_itens:
                    if len(item) == 5:
                        descricao, tipo, quantidade, valor_unitario, valor_total = item
                        try:
                            item_convertido = Item(
                                descricao=descricao,
                                tipo=tipo,
                                quantidade=float(quantidade),
                                valor_unitario=parse_monetary(valor_unitario),
                                valor_total=parse_monetary(valor_total)
                            )
                            itens_convertidos.append(item_convertido.dict(by_alias=True))
                        except (ValueError, ValidationError) as e:
                            print(f"Erro ao converter item no documento _id {doc.get('_id')}: {e}")
                            continue  # Pular itens com erros

                # Construir o novo documento com aliases e incluir 'original_id' como string
                novo_doc = {
                    "original_id": str(doc.get('_id')),  # Inclui o antigo _id como 'original_id' (string)
                    "Número": doc.get('Número', ''),
                    "Data": data,
                    "Credor": doc.get('Credor', ''),
                    "Alteração": alteracao,
                    "Empenhado": empenhado,
                    "Liquidado": liquidado,
                    "Pago": pago,
                    "Atualizado": atualizado,
                    "link_Detalhes": doc.get('link_Detalhes', ''),
                    "Poder": doc.get('Poder', ''),
                    "Função": doc.get('Função', ''),
                    "Elemento de Despesa": doc.get('Elemento de Despesa', ''),
                    "Unid. Administradora": doc.get('Unid. Administradora', ''),
                    "Subfunção": doc.get('Subfunção', ''),
                    "Subelemento": doc.get('Subelemento', ''),
                    "Unid. Orçamentária": doc.get('Unid. Orçamentária', ''),
                    "Fonte de recurso": doc.get('Fonte de recurso', ''),
                    "Projeto/Atividade": doc.get('Projeto/Atividade', ''),
                    "Categorias de base legal": doc.get('Categorias de base legal', ''),
                    "Histórico": doc.get('Histórico', ''),
                    "Item(ns)": itens_convertidos
                }

                # Validar o documento com Pydantic
                try:
                    empenho_detalhado = EmpenhoDetalhado(**novo_doc)
                    valid_doc = empenho_detalhado.dict(by_alias=True)
                except ValidationError as ve:
                    print(f"Erro de validação no documento original_id {novo_doc['original_id']}: {ve}")
                    continue  # Pular documentos com erros de validação

                # Criar operação de ReplaceOne com upsert=True baseado no campo "original_id"
                operations.append(
                    ReplaceOne(
                        {"original_id": valid_doc["original_id"]},  # Filtro baseado no campo 'original_id'
                        valid_doc,  # Documento a ser inserido ou substituído
                        upsert=True  # Se não existir, insere; se existir, substitui
                    )
                )
                count += 1

                # Executar operações em lote quando o tamanho do lote for alcançado
                if len(operations) >= batch_size:
                    result = target_collection.bulk_write(operations, ordered=False)
                    print(f"{count} documentos processados. Inseridos: {result.upserted_count}, Atualizados: {result.modified_count}")
                    operations = []

            except Exception as e:
                print(f"Erro ao migrar documento com _id {doc.get('_id')}: {e}")

        # Executar quaisquer operações restantes
        if operations:
            result = target_collection.bulk_write(operations, ordered=False)
            print(f"{count} documentos processados. Inseridos: {result.upserted_count}, Atualizados: {result.modified_count}")

        print(f"Total de documentos migrados: {count}")

    except Exception as e:
        print(f"Erro durante a migração: {e}")

    finally:
        client.close()

# Executar a migração
if __name__ == "__main__":
    migrate_data()
