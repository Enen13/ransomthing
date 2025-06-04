import json
import pandas as pd

from pymongo import MongoClient

from dotenv import load_dotenv
from urllib.parse import quote_plus
import os, pathlib



loaded = load_dotenv(dotenv_path=pathlib.Path(r"P1/analyzer/.env"))
# Uncomment below to check connection with MongoDB (Input path to .env)
# print("🔁 .env loaded:", loaded)

# for key in ["MONGODB_USER", "MONGODB_PASS", "MONGODB_DB"]:
#     value = os.getenv(key)
#     print(f"{key} = {value!r}")


user     = quote_plus(os.getenv("MONGODB_USER"))
pw       = quote_plus(os.getenv("MONGODB_PASS"))
db       = os.getenv("MONGODB_DB")

uri = f"mongodb+srv://{user}:{pw}@ransomcrawl.mmnwun3.mongodb.net/"
client = MongoClient(uri, serverSelectionTimeoutMS=5000)   # 5 s fail-fast

db = client["ransomware_db"]
collection_names = db.list_collection_names()

for name in collection_names:
    print(f"📦 Loading collection: {name}")
    col = db[name]
    docs = list(col.find({}, {"_id": 0}))
    df = pd.json_normalize(docs, sep="_") if docs else pd.DataFrame()
    print(f"🧾 {name} shape:", df.shape)
    print(df)

# # 1 ── pull the documents ----------------------------------------------------
# cursor = col.find({}, {"_id": 0})          # filter={}, projection: drop _id
# docs   = list(cursor)                      # materialise once

# # 2 ── build the DataFrame ---------------------------------------------------
# df = (pd.json_normalize(docs, sep="_")     # flattens dotted keys
#         if docs and isinstance(docs[0], dict) and any("." in k for k in docs[0])
#         else pd.DataFrame(docs))

# print(df)