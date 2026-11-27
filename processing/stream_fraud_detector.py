import os
import re
from datetime import datetime, timezone
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, LongType, IntegerType

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
    enriched.write.mode("append").partitionBy("event_date", "category").parquet(parquet_dir)

    rows = enriched.collect()
    alerts = []
    for r in rows:
        if r["event_type"] == "checkout" and int(r["amount_idr"] or 0) > 10_000_000:
            alerts.append({"event_id": r["event_id"], "fraud_type": "Nominal Melonjak", "risk_score": 88})
        elif r["event_type"] == "review" and FRAUD_REVIEW_PATTERN.search(r["review_text"] or ""):
            alerts.append({"event_id": r["event_id"], "fraud_type": "Ulasan Penipuan", "risk_score": 82})
    print(f"[spark-stream] batch={batch_id} rows={len(rows)} alerts={len(alerts)}")
