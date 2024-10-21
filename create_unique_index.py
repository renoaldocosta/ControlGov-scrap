import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

def create_unique_index():
    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL")
    if not mongodb_url:
        print("MONGODB_URL não está definido nas variáveis de ambiente.")
        return

    client = MongoClient(mongodb_url)
    db = client["CMP"]
    target_collection = db["EMPENHOS_DETALHADOS"]

    # Criar índice único no campo 'original_id'
    try:
        target_collection.create_index("original_id", unique=True)
        print("Índice único criado no campo 'original_id'.")
    except pymongo.errors.DuplicateKeyError as e:
        print(f"Erro ao criar índice único: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    create_unique_index()
