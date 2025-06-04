import os
import json
import pandas as pd
from pathlib import Path
from pymongo import MongoClient
from dotenv import load_dotenv

import config

load_dotenv()

ID_CACHE_PATH = config.STORAGE_PATH / "id_cache.json"    

def fetch_data_from_mongo(): 
    user = os.getenv("MONGODB_USER")
    pw = os.getenv("MONGODB_PASS")
    db_name = os.getenv("MONGODB_DB")
    col_name = os.getenv("MONGODB_COLLECTION")
    
    uri = f"mongodb+srv://{user}:{pw}@ransomcrawl.mmnwun3.mongodb.net/"
    client = MongoClient(uri, serverSelectionTimeoutMS = 5000)   
    return list(client[db_name][col_name].find())

def load_cached_ids():
    if ID_CACHE_PATH.exists():
        with open(ID_CACHE_PATH, "r") as f:
            return set(json.load(f)["_ids"])
    return set()

def save_cached_ids(ids):
    with open(ID_CACHE_PATH, "w") as f:
        json.dump({"_ids": list(ids)}, f, indent= 2)
    
def load_combined_json() -> list:
    combined_path = config.COMBINED_PATH
    mongo_data = fetch_data_from_mongo()
    
    current_ids = {str(doc["_id"]) for doc in mongo_data}
    cached_ids = load_cached_ids()
    
    if current_ids == cached_ids:
        print("❌ No new ids detected. Using cached combined.json")
        with open(combined_path, "r", encoding = "utf-8") as f:
            return json.load(f)
    
    else:
        new_ids = current_ids - cached_ids
        print(f"{len(new_ids)} new document(s) detected. Updating combined.json...")
        
        with open(combined_path, "w", encoding="utf-8") as f:
            json.dump(mongo_data, f, ensure_ascii = False, indent= 2)
        print(f"✅ Combined JSON file updated at: {combined_path}")

    save_cached_ids(current_ids)
    return mongo_data