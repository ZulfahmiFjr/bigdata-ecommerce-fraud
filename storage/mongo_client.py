import os
from datetime import datetime, timezone
from pymongo import MongoClient, DESCENDING


def get_mongo_db(uri=None, db_name=None):
    # ambil koneksi database mongodb dari env biar gampang diatur di docker
    mongo_uri = uri or os.getenv("MONGO_URI", "mongodb://mongodb:27017")
    target_db = db_name or os.getenv("MONGO_DB", "ecommerce_bigdata")
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    return client[target_db]


def ensure_indexes(db):
    # pasang index ringan di timestamp biar query dashboard tetep cepet
    db.realtime_metrics.create_index([("recorded_at", DESCENDING)])
    db.fraud_alerts.create_index([("detected_at", DESCENDING)])
    db.fraud_alerts.create_index([("fraud_type", 1)])
    db.prescriptive_actions.create_index([("created_at", DESCENDING)])
    db.benchmark_results.create_index([("run_at", DESCENDING)])
