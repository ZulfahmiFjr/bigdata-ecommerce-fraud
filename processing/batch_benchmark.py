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


def run_analytics_queries(df):
    # jalanin 3 query analitik khas e-commerce buat ngukur waktu komputasi
    q1 = (
        df.groupBy("merchant_id")
        .agg(F.count("*").alias("total_tx"), F.sum("amount_idr").alias("gmv"), F.sum("is_high_value").alias("fraud_tx"))
        .orderBy(F.desc("gmv"))
        .limit(10)
        .collect()
    )
    q2 = (
        df.groupBy("device", "event_type")
        .agg(F.count("*").alias("cnt"), F.avg("amount_idr").alias("avg_amt"))
        .collect()
    )
    q3 = (
        df.filter(F.col("is_high_value") == 1)
        .groupBy("user_id")
        .agg(F.count("*").alias("high_val_count"), F.sum("amount_idr").alias("total_amt"))
        .orderBy(F.desc("total_amt"))
        .limit(10)
        .collect()
    )
    return len(q1), len(q2), len(q3)


def main():
    num_rows = int(os.getenv("BENCHMARK_ROWS", "1000000"))
    base_dir = os.getenv("BENCHMARK_DIR", "/app/data/parquet/benchmark_tmp")
    evidence_file = os.getenv("BENCHMARK_FILE", "/app/docs/evidence/benchmark_results.json")

    raw_json_dir = os.path.join(base_dir, "raw_json_unpartitioned")
    opt_parquet_dir = os.path.join(base_dir, "opt_parquet_partitioned")

    # bersihin sisa folder benchmark lama kalo ada biar ukuran disk akurat
    if os.path.exists(base_dir):
        shutil.rmtree(base_dir)
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.dirname(evidence_file), exist_ok=True)

    spark = (
        SparkSession.builder
        .appName("SparkOptimizationBenchmark")
        .master("local[2]")
        .config("spark.sql.parquet.compression.codec", "snappy")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    print(f"[benchmark] menyiapkan dataset historis sebanyak {num_rows:,} baris")
    source_df = build_synthetic_dataset(spark, num_rows).persist(StorageLevel.MEMORY_AND_DISK)
    source_df.count()

    # simpan versi mentah (JSON tanpa partisi) sama versi optimasi (parquet snappy terpartisi)
    t_w1 = time.perf_counter()
    source_df.write.mode("overwrite").json(raw_json_dir)
    write_raw_sec = round(time.perf_counter() - t_w1, 3)

    t_w2 = time.perf_counter()
    source_df.write.mode("overwrite").partitionBy("event_date", "category").parquet(opt_parquet_dir)
    write_opt_sec = round(time.perf_counter() - t_w2, 3)
    source_df.unpersist()

    raw_size_mb = dir_size_mb(raw_json_dir)
    opt_size_mb = dir_size_mb(opt_parquet_dir)
    storage_saved_pct = round(((raw_size_mb - opt_size_mb) / raw_size_mb) * 100.0, 2) if raw_size_mb > 0 else 0.0
    print(f"[benchmark] ukuran disk -> raw JSON: {raw_size_mb} MB | parquet terpartisi: {opt_size_mb} MB (hemat {storage_saved_pct}%)")

    target_date = "2026-11-27"
    target_cat = "elektronik"

    # skenario 1 sebelum optimasi: baca JSON tanpa partisi, shuffle partitions default 200, tanpa cache
    spark.conf.set("spark.sql.shuffle.partitions", "200")
    t_b0 = time.perf_counter()
    base_df = (
        spark.read.json(raw_json_dir)
        .filter((F.col("event_date") == target_date) & (F.col("category") == target_cat))
    )
    run_analytics_queries(base_df)
    baseline_sec = round(time.perf_counter() - t_b0, 3)
    print(f"[benchmark] SEBELUM optimasi (raw JSON, shuffle=200, no cache): {baseline_sec} detik")

    # skenario 2 sesudah optimasi: parquet terpartisi (partition pruning), shuffle partitions 4, persist
    spark.conf.set("spark.sql.shuffle.partitions", "4")
    t_o0 = time.perf_counter()
    opt_df = (
        spark.read.parquet(opt_parquet_dir)
        .filter((F.col("event_date") == target_date) & (F.col("category") == target_cat))
        .persist(StorageLevel.MEMORY_AND_DISK)
    )
    run_analytics_queries(opt_df)
    opt_df.unpersist()
    optimized_sec = round(time.perf_counter() - t_o0, 3)
    print(f"[benchmark] SESUDAH optimasi (parquet partisi, shuffle=4, cache): {optimized_sec} detik")

    speedup = round(baseline_sec / optimized_sec, 2) if optimized_sec > 0 else 0.0
    time_saved_pct = round(((baseline_sec - optimized_sec) / baseline_sec) * 100.0, 2) if baseline_sec > 0 else 0.0

    result = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "dataset_rows": num_rows,
        "filter_query": f"event_date='{target_date}' AND category='{target_cat}' (3 agregasi analitik)",
        "baseline": {
            "label": "Sebelum Optimasi (JSON, shuffle=200, tanpa cache)",
            "query_time_sec": baseline_sec,
            "write_time_sec": write_raw_sec,
            "storage_mb": raw_size_mb,
            "shuffle_partitions": 200,
            "partitioned": False,
            "cached": False,
        },
        "optimized": {
            "label": "Sesudah Optimasi (Parquet Partisi, shuffle=4, cache)",
            "query_time_sec": optimized_sec,
            "write_time_sec": write_opt_sec,
            "storage_mb": opt_size_mb,
            "shuffle_partitions": 4,
            "partitioned": True,
            "cached": True,
        },
        "speedup_x": speedup,
        "time_saved_pct": time_saved_pct,
        "storage_saved_pct": storage_saved_pct,
    }

    with open(evidence_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    try:
        db = get_mongo_db()
        ensure_indexes(db)
        save_benchmark_result(db, result)
        print("[benchmark] hasil benchmark berhasil disimpan ke mongodb dan JSON evidence")
    except Exception as err:
        print(f"[benchmark] peringatan gagal simpen ke mongodb: {err}")

    # bersihin folder temporary benchmark raw JSON biar disk VPS tetep hemat
    shutil.rmtree(base_dir, ignore_errors=True)
    spark.stop()
    print(f"[benchmark] SELESAI -> percepatan {speedup}x ({time_saved_pct}% lebih cepat), hemat disk {storage_saved_pct}%")


if __name__ == "__main__":
    main()
