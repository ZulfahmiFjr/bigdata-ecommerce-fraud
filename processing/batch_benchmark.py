import json
import os
import shutil
import time
from datetime import datetime, timezone
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark import StorageLevel
from storage.mongo_client import get_mongo_db, ensure_indexes, save_benchmark_result


def dir_size_mb(path):
    # hitung total ukuran folder di disk dlam satuan megabyte
    total = 0
    for root, _, files in os.walk(path):
        for fname in files:
            total += os.path.getsize(os.path.join(root, fname))
    return round(total / (1024 * 1024), 2)


def build_synthetic_dataset(spark, num_rows):
    # bikin dataset historis skala 1 juta baris langsung di spark biar cepet dan hemat RAM
    categories = F.array(
        F.lit("elektronik"),
        F.lit("fashion"),
        F.lit("gadget"),
        F.lit("rumah_tangga"),
        F.lit("kecantikan"),
    )
    dates = F.array(
        F.lit("2026-11-21"),
        F.lit("2026-11-22"),
        F.lit("2026-11-23"),
        F.lit("2026-11-24"),
        F.lit("2026-11-25"),
        F.lit("2026-11-26"),
        F.lit("2026-11-27"),
    )
    event_types = F.array(F.lit("view"), F.lit("view"), F.lit("add_to_cart"), F.lit("checkout"), F.lit("review"))

    df = (
        spark.range(0, num_rows, numPartitions=4)
        .withColumn("event_date", F.element_at(dates, (F.col("id") % 7).cast("int") + 1))
        .withColumn("category", F.element_at(categories, (F.col("id") % 5).cast("int") + 1))
        .withColumn("event_type", F.element_at(event_types, (F.col("id") % 5).cast("int") + 1))
        .withColumn("user_id", F.concat(F.lit("usr_"), ((F.col("id") % 50000) + 1000).cast("string")))
        .withColumn("merchant_id", F.concat(F.lit("mrc_"), ((F.col("id") % 200) + 100).cast("string")))
        .withColumn(
            "amount_idr",
            F.when(F.col("event_type") == "checkout", ((F.col("id") % 40) + 1) * F.lit(350000)).otherwise(F.lit(0)),
        )
        .withColumn("is_high_value", F.when(F.col("amount_idr") > 10000000, F.lit(1)).otherwise(F.lit(0)))
        .withColumn("device", F.when((F.col("id") % 2) == 0, F.lit("android_app")).otherwise(F.lit("web_chrome")))
    )
    return df
