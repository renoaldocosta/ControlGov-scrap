import pymongo
from pymongo import MongoClient
import os
from dotenv import load_dotenv

def check_duplicates():
    load_dotenv()
    mongodb_url = os.getenv("MONGODB_URL")
    if not mongodb_url:
        print("MONGODB_URL não está definido nas variáveis de ambiente.")
        return

    client = MongoClient(mongodb_url)
    db = client["CMP"]
    target_collection = db["EMPENHOS_DETALHADOS"]

    pipeline = [
        {"$group": {"_id": "$original_id", "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]
    duplicates = list(target_collection.aggregate(pipeline))
    if duplicates:
        print("Duplicações encontradas:")
        for dup in duplicates:
            print(dup)
    else:
        print("Nenhuma duplicação encontrada.")

    client.close()

if __name__ == "__main__":
    check_duplicates()
