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


def save_realtime_metrics(db, metric_doc):
    # simpen ringkasan metrik per micro-batch ke koleksi realtime_metrics
    doc = dict(metric_doc)
    doc.setdefault("recorded_at", datetime.now(timezone.utc).isoformat())
    db.realtime_metrics.insert_one(doc)


def save_fraud_alerts(db, alerts):
    # simpen daftar alert fraud kalo ada yg ketangkep di batch sekarang
    if not alerts:
        return
    now_iso = datetime.now(timezone.utc).isoformat()
    docs = []
    for item in alerts:
        d = dict(item)
        d.setdefault("detected_at", now_iso)
        docs.append(d)
    db.fraud_alerts.insert_many(docs)


def save_prescriptive_actions(db, actions):
    # simpen rekomendasi aksi preskriptif biar langsung muncul di panel dashboard
    if not actions:
        return
    now_iso = datetime.now(timezone.utc).isoformat()
    docs = []
    for item in actions:
        d = dict(item)
        d.setdefault("created_at", now_iso)
        docs.append(d)
    db.prescriptive_actions.insert_many(docs)


def save_benchmark_result(db, result_doc):
    # simpen hasil perbandingan waktu eksekusi spark sebelum vs sesudah optimasi
    doc = dict(result_doc)
    doc.setdefault("run_at", datetime.now(timezone.utc).isoformat())
    db.benchmark_results.insert_one(doc)


def fetch_recent_metrics(db, limit=60):
    rows = list(db.realtime_metrics.find({}, {"_id": 0}).sort("recorded_at", DESCENDING).limit(limit))
    rows.reverse()
    return rows


def fetch_recent_alerts(db, limit=100, fraud_type=None, category=None):
    query = {}
    if fraud_type and fraud_type != "Semua":
        query["fraud_type"] = fraud_type
    if category and category != "Semua":
        query["category"] = category
    return list(db.fraud_alerts.find(query, {"_id": 0}).sort("detected_at", DESCENDING).limit(limit))


def fetch_prescriptive_actions(db, limit=40, priority=None):
    query = {}
    if priority and priority != "Semua":
        query["priority"] = priority
    return list(db.prescriptive_actions.find(query, {"_id": 0}).sort("created_at", DESCENDING).limit(limit))


def fetch_latest_benchmark(db):
    return db.benchmark_results.find_one({}, {"_id": 0}, sort=[("run_at", DESCENDING)])
