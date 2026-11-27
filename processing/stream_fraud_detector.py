import os
import re
from datetime import datetime, timezone
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, LongType, IntegerType
from storage.mongo_client import (
    get_mongo_db,
    ensure_indexes,
    save_realtime_metrics,
    save_fraud_alerts,
    save_prescriptive_actions,
)

FRAUD_REVIEW_PATTERN = re.compile(r"(palsu|penipu|scam|barang kosong|bohong|abal-abal)", re.IGNORECASE)


def build_event_schema():
    # skema eksplisit 3 jenis data (terstruktur, nested JSON clickstream, teks ulasan)
    clickstream_schema = StructType([
        StructField("session_id", StringType(), True),
        StructField("device", StringType(), True),
        StructField("city", StringType(), True),
        StructField("ip_address", StringType(), True),
        StructField("referrer", StringType(), True),
    ])
    return StructType([
        StructField("event_id", StringType(), True),
        StructField("event_time", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("user_id", StringType(), True),
        StructField("merchant_id", StringType(), True),
        StructField("category", StringType(), True),
        StructField("amount_idr", LongType(), True),
        StructField("quantity", IntegerType(), True),
        StructField("payment_method", StringType(), True),
        StructField("clickstream", clickstream_schema, True),
        StructField("review_text", StringType(), True),
        StructField("rating", IntegerType(), True),
    ])


def build_spark_session():
    # mode local[2] sama shuffle partitions 4 biar pas sama VPS 2 vCPU dan hemat RAM
    spark = (
        SparkSession.builder
        .appName("EcommerceFraudRealTimeDetector")
        .master("local[2]")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.sql.parquet.compression.codec", "snappy")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def process_micro_batch(batch_df, batch_id, parquet_dir, mongo_db):
    # skip kalo micro-batch kosong biar ga buang CPU atau bikin file parquet kosong
    if batch_df.rdd.isEmpty():
        return

    enriched = (
        batch_df
        .withColumn("event_date", F.substring(F.col("event_time"), 1, 10))
        .withColumn("device", F.col("clickstream.device"))
        .withColumn("city", F.col("clickstream.city"))
        .withColumn("ip_address", F.col("clickstream.ip_address"))
        .withColumn("referrer", F.col("clickstream.referrer"))
        .drop("clickstream")
    )

    # simpen arsip historis ke parquet terpartisi berdasarkan tanggal sama kategori
    (
        enriched.write
        .mode("append")
        .partitionBy("event_date", "category")
        .parquet(parquet_dir)
    )

    # tarik hasil micro-batch yg ukurannya kecil buat deteksi fraud dan nulis ke mongodb
    rows = enriched.collect()
    total_events = len(rows)
    total_gmv = 0
    checkout_counts_by_user = {}
    category_views = {}
    category_checkouts = {}
    alerts = []
    actions = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for r in rows:
        ev_type = r["event_type"]
        cat = r["category"] or "lainnya"
        amt = int(r["amount_idr"] or 0)
        uid = r["user_id"]
        mid = r["merchant_id"]

        if ev_type == "view":
            category_views[cat] = category_views.get(cat, 0) + 1
        elif ev_type == "checkout":
            total_gmv += amt
            category_checkouts[cat] = category_checkouts.get(cat, 0) + 1
            checkout_counts_by_user[uid] = checkout_counts_by_user.get(uid, []) + [r]

            # pola fraud 2 nominal melonjak di atas 10 juta rupiah
            if amt > 10_000_000:
                alerts.append({
                    "event_id": r["event_id"],
                    "fraud_type": "Nominal Melonjak",
                    "risk_score": 88,
                    "user_id": uid,
                    "merchant_id": mid,
                    "category": cat,
                    "amount_idr": amt,
                    "city": r["city"],
                    "reason": f"Nominal transaksi Rp{amt:,} melebihi batas wajar Rp10.000.000",
                    "detected_at": now_iso,
                })
                actions.append({
                    "action_category": "Verifikasi Transaksi",
                    "priority": "Tinggi",
                    "target": f"Transaksi {r['event_id']} ({uid})",
                    "category": cat,
                    "trigger": f"Nominal Rp{amt:,} pada kategori {cat}",
                    "recommendation": "Tahan transaksi sementara untuk konfirmasi manual sebelum dana diteruskan",
                    "created_at": now_iso,
                })
        elif ev_type == "review":
            review_txt = r["review_text"] or ""
            # pola fraud 3 teks ulasan ngandung kata kunci indikasi penipuan
            if FRAUD_REVIEW_PATTERN.search(review_txt):
                alerts.append({
                    "event_id": r["event_id"],
                    "fraud_type": "Ulasan Penipuan",
                    "risk_score": 82,
                    "user_id": uid,
                    "merchant_id": mid,
                    "category": cat,
                    "amount_idr": 0,
                    "city": r["city"],
                    "reason": f"Ulasan terindikasi penipuan: \"{review_txt[:90]}\"",
                    "detected_at": now_iso,
                })
                actions.append({
                    "action_category": "Audit Merchant",
                    "priority": "Tinggi",
                    "target": f"Merchant {mid}",
                    "category": cat,
                    "trigger": f"Ulasan rating {r['rating']} mengandung kata kunci penipuan",
                    "recommendation": "Audit toko secara manual dan tahan pencairan dana sementara",
                    "created_at": now_iso,
                })

    # pola fraud 1 transaksi kilat >= 5 checkout dari satu akun dlam 1 jendela batch
    for uid, tx_list in checkout_counts_by_user.items():
        if len(tx_list) >= 5:
            sample = tx_list[0]
            total_burst = sum(int(x["amount_idr"] or 0) for x in tx_list)
            alerts.append({
                "event_id": sample["event_id"],
                "fraud_type": "Transaksi Kilat",
                "risk_score": 95,
                "user_id": uid,
                "merchant_id": sample["merchant_id"],
                "category": sample["category"],
                "amount_idr": total_burst,
                "city": sample["city"],
                "reason": f"Akun melakukan {len(tx_list)} transaksi beruntun dalam 1 jendela waktu (indikasi card testing)",
                "detected_at": now_iso,
            })
            actions.append({
                "action_category": "Keamanan Akun",
                "priority": "Kritis",
                "target": f"Akun {uid}",
                "category": sample["category"],
                "trigger": f"{len(tx_list)} transaksi beruntun total Rp{total_burst:,}",
                "recommendation": "Blokir sementara akun terindikasi fraud dan wajibkan verifikasi OTP",
                "created_at": now_iso,
            })

    # sinyal bisnis 4 kategori tinggi klik tapi konversi checkout di bawah 10 persen
    for cat, views in category_views.items():
        checkouts = category_checkouts.get(cat, 0)
        conv_rate = (checkouts / views) * 100.0 if views > 0 else 0.0
        if views >= 5 and conv_rate < 10.0:
            actions.append({
                "action_category": "Optimasi Konversi",
                "priority": "Sedang",
                "target": f"Kategori {cat}",
                "category": cat,
                "trigger": f"{views} klik produk tetapi hanya {checkouts} checkout (konversi {conv_rate:.1f}%)",
                "recommendation": f"Terbitkan voucher diskon 10-15% atau promo gratis ongkir khusus kategori {cat}",
                "created_at": now_iso,
            })

    metric_doc = {
        "batch_id": int(batch_id),
        "recorded_at": now_iso,
        "total_events": total_events,
        "total_checkouts": sum(category_checkouts.values()),
        "total_views": sum(category_views.values()),
        "total_gmv": total_gmv,
        "fraud_count": len(alerts),
        "anomaly_rate_pct": round((len(alerts) / total_events) * 100.0, 2) if total_events else 0.0,
        "category_views": category_views,
        "category_checkouts": category_checkouts,
    }

    save_realtime_metrics(mongo_db, metric_doc)
    save_fraud_alerts(mongo_db, alerts)
    save_prescriptive_actions(mongo_db, actions)
    print(f"[spark-stream] batch={batch_id} events={total_events} gmv=Rp{total_gmv:,} fraud={len(alerts)} actions={len(actions)}")
