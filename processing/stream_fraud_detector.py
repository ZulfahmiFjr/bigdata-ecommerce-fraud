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
