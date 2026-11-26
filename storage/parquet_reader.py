import os
import pandas as pd
import pyarrow.dataset as ds


def list_parquet_partitions(base_dir):
    # cari daftar partisi event_date sama category yg udah kebentuk di folder parquet
    dates = set()
    categories = set()
    if not os.path.isdir(base_dir):
        return [], []
    for root, dirs, files in os.walk(base_dir):
        rel = os.path.relpath(root, base_dir)
        if rel == ".":
            continue
        for part in rel.split(os.sep):
            if part.startswith("event_date="):
                dates.add(part.split("=", 1)[1])
            elif part.startswith("category="):
                categories.add(part.split("=", 1)[1])
    return sorted(dates), sorted(categories)


def read_partitioned_parquet(base_dir, event_date=None, category=None, max_rows=500):
    # baca data parquet terpartisi pake pyarrow dataset biar partition pruning jalan dan hemat RAM
    if not os.path.isdir(base_dir):
        return pd.DataFrame(), 0
    has_parquet = False
    for _, _, files in os.walk(base_dir):
        if any(f.endswith(".parquet") for f in files):
            has_parquet = True
            break
    if not has_parquet:
        return pd.DataFrame(), 0

    dataset = ds.dataset(base_dir, format="parquet", partitioning="hive")
    expr = None
    if event_date and event_date != "Semua":
        cond = ds.field("event_date") == event_date
        expr = cond if expr is None else (expr & cond)
    if category and category != "Semua":
        cond = ds.field("category") == category
        expr = cond if expr is None else (expr & cond)

    table = dataset.to_table(filter=expr)
    total_rows = table.num_rows
    if total_rows == 0:
        return pd.DataFrame(), 0
    df = table.slice(0, max_rows).to_pandas()
    return df, total_rows
